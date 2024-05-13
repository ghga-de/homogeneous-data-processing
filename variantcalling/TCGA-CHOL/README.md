# Batch run of TCGA samples with sarek

1. Build cohort Data portal use:
    Use Cohort Builder with:
    - General:
        - Program: TCGA
        - Project: TCGA-CHOL
    - Available Data:
        - Data Category: sequencing reads
        - Experimental Strategy: WXS
2. Create new workspace `tcga` 
3. Download data gdc-client
4. Transform into sarek samplesheet with Python script.
    - Download Samplesheet from GDC
    - Download clinical sheet
    - run `utils/gdc_to_sarek_sheet.py`
5. Remove samples where clinical information is missing:
    1. TCGA-ZK-AAYZ
    2. TCGA-5A-A8ZF
    3. TCGA-5A-A8ZG
6. Find target `bed` files for WXS experiments
    
    [https://api.gdc.cancer.gov/files/](https://api.gdc.cancer.gov/files/)e52d13b0-1cb9-4f08-82e0-4dc024713a94?pretty=true&fields=analysis.metadata.read_groups.target_capture_kit_target_region
    
    [https://api.gdc.cancer.gov/files/](https://api.gdc.cancer.gov/files/)3a3f85d0-5d76-4c46-96b0-58443d2d1f81?pretty=true&fields=analysis.metadata.read_groups.target_capture_kit_target_region
    
    [http://www.genomedata.org/pmbio-workshop/results/all/inputs/SeqCapEZ_Exome_v3.0_Design_Annotation_files/](http://www.genomedata.org/pmbio-workshop/results/all/inputs/SeqCapEZ_Exome_v3.0_Design_Annotation_files/)
    
    → only available for hg19 → needs liftover
    
    - [http://hgdownload.cse.ucsc.edu/downloads.html#liftover](http://hgdownload.cse.ucsc.edu/downloads.html#liftover)
    - [http://hgdownload.cse.ucsc.edu/admin/exe/](http://hgdownload.cse.ucsc.edu/admin/exe/)
    
    ```bash
    rsync -aP rsync://hgdownload.soe.ucsc.edu/genome/admin/exe/linux.x86_64/liftOver ./
    ./liftOver SeqCap_EZ_Exome_v3_hg19_capture_targets.bed hg18ToHg39.over.chain.gz SeqCap_EZ_Exome_v3_hg38_capture_targets.bed unlifted.bed
    ```
    
7. Sort `bed` file
    
    https://nfcore.slack.com/archives/CGFUX04HZ/p1663842164835839
    
    → `bedtools sort`
    
8. Create params.json for sarek
    
    ```json
    {
        "input": "\/sfs\/9\/ws\/paifb01-tcga\/samplesheet.csv",
        "outdir": "\/sfs\/9\/ws\/paifb01-tcga\/sarek-results",
        "intervals": "/sfs/9/ws/paifb01-tcga/reference/target/SeqCap_EZ_Exome_v3_hg38_capture_targets_sorted.bed",
        "tools": "haplotypecaller,strelka,mutect2,manta,ascat,cnvkit,vep,snpeff",
        "only_paired_variant_calling": true,
        "email": "famke.baeuerle@qbic.uni-tuebingen.de"
    }
    ```
    
9. Install nextflow & run sarek
    
    ```bash
    ./nextflow run nf-core/sarek -r 3.4.0 -profile cfc -params-file sarek-params.json
    ```