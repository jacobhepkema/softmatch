#!/usr/bin/env python3
import argparse
import csv
import sys
import regex
import json
import html
from pathlib import Path

# --- Configuration ---
# Default max errors allowed (e.g., 2 mismatches/indels)
DEFAULT_ERRORS = 2
# Max reads to include in HTML to prevent browser crash (text output has all)
HTML_READ_LIMIT = 500 

def parse_fastq(filepath):
    """
    Generator that streams FASTQ records to save memory.
    Yields (header, sequence, qual).
    """
    with open(filepath, 'r') as f:
        while True:
            header = f.readline().strip()
            if not header: break
            seq = f.readline().strip()
            f.readline() # Plus line
            qual = f.readline().strip()
            yield header, seq, qual

def parse_queries(filepath):
    """
    Parses CSV: Name,Sequence or just Sequence.
    Returns list of dicts: {'name': str, 'seq': str}
    """
    queries = []
    with open(filepath, 'r') as f:
        # Sniff format
        line = f.readline().strip()
        f.seek(0)
        
        # Check if CSV has header or simple list
        has_comma = ',' in line
        reader = csv.reader(f)
        
        idx = 1
        for row in reader:
            if not row: continue
            if len(row) >= 2:
                queries.append({'name': row[0].strip(), 'seq': row[1].strip().upper()})
            elif len(row) == 1:
                # Assign generic name if missing
                queries.append({'name': f"Adapter_{idx}", 'seq': row[0].strip().upper()})
                idx += 1
    return queries

def find_matches(read_seq, queries, max_errors):
    """
    Uses regex fuzzy matching to find adapters.
    Returns list of hits.
    """
    hits = []
    for q in queries:
        pattern = f"({q['seq']}){{e<={max_errors}}}"
        # bestmatch optimizes for lowest error count
        matches = regex.finditer(pattern, read_seq, regex.BESTMATCH)
        
        for m in matches:
            # regex match objects with fuzzy logic
            start, end = m.span()
            # fuzzy_counts returns (sub, ins, del)
            errors = sum(m.fuzzy_counts)
            match_seq = m.group()
            
            hits.append({
                'name': q['name'],
                'start': start,
                'end': end,
                'len': end - start,
                'errors': errors,
                'match_seq': match_seq,
                'strand': 1 # Assuming query is 5'->3' on the read
            })
    
    # Sort hits by start position
    hits.sort(key=lambda x: x['start'])
    return hits

