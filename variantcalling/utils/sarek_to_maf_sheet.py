import pandas as pd
import click

# Read the Sarek sheet from a CSV file
def read_sarek_sheet(filepath: str):
    sarek_sheet = pd.read_csv(filepath, sep=',')
    return sarek_sheet

# Create rows for a specific patient in the vcf2maf base sheet
def create_rows(patient, sarek_sheet):
    rows = sarek_sheet[sarek_sheet['patient'] == patient]
    for index, row in rows.iterrows():
        if row['status'] == 0:
            normal_id = row['sample']
        elif row['status'] == 1:
            tumor_id = row['sample']
    new_row = pd.DataFrame({
        'patient': [patient],
        'normal_id': [normal_id],
        'tumor_id': [tumor_id],
    }).iloc[0]
    return new_row

# Create the vcf2maf base sheet by applying create_rows to each patient
def create_vcf2maf_base_sheet(sarek_sheet: pd.DataFrame):
    vcf2maf_sheet = pd.DataFrame(columns=['patient', 'normal_id', 'tumor_id'])
    vcf2maf_sheet = pd.concat([vcf2maf_sheet, sarek_sheet.apply(lambda x: create_rows(x['patient'], sarek_sheet), axis=1)], ignore_index=True)
    vcf2maf_sheet = vcf2maf_sheet.drop_duplicates().reset_index(drop=True)
    return vcf2maf_sheet

# Create caller rows for each patient in the vcf2maf base sheet
def create_caller_rows(vcf2maf_sheet: pd.DataFrame, sarek_sheet: pd.DataFrame):
    callers = ['manta', 'mutect2', 'strelka_snv', 'strelka_indel']
    duplicated_rows = pd.DataFrame(columns=['patient', 'normal_id', 'tumor_id'])
    for index, row in vcf2maf_sheet.iterrows():
        patient = row['patient']
        normal_id = row['normal_id']
        tumor_id = row['tumor_id']
        for caller in callers:
            duplicated_rows = pd.concat([duplicated_rows, pd.DataFrame({
                'caller': [caller],
                'patient': [patient],
                'normal_id': [normal_id],
                'tumor_id': [tumor_id],
            })], ignore_index=True)
    return duplicated_rows

# Add VCF filepaths to the caller rows
def add_vcf_filepaths(caller_rows, path):
    caller_rows['index'] = caller_rows.apply(lambda row: f'{path}/{row["caller"].split("_")[0]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"].split("_")[0]}.filtered_VEP.ann.vcf.gz.tbi' if row["caller"] == 'mutect2' else f'{path}/{row["caller"].split("_")[0]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"].split("_")[0]}.somatic_indels_VEP.ann.vcf.gz.tbi' if row["caller"] == 'strelka_indel' else f'{path}/{row["caller"].split("_")[0]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"].split("_")[0]}.somatic_snvs_VEP.ann.vcf.gz.tbi' if row["caller"] == 'strelka_snv' else f'{path}/{row["caller"]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"]}.diploid_sv_VEP.ann.vcf.gz.tbi', axis=1)
    caller_rows['vcf'] = caller_rows.apply(lambda row: f'{path}/{row["caller"].split("_")[0]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"].split("_")[0]}.filtered_VEP.ann.vcf.gz' if row["caller"] == 'mutect2' else f'{path}/{row["caller"].split("_")[0]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"].split("_")[0]}.somatic_indels_VEP.ann.vcf.gz' if row["caller"] == 'strelka_indel' else f'{path}/{row["caller"].split("_")[0]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"].split("_")[0]}.somatic_snvs_VEP.ann.vcf.gz' if row["caller"] == 'strelka_snv' else f'{path}/{row["caller"]}/{row["tumor_id"]}_vs_{row["normal_id"]}/{row["tumor_id"]}_vs_{row["normal_id"]}.{row["caller"]}.diploid_sv_VEP.ann.vcf.gz', axis=1)
    return caller_rows

# Get tumor and normal names for a specific patient and caller
def get_tumor_normal_names_vcf(patient, caller: str, sarek_sheet: pd.DataFrame):
    tumor_sample = sarek_sheet[(sarek_sheet['status'] == 1) & (sarek_sheet['patient'] == patient)]['sample'].values[0]
    normal_sample = sarek_sheet[(sarek_sheet['status'] == 0) & (sarek_sheet['patient'] == patient)]['sample'].values[0]
    caller_to_normal = {
        'manta': 'NORMAL',
        'mutect2': f'{patient}_{normal_sample}',
        'strelka_snv': 'NORMAL',
        'strelka_indel': 'NORMAL'
    }
    caller_to_tumor = {
        'manta': 'TUMOR',
        'mutect2': f'{patient}_{tumor_sample}',
        'strelka_snv': 'TUMOR',
        'strelka_indel': 'TUMOR'
    }
    return pd.DataFrame({
        'vcf_normal_id': [caller_to_normal[caller]],
        'vcf_tumor_id': [caller_to_tumor[caller]]
    }).iloc[0]

# Main function to process the Sarek sample sheet and generate the output CSV file
@click.command()
@click.option('--sarek_sample_sheet', required=True, help='Path to the GDC sample sheet')
@click.option('--custom_path', default='', help='Custom path to bam files (will be added to sample sheet)')
@click.option('--output_file', default='samplesheet.csv', help='Path to the output CSV file')
def main(sarek_sample_sheet, custom_path, output_file):
    # Read the Sarek sample sheet
    sarek_sheet = read_sarek_sheet(sarek_sample_sheet)
    
    # Create the vcf2maf base sheet
    vcf2maf_base_sheet = create_vcf2maf_base_sheet(sarek_sheet)
    
    # Create caller rows for each patient in the vcf2maf base sheet
    caller_rows = create_caller_rows(vcf2maf_base_sheet, sarek_sheet)
    
    # Add VCF filepaths to the caller rows
    caller_rows = add_vcf_filepaths(caller_rows, custom_path)
    
    # Get tumor and normal names for each caller and patient
    caller_rows[['vcf_normal_id', 'vcf_tumor_id']] = caller_rows.apply(lambda row: pd.Series({'vcf_normal_id': get_tumor_normal_names_vcf(row['patient'], row['caller'], sarek_sheet)['vcf_normal_id'], 'vcf_tumor_id': get_tumor_normal_names_vcf(row['patient'], row['caller'], sarek_sheet)['vcf_tumor_id']}), axis=1)
    
    # Filter callers
    caller_rows = caller_rows[caller_rows['caller'] != 'manta']

    # Generate sample names
    caller_rows['sample'] = caller_rows.apply(lambda row: f'{row["patient"]}_{row["caller"]}', axis=1)
    
    # Drop unnecessary columns
    caller_rows = caller_rows.drop(columns=['patient', 'caller'])
    
    # Save the caller rows to the output CSV file
    caller_rows.to_csv(output_file, index=False)

if __name__ == '__main__':
    main()