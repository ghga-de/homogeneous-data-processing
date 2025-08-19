import pandas as pd 

files = pd.read_csv('downloaded-files.csv')
overview_sheet = pd.read_csv('overview-sheet.csv', delimiter=';')

# Extract the GHGA file IDs from the files DataFramee
file_ids = files['fileid'].tolist() 

# Filter the overview_sheet to keep only rows where GHGA_F is in the list of file IDs
filtered_overview = overview_sheet[overview_sheet['GHGA_F'].isin(file_ids)]


# Remove files where FileName contains 'PseudoFile'
filtered_overview = filtered_overview[~filtered_overview['FileName'].str.contains('PseudoFile', na=False)]

fastq = filtered_overview[filtered_overview['FileType'] == 'FASTQ']


sarek_fastq = pd.DataFrame()

sarek_fastq['patient'] = fastq['PID'].apply(lambda x: 'P' + x.split('_')[-1])
sarek_fastq['sample'] = fastq['PID'].apply(lambda x: 'S' + x.split('_')[-1])
sarek_fastq['sex'] = fastq['Biolsex'].apply(lambda x: 'XX' if x == 'FEMALE' else 'XY')
sarek_fastq['status'] = fastq['CaseControl'].apply(lambda x: '1' if x == 'CASE' else '0')
sarek_fastq['fastq'] = 'WES/' + fastq['GHGA_F']
sarek_fastq['read'] = fastq['R1_R2']

# Append _T to tumor samples (cases) and _N to normal samples (controls)
sarek_fastq['sample'] = sarek_fastq.apply(lambda row: row['sample'] + '_T' if row['status'] == '1' else row['sample'] + '_N', axis=1)

# Create a temporary dataframe with fastq path and read number
temp_df = sarek_fastq[['patient', 'sample', 'sex', 'status', 'fastq', 'read']]

# Convert the read column to string to ensure proper handling
temp_df['read'] = 'fastq_' + temp_df['read'].astype(int).astype(str)

# Pivot the dataframe to create separate columns for read 1 and 2
pivoted = temp_df.pivot_table(
    index=['patient', 'sample', 'sex', 'status'],
    columns='read',
    values='fastq',
    aggfunc='first'
).reset_index()

# Replace the original dataframe with the pivoted one
sarek_fastq_piv = pivoted

sarek_fastq_piv['lane'] = 'lane_1'

sarek_fastq_piv[['patient', 'sex', 'status', 'sample', 'lane', 'fastq_1', 'fastq_2']].to_csv('sarek-fastq-samplesheet.csv', index=False, sep=',')