"""
Convert Jupyter notebooks to HTML pages for website.

From nbconvert repository.

https://github.com/jupyter/nbconvert
"""

import json
import html
from pathlib import Path
import re
import sys

# Configuration.
NOTEBOOKS = [
    {
        "file": "01a_weather_station_data_filtering.ipynb",
        "page_id": "04a_code_weather_stations",
        "nav_name": "1a. Weather Stations",
        "title": "Weather Station Data Filtering",
        "description": "Filtering NOAA GSOD data to extract NYC weather stations (Central Park & JFK)."
    },
    {
        "file": "01b_extreme_heat_days_filter.ipynb",
        "page_id": "04b_code_heat_classification",
        "nav_name": "1b. Heat Classification",
        "title": "Extreme Heat Days Classification",
        "description": "Classifying days as extreme heat (≥93°F) vs normal heat based on climatological thresholds."
    },
    {
        "file": "02_311_tract_daily.ipynb",
        "page_id": "04c_code_311_processing",
        "nav_name": "2. 311 Processing",
        "title": "NYC 311 Data Processing",
        "description": "Processing 311 service requests and aggregating QoL complaints by census tract."
    },
    {
        "file": "03_acs_tract.ipynb",
        "page_id": "04d_code_census_acs",
        "nav_name": "3. Census ACS",
        "title": "Census ACS Data Extraction",
        "description": "Extracting socioeconomic indicators from American Community Survey at tract level."
    },
    {
        "file": "04_additional_feature.ipynb",
        "page_id": "04e_code_additional_features",
        "nav_name": "4. Additional Features",
        "title": "Additional Feature Engineering",
        "description": "Computing POI density, subway distance, and other spatial accessibility metrics."
    },
    {
        "file": "05_nlcd_calculations.ipynb",
        "page_id": "04f_code_nlcd_rasters",
        "nav_name": "5. NLCD Rasters",
        "title": "NLCD Raster Calculations",
        "description": "Zonal statistics for tree canopy and impervious surface from NLCD data."
    },
    {
        "file": "06_data_merge_cleaning.ipynb",
        "page_id": "04g_code_data_merging",
        "nav_name": "6. Data Merging",
        "title": "Data Merging & Cleaning",
        "description": "Combining all datasets and preparing final analysis-ready table."
    },
    {
        "file": "07_ols_ml.ipynb",
        "page_id": "04i_code_ols_ml_shap",
        "nav_name": "8. OLS & ML + SHAP",
        "title": "OLS & ML Modeling with SHAP",
        "description": "OLS regression, Random Forest modeling, and SHAP interpretability analysis."
    },
    {
        "file": "eda.ipynb",
        "page_id": "04h_code_eda",
        "nav_name": "7. EDA",
        "title": "Exploratory Data Analysis",
        "description": "Visualizations and summary statistics of the merged dataset."
    },
]

# Conversion functions.
def escape_html(text):
    """Escape HTML special characters."""
    return html.escape(str(text))


def convert_markdown(md_text):
    """Convert markdown to HTML."""
    # Headers.
    md_text = re.sub(r'^#### (.+)$', r'<h6>\1</h6>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^### (.+)$', r'<h5>\1</h5>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^## (.+)$', r'<h4>\1</h4>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^# (.+)$', r'<h3>\1</h3>', md_text, flags=re.MULTILINE)
    
    # Bold and italic.
    md_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', md_text)
    md_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md_text)
    md_text = re.sub(r'__(.+?)__', r'<b>\1</b>', md_text)
    md_text = re.sub(r'_(.+?)_', r'<em>\1</em>', md_text)
    
    # Code.
    md_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', md_text)
    
    # Links.
    md_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', md_text)
    
    # Paragraphs.
    paragraphs = md_text.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p:
            if p.startswith('<h') or p.startswith('<ul') or p.startswith('<ol'):
                result.append(p)
            else:
                result.append(f'<p>{p}</p>')
    
    return '\n'.join(result)


