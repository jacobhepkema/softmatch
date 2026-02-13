import argparse
import sys
import concurrent.futures
import itertools
import regex
from pathlib import Path
from .processing import parse_fastq, parse_queries, find_matches, reverse_complement
from .visualization import generate_html, generate_cluster_html
from .clustering import cluster_reads

DEFAULT_ERRORS = 2
BATCH_SIZE = 1000

def _process_read_batch(batch, queries, max_errors):
    """Worker function for multiprocessing."""
    results = []
    for header, seq, qual in batch:
        hits = find_matches(seq, queries, max_errors)
        results.append((header, seq, hits))
    return results

def _get_batches(fastq_gen, batch_size):
    """Yield batches of records from the FASTQ generator."""
    batch = []
    for record in fastq_gen:
        batch.append(record)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
HTML_READ_LIMIT = 500
SUMMARY_READ_LIMIT = 5000

def main():
    parser = argparse.ArgumentParser(description="FAST soft-matching of adapters in FASTQ files.")
    parser.add_argument("query_csv", help="CSV file with columns: Name,Sequence")
    parser.add_argument("input_fastq", help="Input FASTQ file")
    parser.add_argument("--errors", type=int, default=DEFAULT_ERRORS, help=f"Max errors allowed (default: {DEFAULT_ERRORS})")
    parser.add_argument("--no_html", action="store_true", help="Disable HTML visualization output")
    parser.add_argument("--summary", action="store_true", help="Generate a clustered summary visualization")
    parser.add_argument("--output", "-o", default="softmatch_results.txt", help="Output text file path")

    args = parser.parse_args()

    # 1. Load Queries
    print(f"Loading queries from {args.query_csv}...")
    queries = parse_queries(args.query_csv)

    # Pre-compile queries for speed
    for q in queries:
        q['fwd_re'] = regex.compile(f"({q['seq']}){{e<={args.errors}}}", regex.BESTMATCH)
        rev_seq = reverse_complement(q['seq'])
        q['rev_seq'] = rev_seq
        if rev_seq != q['seq']:
            q['rev_re'] = regex.compile(f"({rev_seq}){{e<={args.errors}}}", regex.BESTMATCH)
        else:
            q['rev_re'] = None

    query_names = [q['name'] for q in queries]
    print(f"Loaded {len(queries)} query sequences.")

    # 2. Process FASTQ
    print(f"Scanning {args.input_fastq}...")

    results_for_html = []
    results_for_summary = []
    total_reads = 0
    reads_with_hits = 0

    # Open output text file
    with open(args.output, 'w') as out_f:
        out_f.write("ReadID\tAdapter\tStart\tEnd\tStrand\tErrors\tMatchedSequence\n")

        fastq_gen = parse_fastq(args.input_fastq)
        batches = _get_batches(fastq_gen, BATCH_SIZE)

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Use executor.map to maintain order
            for batch_results in executor.map(_process_read_batch, batches,
                                            itertools.repeat(queries),
                                            itertools.repeat(args.errors)):
                for header, seq, hits in batch_results:
                    total_reads += 1
                    if total_reads % 10000 == 0:
                        print(f"Processed {total_reads} reads...", end='\r')

                    read_id = header.split()[0] # Take first part of header
                    if hits:
                        reads_with_hits += 1

                        # Write to text file
                        for hit in hits:
                            strand_str = "+" if hit['strand'] == 1 else "-"
                            out_f.write(f"{read_id}\t{hit['name']}\t{hit['start']}\t{hit['end']}\t{strand_str}\t{hit['errors']}\t{hit['match_seq']}\n")

                    # Save to HTML buffer (limit check)
                    if not args.no_html and len(results_for_html) < HTML_READ_LIMIT:
                        results_for_html.append({
                            'id': read_id,
                            'seq': seq,
                            'hits': hits
                        })

                    # Save to Summary buffer (limit check)
                    if args.summary and len(results_for_summary) < SUMMARY_READ_LIMIT:
                        results_for_summary.append({
                            'id': read_id,
                            'seq': seq,
                            'hits': hits
                        })

    print(f"\nDone. Processed {total_reads} reads.")
    print(f"Reads with at least one match: {reads_with_hits}")
    print(f"Text results written to: {args.output}")

    # 3. Generate HTML
    if not args.no_html:
        html_path = Path(args.output).with_suffix('.html')
        print(f"Generating interactive report: {html_path}")
        if len(results_for_html) == HTML_READ_LIMIT:
            print(f"Note: HTML report limited to first {HTML_READ_LIMIT} reads to ensure performance.")
        generate_html(results_for_html, html_path, query_names=query_names)

    # 4. Generate Summary
    if args.summary:
        summary_path = Path(args.output).parent / (Path(args.output).stem + "_summary.html")
        print(f"Generating clustered summary: {summary_path}")
        if len(results_for_summary) == SUMMARY_READ_LIMIT:
            print(f"Note: Summary limited to first {SUMMARY_READ_LIMIT} reads.")
        clusters = cluster_reads(results_for_summary)
        generate_cluster_html(clusters, summary_path, query_names=query_names)

if __name__ == "__main__":
    main()
