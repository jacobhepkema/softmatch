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
            height: 20px;
            margin-top: 8px;
            border-top: 1px solid #f0f0f0;
        }}
        .index-tick {{
            position: absolute;
            top: 0;
            height: 4px;
            border-left: 1px solid #d1d5da;
        }}
        .index-label {{
            position: absolute;
            top: 6px;
            font-size: 10px;
            color: #959da5;
            transform: translateX(-50%);
            white-space: nowrap;
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

            // Build Annotation Layer
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
                    const tick = document.createElement('div');
                    tick.className = 'index-tick';
                    tick.style.left = `${{i + 0.5}}ch`;
                    indicesLayer.appendChild(tick);

                    const lbl = document.createElement('div');
                    lbl.className = 'index-label';
                    lbl.style.left = `${{i + 0.5}}ch`;
                    lbl.textContent = pos;
                    indicesLayer.appendChild(lbl);
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
