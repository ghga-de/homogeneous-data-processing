import pandas as pd 

files = pd.read_csv('downloaded-files.csv')
individual = pd.read_csv('GHGAS22583975347886_Individual.csv')
process_data_file = pd.read_csv('GHGAS22583975347886_ProcessDataFile.csv')
research_data_file = pd.read_csv('GHGAS22583975347886_ResearchDataFile.csv')
sample = pd.read_csv('GHGAS22583975347886_Sample.csv', delimiter=';')

filtered_process_data_file = process_data_file[process_data_file['accession'].isin(files['fileid'])]

print(filtered_process_data_file[['accession', 'format']])

filtered_research_data_file = research_data_file[research_data_file['accession'].isin(files['fileid'])]

print(filtered_research_data_file[['accession', 'format']])

filtered_individual = individual[individual['accession'].isin(filtered_process_data_file['accession'])]

print(filtered_individual[['accession', 'sex']])

print(sample[['accession', 'case_control_status', 'individual']])