import click
import pandas as pd

def read_gdc_sheet(filepath: str):
    gdc_sheet = pd.read_csv(filepath, sep='\t')
    return gdc_sheet

def read_clinical_sheet(filepath: str):
    clinical_sheet = pd.read_csv(filepath, sep='\t')
    return clinical_sheet

def get_file_path(sample_id, gdc_sample_sheet, custom_path=''):
    file_id = gdc_sample_sheet[gdc_sample_sheet['Sample ID'] == sample_id]['File ID'].values[0]
    file_name = gdc_sample_sheet[gdc_sample_sheet['Sample ID'] == sample_id]['File Name'].values[0]
    return custom_path + '/' + file_id + '/' + file_name

def get_sample_status(sample_id, gdc_sample_sheet):
    sample_type = gdc_sample_sheet[gdc_sample_sheet['Sample ID'] == sample_id]['Sample Type']
    if sample_type.str.contains('tumor', case=False).any():
        return 1
    else:
        return 0

def get_patient_sex(patient, clinical_sheet):
    sex_string = clinical_sheet[clinical_sheet['case_submitter_id'] == patient]['gender'].values[0]
    if sex_string == 'female':
        return 'XX'
    if sex_string == 'male':
        return 'XY'
    else:
        return ''

def remove_duplicate_normals(sarek_sheet):
    # First, we group the dataframe by 'patient' and 'status'
    grouped = sarek_sheet.groupby(['patient', 'status'])

    # Then, we apply a function to each group
    # If the group is normal (status=0), we take the first row
    # If the group is tumor (status=1), we take all rows
    def select_rows(group):
        if group['status'].iloc[0] == 0:
            if not group.iloc[1:].empty:
                print(group.iloc[1:][['patient', 'sample']])
            return group.head(1)
        else:
            return group

    # We apply the function to each group and concatenate the results
    sarek_sheet = grouped.apply(select_rows).reset_index(drop=True)

    return sarek_sheet
    

def create_sarek_sheet(gdc_sheet, clinical_sheet, custom_path):
    sarek_sheet = gdc_sheet[['Case ID','Sample ID']].copy()
    sarek_sheet.rename({
        'Case ID':'patient',
        'Sample ID':'sample'
        }, axis=1, inplace=True)
    sarek_sheet['status'] = sarek_sheet['sample'].apply(lambda x: get_sample_status(x, gdc_sheet))
    sarek_sheet['lane'] = 'lane_1'
    sarek_sheet['sex'] = sarek_sheet['patient'].apply(lambda x: get_patient_sex(x, clinical_sheet))
    sarek_sheet['bam'] = sarek_sheet['sample'].apply(lambda x: get_file_path(x, gdc_sheet, custom_path))
    # Remove duplicate normals
    sarek_sheet = remove_duplicate_normals(sarek_sheet)
    return sarek_sheet

@click.command()
@click.option('--gdc_sample_sheet', required=True, help='Path to the GDC sample sheet')
@click.option('--clinical_sheet', default='clinical.tsv', required=True, help='Path to the GDC sex sheet')
@click.option('--custom_path', default='', help='Custom path to bam files (will be added to sample sheet)')
@click.option('--output_file', default='samplesheet.csv', help='Path to the output CSV file')
def main(gdc_sample_sheet, clinical_sheet, custom_path, output_file):
    # Read GDC sheets
    gdc_sheet = read_gdc_sheet(gdc_sample_sheet)
    clinical_sheet = read_clinical_sheet(clinical_sheet)

    # Create Sarek sheet
    sarek_sheet = create_sarek_sheet(gdc_sheet, clinical_sheet, custom_path)

    # Save the resulting DataFrame to a CSV file
    sarek_sheet.to_csv(output_file, index=False)
    print(f"Samplesheet successfully created and saved to {output_file}")

if __name__ == '__main__':
    main()