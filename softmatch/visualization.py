import json
import html

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
        .viz-wrapper {{
            position: relative;
            font-family: 'Menlo', 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            padding-top: 40px;
            display: inline-block;
        }}

        .sequence-layer {{ color: #333; white-space: pre; }}

        /* Annotation Tracks */
        .annotation-layer {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }}

        .annotation {{
            position: absolute;
            height: 8px;
            background: var(--annot-color);
            border-radius: 2px;
            opacity: 0.8;
            cursor: pointer;
            pointer-events: auto;
            transition: all 0.2s;
        }}

        .annotation:hover {{ opacity: 1; height: 12px; transform: translateY(-2px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}

        /* Arrow heads for direction */
        .annotation.fwd::after {{
            content: ''; position: absolute; right: -4px; top: -2px;
            border-top: 6px solid transparent; border-bottom: 6px solid transparent;
            border-left: 6px solid var(--annot-color);
        }}

        .annotation.rev::before {{
            content: ''; position: absolute; left: -4px; top: -2px;
            border-top: 6px solid transparent; border-bottom: 6px solid transparent;
            border-right: 6px solid var(--annot-color);
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

        data.forEach(read => {{
            const div = document.createElement('div');
            div.className = 'read-container';

            const header = document.createElement('div');
            header.className = 'read-header';
            header.textContent = read.id;
            div.appendChild(header);

            const vizWrapper = document.createElement('div');
            vizWrapper.className = 'viz-wrapper';

            const annotLayer = document.createElement('div');
            annotLayer.className = 'annotation-layer';

            read.hits.forEach((hit, idx) => {{
                const startCh = hit.start;
                const widthCh = hit.len;
                const topOffset = 10 + (idx % 3) * 12;

                const colors = ['#6d5dfc', '#fc5d5d', '#5dfca8', '#fcb05d'];
                const color = colors[idx % colors.length];
                const strandClass = hit.strand === 1 ? 'fwd' : 'rev';

                const annot = document.createElement('div');
                annot.className = `annotation ${{strandClass}}`;
                annot.style.left = `${{startCh}}ch`;
                annot.style.width = `${{widthCh}}ch`;
                annot.style.top = `${{topOffset}}px`;
                annot.style.backgroundColor = color;
                annot.style.setProperty('--annot-color', color);

                annot.onmouseover = (e) => showTooltip(e, hit.name, hit.errors, hit.match_seq, hit.strand);
                annot.onmouseout = hideTooltip;

                const label = document.createElement('div');
                label.className = 'label';
                label.style.color = color;
                label.textContent = hit.name;
                annot.appendChild(label);

                annotLayer.appendChild(annot);
            }});

            const seqLayer = document.createElement('div');
            seqLayer.className = 'sequence-layer';
            seqLayer.textContent = read.seq;

            vizWrapper.appendChild(annotLayer);
            vizWrapper.appendChild(seqLayer);
            div.appendChild(vizWrapper);
            container.appendChild(div);
        }});

        function showTooltip(e, name, err, seq, strand) {{
            tooltip.style.display = 'block';
            tooltip.style.left = e.pageX + 10 + 'px';
            tooltip.style.top = e.pageY + 10 + 'px';
            const strandText = strand === 1 ? 'Forward' : 'Reverse Complement';
            tooltip.innerHTML = `<strong>${{name}}</strong> (${{strandText}})<br>Seq: ${{seq}}<br>Errors: ${{err}}`;
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

def generate_cluster_html(clusters, output_path):
    """
    Generates a minimalist clustered visualization.
    """

    # Pre-calculate offsets and widths for each cluster
    cluster_data = []
    for sig, reads in clusters.items():
        if not reads: continue

        sig_name = " + ".join([f"{name}({'+' if strand == 1 else '-'})" for name, strand in sig])

        # Max distance before the first adapter to align everything
        max_prefix = max(r['hits'][0]['start'] for r in reads)

        cluster_reads = []
        for r in reads:
            offset = max_prefix - r['hits'][0]['start']

            hits_viz = []
            for hit in r['hits']:
                hits_viz.append({
                    'name': hit['name'],
                    'start': hit['start'] + offset,
                    'len': hit['len'],
                    'strand': hit['strand'],
                    'errors': hit['errors']
                })

            cluster_reads.append({
                'id': r['id'],
                'total_len': r['seq_len'] + offset,
                'hits': hits_viz,
                'offset': offset
            })

        cluster_data.append({
            'signature': sig_name,
            'reads': cluster_reads,
            'max_width': max(r['total_len'] for r in cluster_reads)
        })

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Softmatch Cluster Visualization</title>
    <style>
        body {{ font-family: sans-serif; background: #f0f0f0; padding: 20px; }}
        .cluster-container {{ background: white; border-radius: 8px; padding: 15px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .cluster-title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #444; border-bottom: 1px solid #eee; padding-bottom: 5px; }}

        .viz-area {{
            position: relative;
            font-family: monospace;
            font-size: 10px;
            overflow-x: auto;
            white-space: nowrap;
        }}

        .read-row {{
            position: relative;
            height: 8px;
            margin-bottom: 1px;
            background: #e0e0e0;
            display: block;
        }}

        .adapter-block {{
            position: absolute;
            height: 100%;
            opacity: 0.8;
        }}

        .adapter-block.fwd::after {{
            content: ''; position: absolute; right: -2px; top: 0;
            border-top: 4px solid transparent; border-bottom: 4px solid transparent;
            border-left: 4px solid inherit;
            border-left-color: inherit;
        }}

        .adapter-block.rev::before {{
            content: ''; position: absolute; left: -2px; top: 0;
            border-top: 4px solid transparent; border-bottom: 4px solid transparent;
            border-right: 4px solid inherit;
            border-right-color: inherit;
        }}

        .tooltip {{
            display: none; position: absolute; background: #333; color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 12px; z-index: 100; pointer-events: none;
        }}

        .color-0 {{ background-color: #6d5dfc; }}
        .color-1 {{ background-color: #fc5d5d; }}
        .color-2 {{ background-color: #5dfca8; }}
        .color-3 {{ background-color: #fcb05d; }}
        .color-4 {{ background-color: #5dc3fc; }}
        .color-5 {{ background-color: #bc5dfc; }}

        .color-0.fwd::after {{ border-left-color: #6d5dfc; }}
        .color-0.rev::before {{ border-right-color: #6d5dfc; }}
        .color-1.fwd::after {{ border-left-color: #fc5d5d; }}
        .color-1.rev::before {{ border-right-color: #fc5d5d; }}
        .color-2.fwd::after {{ border-left-color: #5dfca8; }}
        .color-2.rev::before {{ border-right-color: #5dfca8; }}
        .color-3.fwd::after {{ border-left-color: #fcb05d; }}
        .color-3.rev::before {{ border-right-color: #fcb05d; }}
        .color-4.fwd::after {{ border-left-color: #5dc3fc; }}
        .color-4.rev::before {{ border-right-color: #5dc3fc; }}
        .color-5.fwd::after {{ border-left-color: #bc5dfc; }}
        .color-5.rev::before {{ border-right-color: #bc5dfc; }}
    </style>
</head>
<body>
    <h1>Clustered Read Summary</h1>
    <div id="tooltip" class="tooltip"></div>
    <div id="container"></div>

    <script>
        const clusters = {json.dumps(cluster_data)};
        const container = document.getElementById('container');
        const tooltip = document.getElementById('tooltip');

        clusters.forEach(cluster => {{
            const clusterDiv = document.createElement('div');
            clusterDiv.className = 'cluster-container';

            const title = document.createElement('div');
            title.className = 'cluster-title';
            const count = cluster.reads.length;
            title.textContent = cluster.signature + ' (' + count + ' read' + (count !== 1 ? 's' : '') + ')';
            clusterDiv.appendChild(title);

            const vizArea = document.createElement('div');
            vizArea.className = 'viz-area';

            cluster.reads.forEach(read => {{
                const row = document.createElement('div');
                row.className = 'read-row';
                row.style.width = read.total_len + 'ch';
                row.style.marginLeft = '0'; // Everything is already offset

                read.hits.forEach((hit, idx) => {{
                    const block = document.createElement('div');
                    const colorIdx = idx % 6;
                    block.className = 'adapter-block color-' + colorIdx + ' ' + (hit.strand === 1 ? 'fwd' : 'rev');
                    block.style.left = hit.start + 'ch';
                    block.style.width = hit.len + 'ch';
                    block.onmouseover = (e) => showTooltip(e, hit, read.id);
                    block.onmouseout = hideTooltip;

                    row.appendChild(block);
                }});

                vizArea.appendChild(row);
            }});

            clusterDiv.appendChild(vizArea);
            container.appendChild(clusterDiv);
        }});

        function showTooltip(e, hit, readId) {{
            tooltip.style.display = 'block';
            tooltip.style.left = e.pageX + 10 + 'px';
            tooltip.style.top = e.pageY + 10 + 'px';
            const strandText = hit.strand === 1 ? 'Forward' : 'Reverse Complement';
            tooltip.innerHTML = `<strong>${{readId}}</strong><br>Adapter: ${{hit.name}} (${{strandText}})<br>Errors: ${{hit.errors}}`;
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
