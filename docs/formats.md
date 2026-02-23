# File Formats

SoftMatch uses standard file formats for input and produces easy-to-parse output.

## Input Formats

### Query CSV

The query CSV file specifies the sequences to search for. It can be in two formats:

**Named Sequences (Recommended):**
```csv
Name,Sequence
Adapter_A,GCTAGCTAGCTA
Adapter_B,CGTACGTACGTA
```

**Sequence Only:**
```csv
GCTAGCTAGCTA
CGTACGTACGTA
```

In the second case, names like `Adapter_1`, `Adapter_2` will be automatically assigned.

**IUPAC Support:**
Sequences can contain IUPAC ambiguous bases (e.g., `N`, `R`, `Y`, `S`, `W`, `K`, `M`, `B`, `D`, `H`, `V`). These are expanded into the appropriate regex character classes during matching.

### Input FASTQ

SoftMatch expects a standard 4-line FASTQ file. It currently supports uncompressed files.

## Output Formats

### Text Results (`.txt`)

A tab-separated file with the following columns:

- `ReadID`: The first part of the FASTQ header.
- `Adapter`: The name of the matched adapter.
- `Start`: 0-based start position of the match in the read.
- `End`: 0-based end position of the match.
- `Strand`: `+` for forward match, `-` for reverse complement match.
- `Errors`: The number of errors (mismatches, insertions, deletions) in the match.
- `MatchedSequence`: The actual sequence in the read that matched.

### Interactive HTML Report (`.html`)

A standalone HTML file that provides a scrollable view of the first 500 reads. Each read is shown with its matched adapters highlighted. Hovering over a match provides details.

### Clustered Summary HTML (`_summary.html`)

A standalone HTML file that clusters the first 5000 reads by their adapter signature. It provides a high-level overview of the most common adapter combinations found in your data.
