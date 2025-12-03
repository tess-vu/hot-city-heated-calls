#!/usr/bin/env python3
"""
Convert Project_Report.md to website HTML page fragments.

Adjusted from nbconvert repository.

https://github.com/jupyter/nbconvert
"""

import re
from pathlib import Path

# Configuration.

# Define how markdown sections map to HTML pages.
SECTION_MAPPING = {
    "1. INTRODUCTION": {
        "page_file": "01_introduction.html",
        "page_title": "INTRODUCTION",
        "right_panel": """
    <h2>Key Question</h2>
    <p>How do environmental, socioeconomic, and urban morphology factors influence quality of life in NYC during extreme heat weeks versus normal heat weeks?</p>
    
    <h2>Hypotheses</h2>
    - QoL complaint rates rise with temperature.<br><br>
    - SHAP values can reveal the key drivers of 311 complaints.<br><br>
    - Different factors may become more important during extreme heat.
"""
    },
    "2. DATA and METHODS": {
        "page_file": "02_data_and_methods.html",
        "page_title": "DATA & METHODS",
        "right_panel": """
    <h2>Study Parameters</h2>
    <b>Location:</b> New York City<br><br>
    <b>Spatial Resolution:</b> Census tract level<br><br>
    <b>Time Period:</b> Summer 2025 (June–August 23)<br><br>
    <b>Temporal Resolution:</b> Weekly<br><br>
    
    <h2>Heat Thresholds</h2>
    <b>93°F</b> is the extreme heat threshold based on 95th percentile of 1981–2010 climatological baseline.<br>
    <br>- 5 extreme heat weeks
    <br>- 7 normal heat weeks<br><br>
    
    <h2>Data Sources</h2>
    - NOAA (temperature)<br>
    - ACS 2023 (socioeconomic)<br>
    - Landsat (environmental / urban)<br>
    - OpenStreetMap (POIs / kNN / urban)
"""
    },
    "3. RESULTS": {
        "page_file": "03_results.html",
        "page_title": "RESULTS",
        "right_panel": """
    <h2>Model Performance</h2>
    
    <h3>OLS Models</h3>
    - Normal Heat R²: <b>0.084</b>
    <br>- Extreme Heat R²: <b>0.088</b><br>
    
    <h3>Random Forest</h3>
    - Normal Heat R²: <b>0.274</b>
    <br>- Extreme Heat R²: <b>0.246</b><br>
    
    <h2>Top SHAP Predictors</h2>
    <ol>
        <li>Average Height (AH)</li>
        <li>PCT_NON_WHITE</li>
        <li>NDVI</li>
        <li>KNN_SUBWAY_dist_mean</li><br>
    </ol>
    
    <h2>Key Findings</h2>
    <p>Water Coverage Ratio (WCR) increases in importance during extreme heat weeks, while physical morphology variables decrease.</p>
"""
    },
    "4. DISCUSSION": {
        "page_file": "05_discussion.html",
        "page_title": "DISCUSSION",
        "right_panel": """
    <h2>Key Insights</h2>
    <p>Non-linear relationships are the rule rather than the exception for most urban features.</p>
    
    <h2>Notable Patterns</h2>
    - <b>AH:</b> U-shaped relationship<br><br>
    - <b>PCT_NON_WHITE:</b> Inverted-U pattern<br><br>
    - <b>NDVI:</b> Linear negative (more green = fewer complaints)<br><br>
    - <b>BD:</b> Changes from inverted-U to linear under extreme heat
    
    <h2>Limitations</h2>
    <p>Single summer season (2025); ~25% variance explained suggests additional factors at play.</p>
"""
    },
    "5. REFERENCES": {
        "page_file": "06_references.html",
        "page_title": "REFERENCES",
        "right_panel": """
    <h2>Citation Info</h2>
    <p>All references follow APA 7th edition format.</p>
"""
    }
}

# Conversion.

