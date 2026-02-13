import argparse
import sys
from pathlib import Path
from .processing import parse_fastq, parse_queries, find_matches
from .visualization import generate_html, generate_cluster_html
from .clustering import cluster_reads

DEFAULT_ERRORS = 2
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

        for header, seq, qual in parse_fastq(args.input_fastq):
            total_reads += 1
            if total_reads % 10000 == 0:
                print(f"Processed {total_reads} reads...", end='\r')

            hits = find_matches(seq, queries, args.errors)

            if hits:
                reads_with_hits += 1
                read_id = header.split()[0] # Take first part of header

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
            print(f"Note: HTML report limited to first {HTML_READ_LIMIT} matching reads to ensure performance.")
        generate_html(results_for_html, html_path, query_names=query_names)

    # 4. Generate Summary
    if args.summary:
        summary_path = Path(args.output).parent / (Path(args.output).stem + "_summary.html")
        print(f"Generating clustered summary: {summary_path}")
        if len(results_for_summary) == SUMMARY_READ_LIMIT:
            print(f"Note: Summary limited to first {SUMMARY_READ_LIMIT} matching reads.")
        clusters = cluster_reads(results_for_summary)
        generate_cluster_html(clusters, summary_path, query_names=query_names)

if __name__ == "__main__":
    main()
