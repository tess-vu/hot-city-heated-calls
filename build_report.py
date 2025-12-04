"""
Convert Project_Report.md to website HTML page fragments.

Modified from nbconvert repository.

https://github.com/jupyter/nbconvert
"""

import re
from pathlib import Path

# Configuration.

SECTION_MAPPING = {
    "1. INTRODUCTION": {
        "page_file": "01_introduction.html",
        "page_title": "INTRODUCTION",
        "right_panel": """
    <h2>Key Question</h2>
    <p>How do environmental, socioeconomic, and urban morphology factors influence quality of life in NYC during extreme heat weeks versus normal heat weeks?</p>
    
    <h2>Hypotheses</h2>
    <p>- QoL complaint rates rise with temperature.</p>
    <p>- SHAP values can reveal the key drivers of 311 complaints.</p>
    <p>- Different factors may become more important during extreme heat.</p>
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
    93°F is the extreme heat threshold based on 95th percentile of 1981–2010 climatological baseline.<br><br>
    - 5 extreme heat weeks<br>
    - 7 normal heat weeks<br><br>
    
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
    <b>Normal Heat</b>
    R²: 0.084<br><br>
    <b>Extreme Heat</b>
    R²: 0.088<br><br>
    
    <h3>Random Forest</h3>
    <b>Normal Heat</b>
    R²: 0.2738<br>
    RMSE: 0.1940<br>
    MAE: 0.1537<br><br>
    <b>Extreme Heat</b>
    R²: 0.2458<br>
    RMSE: 0.4149<br>
    MAE: 0.3129<br><br>
    
    <h2>Top SHAP Predictors</h2>
    <ol>
        <li>Average Height (AH)</li>
        <li>PCT_NON_WHITE</li>
        <li>NDVI</li>
        <li>KNN_SUBWAY_dist_mean</li><br>
    </ol>
"""
    },
    "4. DISCUSSION": {
        "page_file": "05_discussion.html",
        "page_title": "DISCUSSION",
        "right_panel": """
    <h2>Key Insights</h2>
    <p>Non-linear relationships are the rule rather than the exception for most urban features.</p>
    
    <h2>Notable Patterns</h2>
    <b>AH:</b> U-shaped relationship.<br><br>
    <b>PCT_NON_WHITE:</b> Inverted-U pattern.<br><br>
    <b>NDVI:</b> Linear negative (more green = fewer complaints).<br><br>
    <b>BD:</b> Changes from inverted-U to linear under extreme heat.<br><br>
    
    <h2>Limitations</h2>
    <p>- Single summer season (2025).</p>
    <p>- Approximately 25% variance explained suggests additional factors at play.</p>
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

# Image path configuration for GitHub Pages
# Images should be copied to docs/images/ folder
# From docs/pages/*.html, ../images/ resolves to docs/images/
IMAGE_PATH_PREFIX = "../images/"

# Note: You must copy your images to docs/images/:
#   cp -r notebooks/images/* docs/images/
# This makes images accessible from GitHub Pages which only serves docs/

# Conversion functions.
def convert_markdown_to_html(md_text):
    """Convert markdown to HTML with proper nested list support."""
    
    inline_codes = []
    def save_inline_code(match):
        inline_codes.append(match.group(1))
        return f'__INLINE_CODE_{len(inline_codes)-1}__'
    
    md_text = re.sub(r'`([^`]+)`', save_inline_code, md_text)
    
    # Process markdown line by line.
    lines = md_text.split('\n')
    html_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for headers.
        if line.startswith('#### '):
            html_lines.append(f'<h3>{line[5:]}</h3>')
            i += 1
            continue
        elif line.startswith('### '):
            html_lines.append(f'<h2>{line[4:]}</h2>')
            i += 1
            continue
        elif line.startswith('## '):
            html_lines.append(f'<h1>{line[3:]}</h1>')
            i += 1
            continue
        elif line.startswith('# '):
            # Skip h1 headers.
            i += 1
            continue
        
        # Check for image.
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        if img_match:
            alt_text = img_match.group(1)
            img_path = img_match.group(2)
            # Adjust path for website structure.
            # Original markdown: notebooks/images/EDA/file.png
            # Target: ../images/EDA/file.png (relative to docs/pages/)
            if img_path.startswith('notebooks/images/'):
                img_path = IMAGE_PATH_PREFIX + img_path[len('notebooks/images/'):]
            elif img_path.startswith('notebooks/'):
                img_path = IMAGE_PATH_PREFIX + img_path[len('notebooks/'):]
            # Process caption for italics.
            caption = process_inline_formatting(alt_text)
            # Clean alt text.
            clean_alt = re.sub(r'\*([^*]+)\*', r'\1', alt_text)
            html_lines.append(f'<figure><img class="report-image" src="{img_path}" alt="{clean_alt}"><figcaption>{caption}</figcaption></figure>')
            i += 1
            continue
        
        # Check for list start.
        list_match = re.match(r'^-\s+(.+)$', line)
        if list_match:
            # Collect list items.
            list_html, new_i = process_list(lines, i)
            html_lines.append(list_html)
            i = new_i
            continue
        
        # Regular paragraph or empty line.
        stripped = line.strip()
        if stripped:
            # Process inline formatting.
            processed = process_inline_formatting(stripped)
            html_lines.append(f'<p>{processed}</p>')
        
        i += 1
    
    # Join and restore inline codes.
    html = '\n'.join(html_lines)
    
    for idx, code in enumerate(inline_codes):
        html = html.replace(f'__INLINE_CODE_{idx}__', f'<code>{code}</code>')
    
    return html

def process_list(lines, start_idx):
    """Process a list starting at start_idx, handling nested lists properly."""
    html_parts = ['<ul>']
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        
        # Check for top-level list item.
        top_match = re.match(r'^-\s+(.+)$', line)
        if top_match:
            content = process_inline_formatting(top_match.group(1))
            
            # Look ahead for nested items.
            nested_items = []
            j = i + 1
            while j < len(lines):
                nested_match = re.match(r'^    -\s+(.+)$', lines[j])
                if nested_match:
                    nested_items.append(process_inline_formatting(nested_match.group(1)))
                    j += 1
                else:
                    break
            
            if nested_items:
                # Item with nested list.
                html_parts.append(f'<li>{content}')
                html_parts.append('<ul>')
                for nested in nested_items:
                    html_parts.append(f'<li>{nested}</li>')
                html_parts.append('</ul>')
                html_parts.append('</li>')
                i = j
            else:
                # Simple item.
                html_parts.append(f'<li>{content}</li>')
                i += 1
            continue
        
        # Check if still in list.
        if line.strip() == '':
            # Check if next line continues the list.
            if i + 1 < len(lines) and re.match(r'^-\s+', lines[i + 1]):
                i += 1
                continue
            else:
                # End of list.
                break
        elif re.match(r'^    -\s+', line):
            # Orphan nested item.
            i += 1
            continue
        else:
            # End list.
            break
    
    html_parts.append('</ul>')
    return '\n'.join(html_parts), i

def process_inline_formatting(text):
    """Process inline formatting: bold, italic, links."""
    # Bold.
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # Italic.
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    
    # Links.
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    return text

def split_markdown_by_sections(md_content):
    """Split markdown content by h1 headers."""
    pattern = r'^# (\d+\. .+)$'
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in md_content.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = match.group(1)
            current_content = []
        else:
            current_content.append(line)
    
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
    script_dir = Path(__file__).parent.resolve()
    
    # Look for Project_Report.md.
    report_path = script_dir / 'Project_Report.md'
    if not report_path.exists():
        report_path = script_dir.parent / 'Project_Report.md'
    if not report_path.exists():
        print(f"ERROR: Cannot find Project_Report.md")
        return
    
    # Look for docs/pages/.
    pages_dir = script_dir / 'docs' / 'pages'
    if not pages_dir.exists():
        pages_dir = script_dir.parent / 'docs' / 'pages'
    if not pages_dir.exists():
        pages_dir = script_dir / 'pages'
    
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    print("Building report pages from Project_Report.md.")
    print(f"Source: {report_path}")
    print(f"Output: {pages_dir}")
    print()
    
    # Read markdown.
    md_content = report_path.read_text(encoding='utf-8')
    
    # Remove YAML frontmatter.
    md_content = re.sub(r'^---\n.*?---\n', '', md_content, flags=re.DOTALL)
    
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
            content_html = convert_markdown_to_html(section_content)
            page_html = generate_page_html(
                config['page_title'],
                content_html,
                config['right_panel']
            )
            
            output_path = pages_dir / config['page_file']
            output_path.write_text(page_html, encoding='utf-8')
            
            size_kb = output_path.stat().st_size / 1024
            print(f"{config['page_file']} ({size_kb:.1f} KB).")
        else:
            print(f"Skipping unmapped section: {section_name}.")
    
    print()
    print("Updated report.")

if __name__ == '__main__':
    main()
