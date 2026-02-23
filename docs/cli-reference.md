# CLI Reference

SoftMatch is invoked via the `softmatch` command.

## Usage

```bash
softmatch [OPTIONS] QUERY_CSV INPUT_FASTQ
```

## Positional Arguments

- `QUERY_CSV`: Path to a CSV file containing adapter sequences. See [File Formats](formats.md) for details.
- `INPUT_FASTQ`: Path to the input FASTQ file (uncompressed).

## Options

### `--errors` (Integer, Default: 2)

The maximum number of errors allowed for a match to be considered valid. Errors include mismatches, insertions, and deletions. SoftMatch uses the `regex` library's `BESTMATCH` flag to find the match with the fewest errors within this limit.

### `--no_html` (Flag)

If set, SoftMatch will not generate the interactive HTML report (`softmatch_results.html`). This can be useful for very large datasets or when only the text output is needed.

### `--summary` (Flag)

If set, SoftMatch will generate a clustered summary HTML report (`softmatch_results_summary.html`). Reads are grouped by the set of adapters they contain (their "signature"), and a representative view of each cluster is shown.

### `--output`, `-o` (String, Default: `softmatch_results.txt`)

Specifies the path for the output text file. The HTML reports will use the same base name but with `.html` and `_summary.html` suffixes.

## Environment Variables

SoftMatch uses standard Python multiprocessing. You can control the number of processes used by setting environment variables if your OS supports it (e.g., `OMP_NUM_THREADS`), but typically it will use all available CPU cores.