def generate_html(data, output_path):
    """
    Generates a standalone HTML with interactive visualization.
    """
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Softmatch Visualization</title>
    <style>
        :root {{ --bg: #f9f9f9; --seq-bg: #ffffff; --annot-color: #6d5dfc; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: var(--bg); padding: 20px; color: #333; }}
        h1 {{ font-size: 20px; margin-bottom: 20px; }}
        .read-container {{ background: var(--seq-bg); border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); overflow-x: auto; }}
        .read-header {{ font-weight: bold; font-size: 14px; margin-bottom: 10px; color: #555; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        
        /* Benchling-like Visualization Wrapper */
        .viz-wrapper {{ position: relative; font-family: 'Menlo', 'Consolas', 'Courier New', monospace; font-size: 14px; line-height: 1.5; white-space: pre; padding-top: 30px; /* Space for annotations */ }}
        
        .sequence-layer {{ letter-spacing: 2px; color: #333; display: inline-block; }}
        
        /* Annotation Tracks */
        .annotation-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
        
        .annotation {{
            position: absolute;
            height: 6px;
            background: var(--annot-color);
            border-radius: 2px;
            opacity: 0.8;
            cursor: pointer;
            pointer-events: auto;
            transition: all 0.2s;
        }}
        
        .annotation:hover {{ opacity: 1; height: 10px; transform: translateY(-2px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        
        /* Arrow heads for direction */
        .annotation.fwd::after {{
            content: ''; position: absolute; right: -4px; top: -3px;
            border-top: 6px solid transparent; border-bottom: 6px solid transparent;
            border-left: 6px solid var(--annot-color);
        }}
        
        .label {{
            position: absolute; top: -18px; font-size: 10px; color: var(--annot-color); font-weight: bold; white-space: nowrap;
        }}
        
        .tooltip {{
            display: none; position: absolute; background: #333; color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 12px; z-index: 100; pointer-events: none;
        }}
    </style>
</head>
<body>
    <h1>Softmatch Results <span style="font-weight:normal; font-size:14px; color:#666">Top {len(data)} reads with hits</span></h1>
    <div id="tooltip" class="tooltip"></div>
    <div id="container"></div>

    <script>
        const data = {json.dumps(data)};
        const container = document.getElementById('container');
        const tooltip = document.getElementById('tooltip');
        
        // Character width in pixels (approx for monospace 14px + 2px spacing)
        // We will calculate this dynamically to be precise
        const charWidth = 10.45; // tuned for Menlo/Consolas + 2px spacing
        
        data.forEach(read => {{
            const div = document.createElement('div');
            div.className = 'read-container';
            
            // Build Annotation HTML
            let annotHTML = '';
            
            // Simple lane logic to prevent overlapping text
            // In a real app we'd compute layout, here we just cycle heights
            read.hits.forEach((hit, idx) => {{
                // Math for positioning
                // chars are spaced by letter-spacing (2px) roughly
                // best way is to use ch units, but absolute divs need % or px.
                // We use ch units for robust monospace alignment.
                
                const startCh = hit.start;
                const widthCh = hit.len;
                const topOffset = (idx % 3) * 12; // Stagger overlapping annotations
                
                // Color cycling
                const colors = ['#6d5dfc', '#fc5d5d', '#5dfca8', '#fcb05d'];
                const color = colors[idx % colors.length];
                
                annotHTML += `
                    <div class="annotation fwd" 
                         style="left: calc(${{startCh}} * 1ch + ${{startCh}} * 2px); 
                                width: calc(${{widthCh}} * 1ch + ${{widthCh-1}} * 2px); 
                                top: ${{topOffset}}px;
                                background-color: ${{color}};
                                --annot-color: ${{color}};"
                         onmouseover="showTooltip(event, '${{hit.name}}', ${{hit.errors}}, '${{hit.match_seq}}')"
                         onmouseout="hideTooltip()">
                         <div class="label" style="color:${{color}}">${{hit.name}}</div>
                    </div>
                `;
            }});

            div.innerHTML = `
                <div class="read-header">${{read.id}}</div>
                <div class="viz-wrapper">
                    <div class="annotation-layer">${{annotHTML}}</div>
                    <div class="sequence-layer">${{read.seq}}</div>
                </div>
            `;
            container.appendChild(div);
        }});

        function showTooltip(e, name, err, seq) {{
            tooltip.style.display = 'block';
            tooltip.style.left = e.pageX + 10 + 'px';
            tooltip.style.top = e.pageY + 10 + 'px';
            tooltip.innerHTML = `<strong>${{name}}</strong><br>Seq: ${{seq}}<br>Errors: ${{err}}`;
        }}
        
        function hideTooltip() {{
            tooltip.style.display = 'none';
        }}
    </script>
</body>
</html>
"""
    with open(output_path, 'w') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description="FAST soft-matching of adapters in FASTQ files.")
    parser.add_argument("query_csv", help="CSV file with columns: Name,Sequence")
    parser.add_argument("input_fastq", help="Input FASTQ file")
    parser.add_argument("--errors", type=int, default=DEFAULT_ERRORS, help=f"Max errors allowed (default: {DEFAULT_ERRORS})")
    parser.add_argument("--no_html", action="store_true", help="Disable HTML visualization output")
    parser.add_argument("--output", "-o", default="softmatch_results.txt", help="Output text file path")
    
    args = parser.parse_args()
    
    # 1. Load Queries
    print(f"Loading queries from {args.query_csv}...")
    queries = parse_queries(args.query_csv)
    print(f"Loaded {len(queries)} query sequences.")

    # 2. Process FASTQ
    print(f"Scanning {args.input_fastq}...")
    
    results_for_html = []
    total_reads = 0
    reads_with_hits = 0
    
    # Open output text file
    with open(args.output, 'w') as out_f:
        out_f.write("ReadID\tAdapter\tStart\tEnd\tErrors\tMatchedSequence\n")
        
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
                    out_f.write(f"{read_id}\t{hit['name']}\t{hit['start']}\t{hit['end']}\t{hit['errors']}\t{hit['match_seq']}\n")
                
                # Save to HTML buffer (limit check)
                if not args.no_html and len(results_for_html) < HTML_READ_LIMIT:
                    results_for_html.append({
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
        generate_html(results_for_html, html_path)

if __name__ == "__main__":
    main()
