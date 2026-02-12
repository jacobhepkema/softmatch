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

            // Build Annotation HTML
            let annotHTML = '';

            read.hits.forEach((hit, idx) => {{
                const startCh = hit.start;
                const widthCh = hit.len;
                const topOffset = 10 + (idx % 3) * 12; // Stagger overlapping annotations

                // Color cycling
                const colors = ['#6d5dfc', '#fc5d5d', '#5dfca8', '#fcb05d'];
                const color = colors[idx % colors.length];
                const strandClass = hit.strand === 1 ? 'fwd' : 'rev';

                annotHTML += `<div class="annotation ${{strandClass}}" style="left:${{startCh}}ch; width:${{widthCh}}ch; top:${{topOffset}}px; background-color:${{color}}; --annot-color:${{color}};" onmouseover="showTooltip(event, '${{hit.name}}', ${{hit.errors}}, '${{hit.match_seq}}', ${{hit.strand}})" onmouseout="hideTooltip()"><div class="label" style="color:${{color}}">${{hit.name}}</div></div>`;
            }});

            div.innerHTML = `
                <div class="read-header">${{read.id}}</div>
                <div class="viz-wrapper"><div class="annotation-layer">${{annotHTML}}</div><div class="sequence-layer">${{read.seq}}</div></div>
            `;
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
