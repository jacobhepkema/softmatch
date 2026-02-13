# softmatch

This python package uses regex to check FASTQ reads for the presence of certain pre-defined (expected) sequences, allowing for a certain number of errors using option `--errors <num_errors>`.
By specifying `--summary`, the script will additionally cluster the reads by which sequences were detected.
Disable HTML output with `--no_html`.

Example usage:
```bash
softmatch --errors 4 --summary sequences_to_query.csv reads.fastq
```

The format of `sequences_to_query.csv` is e.g.:
```
adapter_1,ACGCGATCGACGGGCGGCAGT
adapter_2,CAGCCGAGCGTATGTAGGCGGACTACGAGCCG
```

Example sequence cluster output in summary:
<img width="1314" height="834" alt="image" src="https://github.com/user-attachments/assets/fa4cfb2c-f865-4ae6-bd76-f49426ed530e" />

