# Utils

This directory contains a collection of Python scripts that provide various utility functions and helper scripts for data processing and variant calling.

## Scripts

# Utils
This directory contains a collection of Python scripts that provide various utility functions and helper scripts for data processing and variant calling.

## Scripts

- `sarek_to_maf_sheet.py`: This script converts data from the samplesheet format for nf-core/sarek to the samplesheet format for qbic-pipelines/vcftomaf.

- `gdc_to_sarek_sheet.py`: This script converts the samplesheet plus the clinical sheet from the GDC (Genomic Data Commons) format to the samplesheet format for nf-core/sarek.

## Usage
To use any of the scripts in this directory, you can simply run them using Python.

```bash
python gdc_to_sarek_sheet.py --gdc_sample_sheet <path/to/gdc-sheet> --clinical_sheet <path/to/gdc-clinical-sheet> --custom_path <path/to/bam-files> --output_file <output.csv>

python sarek_to_maf_sheet.py --sarek_sample_sheet <path/to/sarek-sheet> --custom_path <path/to/results/annotation> --output_file <output.csv>
```
