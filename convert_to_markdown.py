"""
Convert scraped_data.json to human-readable analysis report.
Focuses ONLY on extracted data relevant to the user's objective.
No metadata, no process details - just the extracted information.
"""

import json
from datetime import datetime
from typing import Dict, Any


def json_to_markdown_complete(json_file: str = "scraped_data.json", 
                               output_file: str = "scraped_data_analysis.md"):
    """
    Convert scraped data to comprehensive human-readable report.
    Focus only on extracted content, not crawl process or metadata.
    
    Args:
        json_file: Input JSON file path
        output_file: Output markdown file path
    """
    print("=" * 80)
    print("CONVERTING TO HUMAN-READABLE ANALYSIS")
    print("=" * 80)
    print(f"\nInput: {json_file}")
    print(f"Output: {output_file}\n")
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    md = []
    
    # Header
    md.append("# Extracted Data Analysis Report\n")
    md.append(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
    
    # Objective
    objective = data.get('objective', 'Not specified')
    md.append(f"**Search Objective**: {objective}\n")
    md.append("---\n")
    
    # Get all extracted data
    extracted_data = data.get('extracted_data', [])
    
    if not extracted_data:
        md.append("## No Data Extracted\n")
        md.append("No relevant information was found matching the objective.\n")
    else:
        md.append(f"## Summary\n")
        md.append(f"Found {len(extracted_data)} pages with relevant information.\n\n")
        md.append("---\n")
        
        # Process each page's extracted content
        for idx, page_data in enumerate(extracted_data, 1):
            url = page_data.get('url', 'Unknown URL')
            content = page_data.get('extracted_content', {})
            relevance = page_data.get('relevance', 0)
            
            if not content or content == {}:
                continue
            
            md.append(f"\n## Source {idx}\n")
            md.append(f"**Relevance Score**: {relevance}/10\n\n")
            
            # Recursively format the extracted content
            md.extend(_format_content(content, level=3))
            
            md.append(f"\n**Source URL**: {url}\n")
            md.append("\n---\n")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    
    # Statistics
    print("✓ Conversion complete!")
    print(f"\nReport includes:")
    print(f"  ✓ Objective: {objective}")
    print(f"  ✓ Sources analyzed: {len(extracted_data)}")
    print(f"\n✓ Output saved to: {output_file}")
    
    return output_file


def _format_content(content: Any, level: int = 3) -> list:
    """
    Recursively format extracted content into readable markdown.
    
    Args:
        content: The content to format (dict, list, or primitive)
        level: Header level for nested structures
        
    Returns:
        List of markdown lines
    """
    lines = []
    
    if isinstance(content, dict):
        for key, value in content.items():
            # Format the key as a readable title
            title = key.replace('_', ' ').title()
            
            if isinstance(value, (dict, list)):
                lines.append(f"{'#' * level} {title}\n")
                lines.extend(_format_content(value, level + 1))
            else:
                lines.append(f"**{title}**: {value}\n")
    
    elif isinstance(content, list):
        if not content:
            lines.append("*No items found*\n")
        elif all(isinstance(item, dict) for item in content):
            # List of objects - format as numbered items
            for idx, item in enumerate(content, 1):
                lines.append(f"\n### Item {idx}\n")
                lines.extend(_format_content(item, level + 1))
        else:
            # Simple list
            for item in content:
                if isinstance(item, str):
                    lines.append(f"- {item}\n")
                else:
                    lines.append(f"- {str(item)}\n")
    
    else:
        # Primitive value
        lines.append(f"{content}\n")
    
    return lines


if __name__ == "__main__":
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "scraped_data.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "scraped_data_analysis.md"
    
    json_to_markdown_complete(json_file, output_file)
    
    print("\n✓ Done! Your data is now in human-readable format!")