def convert_markdown_to_html(md_text):
    """Convert markdown text to HTML."""
    html = md_text
    
    # Remove YAML frontmatter.
    html = re.sub(r'^---\n.*?---\n', '', html, flags=re.DOTALL)
    
    # Headers (process in order from h4 to h2 to avoid conflicts).
    html = re.sub(r'^#### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    # Don't convert h1 - we'll use those for section splitting.
    
    # Bold and italic.
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
    html = re.sub(r'_([^_]+)_', r'<em>\1</em>', html)
    
    # Inline code.
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Links.
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
    
    # Images.
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img class="report-image" src="\2" alt="\1">', html)
    
    # Unordered lists.
    def convert_ul(match):
        items = match.group(0)
        # Split by lines starting with -
        lines = items.strip().split('\n')
        result = ['<ul>']
        current_item = []
        indent_level = 0
        
        for line in lines:
            if line.strip().startswith('- '):
                if current_item:
                    result.append('<li>' + ' '.join(current_item) + '</li>')
                current_item = [line.strip()[2:]]
            elif line.strip().startswith('  - '):
                # Nested item
                if current_item:
                    result.append('<li>' + ' '.join(current_item))
                    result.append('<ul><li>' + line.strip()[4:] + '</li></ul></li>')
                    current_item = []
            elif line.strip():
                current_item.append(line.strip())
        
        if current_item:
            result.append('<li>' + ' '.join(current_item) + '</li>')
        
        result.append('</ul>')
        return '\n'.join(result)
    
    # Simple list conversion.
    html = re.sub(r'((?:^- .+\n?)+)', convert_ul, html, flags=re.MULTILINE)
    
    # Convert remaining lines to paragraphs.
    lines = html.split('\n\n')
    processed = []
    for block in lines:
        block = block.strip()
        if not block:
            continue
        # Don't wrap if already has HTML tags.
        if block.startswith('<') or block.startswith('#'):
            processed.append(block)
        else:
            # Wrap in paragraph.
            processed.append(f'<p>{block}</p>')
    
    html = '\n'.join(processed)
    
    # Clean up any remaining # headers.
    html = re.sub(r'^# .+$', '', html, flags=re.MULTILINE)
    
    return html.strip()


def split_markdown_by_sections(md_content):
    """Split markdown content by h1 headers."""
    # Pattern to match h1 headers.
    pattern = r'^# (\d+\. .+)$'
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in md_content.split('\n'):
        match = re.match(pattern, line)
        if match:
            # Save previous section.
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = match.group(1)
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section.
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def generate_page_html(title, content_html, right_panel_html):
    """Generate full page HTML fragment."""
    return f'''<div class="content-middle">
    <h1>{title}</h1>
    <h2>Hot City, Heated Calls:<br>Understanding Extreme Heat and Quality of Life<br>Using New York City's 311 and SHAP</h2>
    
    <div class="report-content">
{content_html}
    </div>
</div>

<div class="content-right">
{right_panel_html}
</div>'''


# Main.

def main():
    # Find paths.
    script_dir = Path(__file__).parent.resolve()
    
    # Look for Project_Report.md.
    report_path = script_dir / 'Project_Report.md'
    if not report_path.exists():
        report_path = script_dir.parent / 'Project_Report.md'
    if not report_path.exists():
        print(f"ERROR: Cannot find Project_Report.md")
        print(f"Looked in: {script_dir}")
        print(f"       and: {script_dir.parent}")
        return
    
    # Look for docs/pages/.
    pages_dir = script_dir / 'docs' / 'pages'
    if not pages_dir.exists():
        pages_dir = script_dir.parent / 'docs' / 'pages'
    if not pages_dir.exists():
        pages_dir = script_dir / 'pages'
    
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Building report pages from Project_Report.md")
    print("=" * 60)
    print(f"Source: {report_path}")
    print(f"Output: {pages_dir}")
    print()
    
    # Read markdown.
    md_content = report_path.read_text(encoding='utf-8')
    
    # Split into sections.
    sections = split_markdown_by_sections(md_content)
    
    print(f"Found {len(sections)} sections:")
    for section_name in sections:
        print(f"  - {section_name}")
    print()
    
    # Generate pages.
    for section_name, section_content in sections.items():
        if section_name in SECTION_MAPPING:
            config = SECTION_MAPPING[section_name]
            
            # Convert markdown to HTML.
            content_html = convert_markdown_to_html(section_content)
            
            # Generate page.
            page_html = generate_page_html(
                config['page_title'],
                content_html,
                config['right_panel']
            )
            
            # Write file.
            output_path = pages_dir / config['page_file']
            output_path.write_text(page_html, encoding='utf-8')
            
            size_kb = output_path.stat().st_size / 1024
            print(f"{config['page_file']} ({size_kb:.1f} KB).")
        else:
            print(f"Skipping unmapped section: {section_name}.")
    
    print()
    print("Pages updated.")

if __name__ == '__main__':
    main()
