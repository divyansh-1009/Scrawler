"""
Complete Data Converter: scraped_data.json → scraped_data_analysis.md
Converts ALL scraped data to human-readable markdown format.
NO AI summaries - just comprehensive data presentation.
"""

import json
from datetime import datetime
from typing import Dict, Any


def json_to_markdown_complete(json_file: str = "scraped_data.json", 
                               output_file: str = "scraped_data_analysis.md"):
    """
    Convert scraped_data.json to complete human-readable markdown.
    Every single piece of data from JSON will be in the markdown.
    
    Args:
        json_file: Input JSON file path
        output_file: Output markdown file path
    """
    print("=" * 80)
    print("CONVERTING SCRAPED DATA TO HUMAN-READABLE FORMAT")
    print("=" * 80)
    print(f"\nInput: {json_file}")
    print(f"Output: {output_file}\n")
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    md = []
    
    # Header
    md.append("# Complete Web Crawling Data - Human-Readable Format\n")
    md.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md.append("---\n")
    
    # Crawl Summary
    md.append("## 📋 Crawl Summary\n")
    summary = data.get('crawl_summary', {})
    md.append(f"- **Total Pages Crawled**: {summary.get('total_pages', 0)}")
    md.append(f"- **Crawl Timestamp**: {summary.get('timestamp', 'N/A')}")
    md.append(f"- **URLs Visited**: {len(summary.get('urls_visited', []))}\n")
    
    # List all URLs visited
    urls = summary.get('urls_visited', [])
    if urls:
        md.append("### URLs Crawled\n")
        for i, url in enumerate(urls, 1):
            md.append(f"{i}. `{url}`")
        md.append("")
    
    md.append("---\n")
    
    # Process each page
    pages = data.get('pages', [])
    md.append(f"## 📄 Detailed Page Data ({len(pages)} pages)\n")
    
    for page_num, page in enumerate(pages, 1):
        md.append(f"### Page {page_num}\n")
        
        # Basic page info
        md.append("#### Basic Information\n")
        md.append(f"- **URL**: `{page.get('url', 'N/A')}`")
        md.append(f"- **Title**: {page.get('title', 'N/A')}")
        md.append(f"- **Description**: {page.get('description', 'N/A') or 'None'}")
        md.append(f"- **Timestamp**: {page.get('timestamp', 'N/A')}")
        md.append(f"- **Links Found**: {page.get('links_found', 0)}\n")
        
        # Metadata
        metadata = page.get('metadata', {})
        if metadata:
            md.append("#### Page Metadata\n")
            md.append("```json")
            md.append(json.dumps(metadata, indent=2, ensure_ascii=False))
            md.append("```\n")
        
        # Structured Data (if extracted)
        structured = page.get('structured_data', {})
        if structured:
            md.append("#### 🎯 Extracted Structured Data\n")
            
            page_type = structured.get('page_type', 'unknown')
            md.append(f"**Page Type**: {page_type}\n")
            
            # Products
            products = structured.get('products', [])
            if products:
                md.append(f"##### Products Found: {len(products)}\n")
                
                # Create table
                md.append("| # | Title | Price | Rating | Availability | Image |")
                md.append("|---|-------|-------|--------|--------------|-------|")
                
                for i, product in enumerate(products, 1):
                    title = product.get('title', 'N/A')[:50]
                    price = product.get('price', 'N/A')
                    rating = f"{product.get('rating', 'N/A')} ({product.get('rating_numeric', 'N/A')}/5)"
                    availability = product.get('availability', 'N/A')
                    has_image = '✓' if product.get('image_url') else '✗'
                    
                    md.append(f"| {i} | {title} | {price} | {rating} | {availability} | {has_image} |")
                
                md.append("")
                
                # Detailed product information
                md.append("##### Complete Product Details\n")
                
                for i, product in enumerate(products, 1):
                    md.append(f"###### Product {i}: {product.get('title', 'N/A')}\n")
                    
                    for key, value in product.items():
                        if key == 'title':
                            continue
                        md.append(f"- **{key.replace('_', ' ').title()}**: {value}")
                    
                    md.append("")
            
            # Categories
            categories = structured.get('categories', [])
            if categories:
                md.append(f"##### Categories Found: {len(categories)}\n")
                
                for i, cat in enumerate(categories, 1):
                    cat_name = cat.get('name', 'N/A')
                    cat_url = cat.get('url', 'N/A')
                    md.append(f"{i}. **{cat_name}** → `{cat_url}`")
                
                md.append("")
        
        # Markdown Content (if available)
        markdown_content = page.get('markdown_content', '')
        if markdown_content and len(markdown_content) > 100:
            md.append("#### 📝 Page Content (Markdown)\n")
            md.append("<details>")
            md.append("<summary>Click to expand full content</summary>\n")
            md.append("```markdown")
            md.append(markdown_content)
            md.append("```")
            md.append("</details>\n")
        
        # HTML Content (first 2000 chars preview)
        html_content = page.get('html_content', '')
        if html_content:
            md.append("#### 💻 HTML Content Preview\n")
            md.append("<details>")
            md.append("<summary>Click to expand HTML preview (first 2000 characters)</summary>\n")
            md.append("```html")
            md.append(html_content[:2000])
            if len(html_content) > 2000:
                md.append("\n... [truncated for readability] ...")
            md.append("```")
            md.append("</details>\n")
        
        md.append("---\n")
    
    # Summary Statistics (if structured data exists)
    all_products = []
    all_categories = set()
    
    for page in pages:
        structured = page.get('structured_data', {})
        if structured:
            products = structured.get('products', [])
            all_products.extend(products)
            
            categories = structured.get('categories', [])
            for cat in categories:
                all_categories.add(cat.get('name', ''))
    
    if all_products or all_categories:
        md.append("## 📊 Summary Statistics\n")
        
        if all_products:
            md.append(f"### Products Statistics (Total: {len(all_products)})\n")
            
            # Price analysis
            prices = []
            for p in all_products:
                price_str = p.get('price', '£0')
                try:
                    price_num = float(price_str.replace('£', '').replace('$', '').replace(',', ''))
                    prices.append(price_num)
                except:
                    pass
            
            if prices:
                md.append("#### Price Analysis")
                md.append(f"- **Total Products with Prices**: {len(prices)}")
                md.append(f"- **Minimum Price**: £{min(prices):.2f}")
                md.append(f"- **Maximum Price**: £{max(prices):.2f}")
                md.append(f"- **Average Price**: £{sum(prices)/len(prices):.2f}")
                md.append(f"- **Total Inventory Value**: £{sum(prices):.2f}\n")
            
            # Rating analysis
            ratings = [p.get('rating_numeric', 0) for p in all_products if 'rating_numeric' in p]
            if ratings:
                md.append("#### Rating Distribution")
                for star in [5, 4, 3, 2, 1]:
                    count = ratings.count(star)
                    if count > 0:
                        percentage = (count / len(ratings)) * 100
                        bar = '█' * int(percentage / 2)
                        md.append(f"- **{star} Stars**: {count} products ({percentage:.1f}%) {bar}")
                md.append(f"- **Average Rating**: {sum(ratings)/len(ratings):.2f} stars")
                md.append(f"- **Total Rated Products**: {len(ratings)}\n")
            
            # Availability
            available = sum(1 for p in all_products if 'In stock' in p.get('availability', ''))
            if available > 0 or len(all_products) > 0:
                md.append("#### Availability Status")
                md.append(f"- **In Stock**: {available} products")
                md.append(f"- **Other Status**: {len(all_products) - available} products\n")
        
        if all_categories:
            md.append(f"### Categories Statistics (Total: {len(all_categories)})\n")
            md.append("**All Unique Categories Found**:\n")
            for cat in sorted(all_categories):
                if cat:
                    md.append(f"- {cat}")
            md.append("")
    
    # Complete Raw Data Section
    md.append("---\n")
    md.append("## 🗂️ Complete Raw Data (JSON)\n")
    md.append("Below is the complete JSON data for reference:\n")
    md.append("<details>")
    md.append("<summary>Click to expand complete JSON data</summary>\n")
    md.append("```json")
    md.append(json.dumps(data, indent=2, ensure_ascii=False))
    md.append("```")
    md.append("</details>\n")
    
    # Footer
    md.append("---\n")
    md.append(f"**End of Report** - Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    
    # Statistics
    print("✓ Conversion complete!")
    print(f"\nContent included:")
    print(f"  ✓ Crawl summary with {len(urls)} URLs")
    print(f"  ✓ {len(pages)} pages with full details")
    print(f"  ✓ {len(all_products)} products extracted")
    print(f"  ✓ {len(all_categories)} unique categories")
    print(f"  ✓ All metadata and timestamps")
    print(f"  ✓ Markdown and HTML content")
    print(f"  ✓ Complete raw JSON included")
    print(f"\n✓ Output saved to: {output_file}")
    print("\nNOTE: Every piece of data from JSON is now in human-readable format!")


if __name__ == "__main__":
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "scraped_data.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "scraped_data_analysis.md"
    
    json_to_markdown_complete(json_file, output_file)
    
    print("\n✓ Done!")
