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
        :root {{
            --bg: #f5f7f9;
            --seq-bg: #ffffff;
            --header-text: #2c3e50;
            --muted-text: #7f8c8d;
            --border-color: #e1e4e8;
            --annot-color: #6d5dfc;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            padding: 40px 20px;
            color: #333;
            margin: 0;
        }}
        .container-wrapper {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ font-size: 24px; margin-bottom: 30px; color: var(--header-text); font-weight: 600; }}
        .read-container {{
            background: var(--seq-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 24px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            overflow-x: auto;
        }}
        .read-header {{
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 13px;
            margin-bottom: 16px;
            color: var(--muted-text);
            display: flex;
            align-items: center;
        }}
        .read-header::before {{
            content: 'ID:';
            font-weight: bold;
            margin-right: 8px;
            color: #bdc3c7;
            font-family: -apple-system, sans-serif;
        }}

        /* Benchling-like Visualization Wrapper */
        .viz-wrapper {{
            position: relative;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 15px;
            line-height: 1.6;
            padding: 45px 0 30px 0;
            display: inline-block;
            min-width: 100%;
        }}

        .sequence-layer {{
            color: #2c3e50;
            white-space: pre;
            position: relative;
            z-index: 2;
        }}

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
            height: 10px;
            background: var(--annot-color);
            border-radius: 3px;
            opacity: 0.75;
            cursor: pointer;
            pointer-events: auto;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 3;
        }}

        .annotation:hover {{
            opacity: 1;
            height: 14px;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        /* Arrow heads for direction */
        .annotation.fwd::after {{
            content: ''; position: absolute; right: -5px; top: -2px;
            border-top: 7px solid transparent; border-bottom: 7px solid transparent;
            border-left: 7px solid var(--annot-color);
        }}

        .annotation.rev::before {{
            content: ''; position: absolute; left: -5px; top: -2px;
            border-top: 7px solid transparent; border-bottom: 7px solid transparent;
            border-right: 7px solid var(--annot-color);
        }}

        .label {{
            position: absolute; top: -20px; font-size: 11px; color: var(--annot-color); font-weight: 700; white-space: nowrap;
            background: rgba(255,255,255,0.9);
            padding: 0 4px;
            border-radius: 3px;
        }}

        /* Indices (Benchling style) */
        .indices-layer {{
            position: relative;
            height: 24px;
            margin-top: 8px;
            border-top: 1px solid #f0f0f0;
        }}
        .index-group {{
            position: absolute;
            top: 0;
            transform: translateX(-50%);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .index-tick {{
            height: 4px;
            border-left: 1px solid #d1d5da;
        }}
        .index-label {{
            font-size: 10px;
            color: #959da5;
            white-space: nowrap;
            margin-top: 2px;
        }}

        .tooltip {{
            display: none;
            position: absolute;
            background: rgba(44, 62, 80, 0.95);
            color: #fff;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 12px;
            z-index: 1000;
            pointer-events: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            backdrop-filter: blur(4px);
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="container-wrapper">
        <h1>Softmatch Results <span style="font-weight:normal; font-size:15px; color:var(--muted-text); margin-left: 10px;">Top {len(data)} reads with hits</span></h1>
        <div id="tooltip" class="tooltip"></div>
        <div id="container"></div>
    </div>

    <script>
        const data = {json.dumps(data)};
        const container = document.getElementById('container');
        const tooltip = document.getElementById('tooltip');

        function escapeHTML(str) {{
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }}

        data.forEach(read => {{
            const div = document.createElement('div');
            div.className = 'read-container';

            // Create header
            const header = document.createElement('div');
            header.className = 'read-header';
            header.textContent = read.id;
            div.appendChild(header);
            // Create visualization wrapper
            const vizWrapper = document.createElement('div');
            vizWrapper.className = 'viz-wrapper';
            const annotLayer = document.createElement('div');
            annotLayer.className = 'annotation-layer';
            read.hits.forEach((hit, idx) => {{
                const startCh = hit.start;
                const widthCh = hit.len;
                const topOffset = 12 + (idx % 3) * 15;
                const colors = ['#6d5dfc', '#e74c3c', '#2ecc71', '#f39c12', '#3498db', '#9b59b6'];
                const color = colors[idx % colors.length];
                const strandClass = hit.strand === 1 ? 'fwd' : 'rev';

                const annot = document.createElement('div');
                annot.className = `annotation ${{strandClass}}`;
                annot.style.left = `${{startCh}}ch`;
                annot.style.width = `${{widthCh}}ch`;
                annot.style.top = `${{topOffset}}px`;
                annot.style.backgroundColor = color;
                annot.style.setProperty('--annot-color', color);
                const label = document.createElement('div');
                label.className = 'label';
                label.style.color = color;
                label.textContent = hit.name;
                annot.appendChild(label);

                annot.onmouseover = (e) => showTooltip(e, hit);
                annot.onmouseout = hideTooltip;

                annotLayer.appendChild(annot);
            }});
            vizWrapper.appendChild(annotLayer);

            // Sequence Layer
            const seqLayer = document.createElement('div');
            seqLayer.className = 'sequence-layer';
            seqLayer.textContent = read.seq;
            vizWrapper.appendChild(seqLayer);

            // Indices Layer
            const indicesLayer = document.createElement('div');
            indicesLayer.className = 'indices-layer';
            for (let i = 0; i < read.seq.length; i++) {{
                const pos = i + 1;
                if (pos === 1 || pos % 10 === 0) {{
                    const group = document.createElement('div');
                    group.className = 'index-group';
                    group.style.left = `${{i + 0.5}}ch`;

                    const tick = document.createElement('div');
                    tick.className = 'index-tick';
                    group.appendChild(tick);

                    const lbl = document.createElement('div');
                    lbl.className = 'index-label';
                    lbl.textContent = pos;
                    group.appendChild(lbl);

                    indicesLayer.appendChild(group);
                }}
            }}
            vizWrapper.appendChild(indicesLayer);

            div.appendChild(vizWrapper);
            container.appendChild(div);
        }});

        function showTooltip(e, hit) {{
            tooltip.style.display = 'block';
            tooltip.style.left = e.pageX + 10 + 'px';
            tooltip.style.top = e.pageY + 10 + 'px';
            const strandText = hit.strand === 1 ? 'Forward' : 'Reverse Complement';
            tooltip.innerHTML = `<strong>${{escapeHTML(hit.name)}}</strong> (${{strandText}})<br>Seq: ${{escapeHTML(hit.match_seq)}}<br>Errors: ${{hit.errors}}`;
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

            cluster_reads.append({
                'id': r['id'],
                'seq_len': r['seq_len'],
                'hits': r['hits'],
                'offset': offset
            })

        cluster_data.append({
            'signature': sig_name,
            'reads': cluster_reads,
            'max_width': max(r['seq_len'] + r['offset'] for r in cluster_reads)
        })

    # Sort clusters by abundance (descending)
    cluster_data.sort(key=lambda x: len(x['reads']), reverse=True)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Softmatch Cluster Visualization</title>
    <style>
        body {{ font-family: sans-serif; background: #f0f0f0; padding: 20px; --base-w: 0.25ch; }}
        .cluster-container {{ background: white; border-radius: 8px; padding: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .cluster-title {{ font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #444; border-bottom: 1px solid #eee; padding-bottom: 2px; }}

        .viz-area {{
            position: relative;
            font-family: monospace;
            font-size: 10px;
            overflow-x: auto;
            white-space: nowrap;
        }}

        .read-row {{
            position: relative;
            height: 4px;
            margin-bottom: 0px;
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
            border-top: 2px solid transparent; border-bottom: 2px solid transparent;
            border-left: 2px solid inherit;
            border-left-color: inherit;
        }}

        .adapter-block.rev::before {{
            content: ''; position: absolute; left: -2px; top: 0;
            border-top: 2px solid transparent; border-bottom: 2px solid transparent;
            border-right: 2px solid inherit;
            border-right-color: inherit;
        }}

        .tooltip {{
            display: none; position: absolute; background: #333; color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 12px; z-index: 100; pointer-events: none;
        }}

        #summary-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-size: 14px;
        }}

        #summary-table th, #summary-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}

        #summary-table th {{
            background-color: #f8f8f8;
            font-weight: bold;
            color: #555;
        }}

        #summary-table tr:hover {{
            background-color: #f1f1f1;
        }}

        #summary-table a {{
            color: #6d5dfc;
            text-decoration: none;
            font-weight: bold;
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

        /* Indices */
        .indices-layer {{
            position: relative;
            height: 20px;
            margin-top: 5px;
            border-top: 1px solid #eee;
        }}
        .index-group {{
            position: absolute;
            top: 0;
            transform: translateX(-50%);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .index-tick {{
            height: 4px;
            border-left: 1px solid #aaa;
        }}
        .index-label {{
            font-size: 8px;
            color: #888;
            white-space: nowrap;
            margin-top: 1px;
        }}
    </style>
</head>
<body>
    <h1>Clustered Read Summary</h1>
    <table id="summary-table">
        <thead>
            <tr>
                <th>Adapter Signature</th>
                <th>Read Count</th>
            </tr>
        </thead>
        <tbody id="summary-body"></tbody>
    </table>

    <div id="tooltip" class="tooltip"></div>
    <div id="container"></div>

    <script>
        const clusters = {json.dumps(cluster_data)};
        const container = document.getElementById('container');
        const summaryBody = document.getElementById('summary-body');
        const tooltip = document.getElementById('tooltip');

        clusters.forEach((cluster, clusterIdx) => {{
            const clusterId = 'cluster-' + clusterIdx;

            // Add to summary table
            const tr = document.createElement('tr');
            const tdSig = document.createElement('td');
            const a = document.createElement('a');
            a.href = '#' + clusterId;
            a.textContent = cluster.signature;
            tdSig.appendChild(a);

            const tdCount = document.createElement('td');
            tdCount.textContent = cluster.reads.length;

            tr.appendChild(tdSig);
            tr.appendChild(tdCount);
            summaryBody.appendChild(tr);

            const clusterDiv = document.createElement('div');
            clusterDiv.className = 'cluster-container';
            clusterDiv.id = clusterId;

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
                row.style.width = 'calc(' + read.seq_len + ' * var(--base-w))';
                row.style.marginLeft = 'calc(' + read.offset + ' * var(--base-w))';

                read.hits.forEach((hit, idx) => {{
                    const block = document.createElement('div');
                    const colorIdx = idx % 6;
                    block.className = 'adapter-block color-' + colorIdx + ' ' + (hit.strand === 1 ? 'fwd' : 'rev');
                    block.style.left = 'calc(' + hit.start + ' * var(--base-w))';
                    block.style.width = 'calc(' + hit.len + ' * var(--base-w))';
                    block.onmouseover = (e) => showTooltip(e, hit, read.id);
                    block.onmouseout = hideTooltip;

                    row.appendChild(block);
                }});

                vizArea.appendChild(row);
            }});

            // Indices Layer
            const indicesLayer = document.createElement('div');
            indicesLayer.className = 'indices-layer';
            indicesLayer.style.width = 'calc(' + cluster.max_width + ' * var(--base-w))';
            for (let i = 0; i < cluster.max_width; i++) {{
                const pos = i + 1;
                if (pos === 1 || pos % 50 === 0) {{
                    const group = document.createElement('div');
                    group.className = 'index-group';
                    group.style.left = 'calc(' + (i + 0.5) + ' * var(--base-w))';

                    const tick = document.createElement('div');
                    tick.className = 'index-tick';
                    group.appendChild(tick);

                    const lbl = document.createElement('div');
                    lbl.className = 'index-label';
                    lbl.textContent = pos;
                    group.appendChild(lbl);

                    indicesLayer.appendChild(group);
                }}
            }}
            vizArea.appendChild(indicesLayer);

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
