#%%
import click
import pandas as pd

def read_gdc_sheet(filepath: str):
    gdc_sheet = pd.read_csv(filepath, sep='\t')
    return gdc_sheet

def get_file_path(filename: str, caller: str):
    return new_dir + '/' + caller + "-maf-pass/" + filename.replace('.maf.gz', '.pass.maf')

def get_caller_info(filename: str):
    if 'VarScan2' in filename:
        return 'TCGA VarScan2'
    if 'Pindel' in filename:
        return 'TCGA Pindel'
    if 'MuTect2' in filename:
        return 'TCGA MuTect'
    if 'MuSE' in filename:
        return 'TCGA MuSE'
    else:
        return ''

def get_sarek_path(caseid: str, ext: str):
    return sarek_dir + caseid + ext


new_dir = '/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/tcga-data'

sarek_dir = '/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/vcftomaf/results/'

caller_gdc_sheet = {
    'muse': '/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/tcga-data/MuSE/gdc_sample_sheet.2024-06-11.tsv',
    'pindel-varscan': '/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/tcga-data/Pindel-Varscan/gdc_sample_sheet.2024-08-06.tsv',
    'mutect': '/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/tcga-data/Mutect/gdc_sample_sheet.2024-05-10.tsv'
}

sheets = pd.DataFrame()
for caller, gdc_sheet in caller_gdc_sheet.items():
    sheet = read_gdc_sheet(gdc_sheet)
    sheet['filepath'] = sheet['File Name'].apply(get_file_path, caller=caller)
    sheet['caller']  = sheet['File Name'].apply(get_caller_info)
    sheets = pd.concat([sheets, sheet])

sheets['case'] = sheets['Case ID'].apply(lambda x: x[:12])

# Add a new line to the sheets dataframe based on the get_sarek_path_mutect function
sarek_entries = []
for case_id in sheets['case'].unique():
    sarek_path = get_sarek_path(case_id, ext = '_mutect2.maf')
    sarek_entries.append({
        'Case ID': case_id,
        'File Name': sarek_path.split('/')[-1],
        'filepath': sarek_path,
        'caller': 'Sarek Mutect',
        'case': case_id
    })
    sarek_path2 = get_sarek_path(case_id, ext = '_strelka_snv.maf')
    sarek_entries.append({
        'Case ID': case_id,
        'File Name': sarek_path2.split('/')[-1],
        'filepath': sarek_path2,
        'caller': 'Sarek Strelka SNV',
        'case': case_id
    })
    sarek_path3 = get_sarek_path(case_id, ext = '_strelka_indel.maf')
    sarek_entries.append({
        'Case ID': case_id,
        'File Name': sarek_path3.split('/')[-1],
        'filepath': sarek_path3,
        'caller': 'Sarek Strelka INDEL',
        'case': case_id
    })
    
sarek_df = pd.DataFrame(sarek_entries)
sheets = pd.concat([sheets, sarek_df], ignore_index=True)
# %%
sheets[['filepath', 'caller', 'case']].to_csv('/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/all_samples.csv', index=False)
# %%
callers = {
    'TCGA VarScan2' : 'tcga_varscan',
    'TCGA Pindel': 'tcga_pindel',
    'TCGA MuTect': 'tcga_mutect',
    'TCGA MuSE': 'tcga_muse',
    'Sarek Mutect': 'sarek_mutect'
}
# Create one sheet per Caller
for caller in sheets['caller'].unique():
    if caller == 'Sarek Strelka SNV' or caller == 'Sarek Strelka INDEL':
        caller_sheet = sheets[(sheets['caller'] == 'Sarek Strelka SNV') | (sheets['caller'] == 'Sarek Strelka INDEL')]
        caller_sheet[['filepath', 'caller', 'case']].to_csv(f'/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/sarek_strelka_samples.csv', index=False)
    else:
        caller_sheet = sheets[sheets['caller'] == caller]
        caller_name = callers[caller]
        caller_sheet[['filepath', 'caller', 'case']].to_csv(f'/Users/famke/01-ghga-project/homogeneous-data-processing/variantcalling/TCGA-CHOL/{caller_name}_samples.csv', index=False)
# %%


# remove TCGA-ZK and TCGA-5A