def convert_outputs_with_figures(outputs):
    """Convert cell outputs to HTML with full figure support."""
    if not outputs:
        return '', 0
    
    html_parts = ['<div class="cell-outputs">']
    figure_count = 0
    
    for output in outputs:
        output_type = output.get('output_type', '')
        
        if output_type == 'stream':
            text = ''.join(output.get('text', []))
            if text.strip():
                if len(text) > 3000:
                    text = text[:3000] + '\n... [output truncated]'
                html_parts.append(f'<pre class="output-stream">{escape_html(text)}</pre>')
                
        elif output_type in ('execute_result', 'display_data'):
            data = output.get('data', {})
            
            # PNG images.
            if 'image/png' in data:
                img_data = data['image/png']
                figure_count += 1
                html_parts.append(f'''
<div class="output-figure">
    <img class="output-image" src="data:image/png;base64,{img_data}" alt="Figure {figure_count}" />
</div>''')
            # JPEG images.
            elif 'image/jpeg' in data:
                img_data = data['image/jpeg']
                figure_count += 1
                html_parts.append(f'''
<div class="output-figure">
    <img class="output-image" src="data:image/jpeg;base64,{img_data}" alt="Figure {figure_count}" />
</div>''')
            # SVG images.
            elif 'image/svg+xml' in data:
                svg_data = ''.join(data['image/svg+xml'])
                figure_count += 1
                html_parts.append(f'<div class="output-figure output-svg">{svg_data}</div>')
                
            # HTML (dataframes).
            elif 'text/html' in data:
                html_content = ''.join(data['text/html'])
                if len(html_content) > 50000:
                    html_parts.append('<div class="output-note">📋 <em>[Large table - see notebook]</em></div>')
                else:
                    html_parts.append(f'<div class="output-html">{html_content}</div>')
                
            # Plain text.
            elif 'text/plain' in data:
                text = ''.join(data['text/plain'])
                if len(text) > 2000:
                    text = text[:2000] + '\n... [truncated]'
                html_parts.append(f'<pre class="output-text">{escape_html(text)}</pre>')
                
        elif output_type == 'error':
            ename = output.get('ename', 'Error')
            evalue = output.get('evalue', '')
            html_parts.append(f'<pre class="output-error">{escape_html(ename)}: {escape_html(evalue)}</pre>')
    
    html_parts.append('</div>')
    has_content = len(html_parts) > 2
    return ('\n'.join(html_parts) if has_content else '', figure_count)


