# Tutorial: Basic Usage

This tutorial will guide you through the basic steps of using SoftMatch to scan a FASTQ file for adapter sequences.

## 1. Prepare your Query CSV

Create a CSV file containing the names and sequences of the adapters you want to find. For example, `queries.csv`:

```csv
adapter_1,ACGCGATCGACGGGCGGCAGT
adapter_2,CAGCCGAGCGTATGTAGGCGGACTACGAGCCG
```

If you don't provide names, SoftMatch will assign generic ones (`Adapter_1`, `Adapter_2`, etc.).

## 2. Run SoftMatch

Run the `softmatch` command-line tool, providing the query CSV and your input FASTQ file.

```bash
softmatch --errors 2 --summary queries.csv reads.fastq
```

### Key Arguments:

- `--errors 2`: Allows up to 2 errors (mismatches, insertions, or deletions) per match.
- `--summary`: Generates a clustered summary HTML report in addition to the standard per-read report.

## 3. Explore the Results

SoftMatch produces several output files:

1. **`softmatch_results.txt`**: A tab-separated text file containing details for every match found.
2. **`softmatch_results.html`**: An interactive HTML report showing individual reads and their matched adapters.
3. **`softmatch_results_summary.html`**: (If `--summary` is used) A clustered view of the reads, grouped by their adapter "signature".

## Example with Sample Data

You can find sample data in the `examples/` directory of the repository.

```bash
softmatch --errors 2 --summary examples/queries.csv examples/sample.fastq
```

This will generate:
- `softmatch_results.txt`
- `softmatch_results.html`
- `softmatch_results_summary.html`

Open the HTML files in your web browser to visualize the results!