def convert_notebook_to_page(nb_path, notebook_info, all_notebooks):
    """Convert a notebook to a full HTML page fragment."""
    
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        return f'<div class="content-middle"><h1>Error</h1><p>{e}</p></div>'
    
    cells = nb.get('cells', [])
    html_parts = []
    cell_count = 0
    figure_count = 0
    
    for cell in cells:
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))
        
        if not source.strip():
            continue
            
        if cell_type == 'markdown':
            md_html = convert_markdown(source)
            html_parts.append(f'<div class="cell-markdown">{md_html}</div>')
            
        elif cell_type == 'code':
            cell_count += 1
            escaped_code = escape_html(source)
            outputs = cell.get('outputs', [])
            output_html, figs = convert_outputs_with_figures(outputs)
            figure_count += figs
            
            html_parts.append(f'''
<div class="cell-code-wrapper">
    <details class="code-fold">
        <summary class="code-fold-toggle">Code Cell {cell_count}</summary>
        <pre class="cell-code"><code>{escaped_code}</code></pre>
    </details>
    {output_html}
</div>
''')
    
    notebook_content = '\n'.join(html_parts)
    
    # Build sidebar navigation.
    nav_items = []
    current_idx = next((i for i, nb in enumerate(all_notebooks) if nb['file'] == notebook_info['file']), 0)
    
    for i, nb in enumerate(all_notebooks):
        is_current = nb['file'] == notebook_info['file']
        css_class = 'notebook-nav-current' if is_current else ''
        nav_items.append(f'<li class="{css_class}"><a href="#" data-page="{nb["page_id"]}">{nb["nav_name"]}</a></li>')
    
    nav_html = '\n'.join(nav_items)
    
    # Prev / Next navigation.
    prev_link = ""
    next_link = ""
    if current_idx > 0:
        prev_nb = all_notebooks[current_idx - 1]
        prev_link = f'<a href="#" data-page="{prev_nb["page_id"]}" class="notebook-prev">← {prev_nb["nav_name"]}</a>'
    if current_idx < len(all_notebooks) - 1:
        next_nb = all_notebooks[current_idx + 1]
        next_link = f'<a href="#" data-page="{next_nb["page_id"]}" class="notebook-next">{next_nb["nav_name"]} →</a>'
    
    # Full page
    page_html = f'''<div class="content-middle">
    <h1>CODE: {escape_html(notebook_info['title'])}</h1>
    <h2>Hot City, Heated Calls:<br>Understanding Extreme Heat and Quality of Life<br>Using New York City's 311 and SHAP</h2>
    
    <p class="notebook-description">{escape_html(notebook_info['description'])}</p>
    
    <div class="notebook-controls">
        <button onclick="toggleAllCode(true)" class="code-toggle-btn">Show All Code</button>
        <button onclick="toggleAllCode(false)" class="code-toggle-btn">Hide All Code</button>
    </div>
    
    <div class="notebook-nav-buttons">
        {prev_link}
        {next_link}
    </div>
    
    <div class="report-content notebook-content">
{notebook_content}
    </div>
    
    <div class="notebook-nav-buttons notebook-nav-bottom">
        {prev_link}
        {next_link}
    </div>
</div>

<div class="content-right">
    <div class="panel-right-content">
        <h2>Notebooks</h2>
        <ul class="notebook-nav-list">
            {nav_html}
        </ul>
        
        <h2>This Notebook</h2>
        <p><b>Source:</b> {escape_html(notebook_info['file'])}</p>
        <p><b>Code Cells:</b> {cell_count}</p>
        <p><b>Figures:</b> {figure_count}</p>
    </div>
    <div class="panel-right-footer">
        <h3>Data Pipeline</h3>
        <h5>Weather → 311 → Census → Features → Merge → EDA → Modeling</h5>
    </div>
</div>'''
    
    return page_html

# Main.
def main():
    # Determine paths.
    script_dir = Path(__file__).parent.resolve()
    
    # Look for notebooks/directory.
    notebooks_dir = script_dir / 'notebooks'
    if not notebooks_dir.exists():
        notebooks_dir = script_dir.parent / 'notebooks'
    if not notebooks_dir.exists():
        print(f"ERROR: Cannot find notebooks/ directory")
        print(f"Looked in: {script_dir / 'notebooks'}")
        print(f"       and: {script_dir.parent / 'notebooks'}")
        sys.exit(1)
    
    # Look for docs/pages/directory.
    pages_dir = script_dir / 'docs' / 'pages'
    if not pages_dir.exists():
        pages_dir = script_dir.parent / 'docs' / 'pages'
    if not pages_dir.exists():
        pages_dir = script_dir / 'pages'
    
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    print("Building notebook pages.")
    print(f"Notebooks Directory: {notebooks_dir}.")
    print(f"Output Directory: {pages_dir}.")
    print()
    
    success_count = 0
    total_size = 0
    
    for nb_info in NOTEBOOKS:
        nb_path = notebooks_dir / nb_info['file']
        
        if nb_path.exists():
            page_html = convert_notebook_to_page(nb_path, nb_info, NOTEBOOKS)
            output_path = pages_dir / f"{nb_info['page_id']}.html"
            output_path.write_text(page_html, encoding='utf-8')
            
            size_kb = output_path.stat().st_size / 1024
            total_size += size_kb
            success_count += 1
            print(f"{nb_info['page_id']}.html ({size_kb:.1f} KB).")
        else:
            print(f"NOT FOUND: {nb_info['file']}.")
    
    print()
    print(f"Converted {success_count}/{len(NOTEBOOKS)} notebooks.")
    print(f"Total Size: {total_size/1024:.2f} MB.")


if __name__ == '__main__':
    main()