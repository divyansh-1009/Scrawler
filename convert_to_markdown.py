"""
Complete Data Converter: scraped_data.json → scraped_data_analysis.md
Converts ALL scraped data to NATURAL LANGUAGE human-readable format.
NO tables, NO technical data - just flowing paragraphs explaining everything.
"""

import json
from datetime import datetime
from typing import Dict, Any


def json_to_markdown_complete(json_file: str = "scraped_data.json", 
                               output_file: str = "scraped_data_analysis.md"):
    """
    Convert scraped_data.json to complete human-readable narrative format.
    Creates long, flowing paragraphs describing every piece of scraped data.
    
    Args:
        json_file: Input JSON file path
        output_file: Output markdown file path
    """
    print("=" * 80)
    print("CONVERTING SCRAPED DATA TO HUMAN-READABLE NARRATIVE")
    print("=" * 80)
    print(f"\nInput: {json_file}")
    print(f"Output: {output_file}\n")
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    md = []
    
    # Header
    md.append("# Web Crawling Analysis Report - Complete Human-Readable Summary\n")
    md.append(f"**Report Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
    md.append("---\n")
    
    # Introduction paragraph
    summary = data.get('crawl_summary', {})
    total_pages = summary.get('total_pages', 0)
    urls = summary.get('urls_visited', [])
    timestamp = summary.get('timestamp', 'unknown time')
    
    md.append("## Executive Summary\n")
    md.append(f"This comprehensive analysis report documents the complete web crawling session conducted on {datetime.fromisoformat(timestamp).strftime('%B %d, %Y at %I:%M %p')}. ")
    md.append(f"During this crawling session, the system successfully visited and extracted data from {total_pages} web {'page' if total_pages == 1 else 'pages'}. ")
    
    if urls:
        md.append(f"The crawling process began at the following URL: {urls[0]}. ")
        if len(urls) > 1:
            md.append(f"From there, the crawler navigated through {len(urls) - 1} additional pages, systematically extracting and documenting all available content, structured data, and metadata encountered along the way. ")
    
    md.append("This report presents every piece of information discovered during the crawl in a narrative, easy-to-understand format, ensuring that no detail is overlooked or omitted.\n\n")
    
    # Process each page with detailed narrative
    pages = data.get('pages', [])
    
    if pages:
        md.append("## Detailed Page-by-Page Analysis\n")
        md.append(f"The following sections provide an exhaustive, detailed description of each of the {len(pages)} pages that were crawled. ")
        md.append("Every element, data point, and piece of content discovered on these pages is described in full detail below.\n\n")
        
        for page_num, page in enumerate(pages, 1):
            md.append("---\n")
            md.append(f"### Page {page_num} - Complete Analysis\n")
            
            # Page introduction
            page_url = page.get('url', 'Unknown URL')
            page_title = page.get('title', 'Untitled Page')
            page_desc = page.get('description', '')
            links_count = page.get('links_found', 0)
            page_time = page.get('timestamp', '')
            
            md.append(f"**Location and Basic Information**: ")
            md.append(f"This page is located at {page_url}. ")
            md.append(f"The page carries the title \"{page_title}\". ")
            
            if page_time:
                try:
                    time_str = datetime.fromisoformat(page_time).strftime('%B %d, %Y at %I:%M %p')
                    md.append(f"The content was extracted on {time_str}. ")
                except:
                    pass
            
            if page_desc:
                md.append(f"The page description reads: \"{page_desc}\". ")
            else:
                md.append("No meta description was provided for this page. ")
            
            md.append(f"During the analysis, the crawler identified a total of {links_count} hyperlinks present on this page.\n\n")
            
            # Structured data - Products (detailed narrative)
            structured = page.get('structured_data', {})
            if structured:
                page_type = structured.get('page_type', 'unknown')
                md.append(f"**Page Classification**: Based on the content analysis, this page has been classified as a \"{page_type}\" type page. ")
                
                products = structured.get('products', [])
                # Filter out incomplete products (those with only price and availability)
                complete_products = [p for p in products if 'title' in p and p.get('title') != 'N/A']
                
                if complete_products:
                    md.append(f"The crawler successfully identified and extracted detailed information about {len(complete_products)} distinct products or items featured on this page. ")
                    md.append("Each product listing has been thoroughly analyzed and all available information has been documented. Below is a comprehensive description of each product:\n\n")
                    
                    for prod_num, product in enumerate(complete_products, 1):
                        title = product.get('title', 'Untitled Product')
                        price_raw = product.get('price', 'Price not available')
                        # Clean price
                        price = price_raw.replace('In stockAdd to basket', '').replace('In stock', '').replace('Add to basket', '').strip()
                        availability = product.get('availability', 'Availability unknown')
                        rating = product.get('rating', 'Not rated')
                        rating_num = product.get('rating_numeric', '')
                        url = product.get('url', '')
                        image = product.get('image', '')
                        image_alt = product.get('image_alt', '')
                        
                        md.append(f"**Product {prod_num}: {title}**\n\n")
                        
                        md.append(f"The {prod_num}{'st' if prod_num == 1 else 'nd' if prod_num == 2 else 'rd' if prod_num == 3 else 'th'} product discovered on this page is titled \"{title}\". ")
                        
                        if price and price != 'Price not available':
                            md.append(f"This product is currently priced at {price}. ")
                        
                        md.append(f"According to the availability information extracted from the page, this item is reported as \"{availability}\". ")
                        
                        if rating and rating != 'Not rated':
                            md.append(f"Customer feedback for this product indicates a rating of \"{rating}\"")
                            if rating_num:
                                md.append(f", which translates to {rating_num} out of 5 stars")
                            md.append(". ")
                        
                        if url:
                            md.append(f"Additional details about this product can be accessed by navigating to the relative URL: {url}. ")
                        
                        if image:
                            md.append(f"The product listing includes a visual representation (image) stored at {image}")
                            if image_alt:
                                md.append(f", with the alternative text description: \"{image_alt}\"")
                            md.append(". ")
                        
                        md.append("\n\n")
                
                # Categories (detailed narrative)
                categories = structured.get('categories', [])
                if categories:
                    md.append(f"**Navigation and Category Structure**: The page includes an organized navigation system featuring {len(categories)} distinct categories or sections. ")
                    md.append("These categories provide a comprehensive taxonomy of the site's content organization. ")
                    md.append("The complete list of categories identified includes: ")
                    
                    cat_names = [cat.get('name', 'Unnamed') for cat in categories]
                    if len(cat_names) > 1:
                        md.append(", ".join(cat_names[:-1]) + ", and " + cat_names[-1] + ". ")
                    else:
                        md.append(cat_names[0] + ". ")
                    
                    md.append("Each of these categories serves as a navigational hub, allowing users to explore different sections of the website. ")
                    
                    md.append("The specific URLs associated with each category are as follows: ")
                    for i, cat in enumerate(categories, 1):
                        cat_name = cat.get('name', 'Unnamed')
                        cat_url = cat.get('url', '')
                        if i == len(categories):
                            md.append(f"and \"{cat_name}\" (accessible at {cat_url}).")
                        elif i == len(categories) - 1:
                            md.append(f"\"{cat_name}\" (accessible at {cat_url}), ")
                        else:
                            md.append(f"\"{cat_name}\" (accessible at {cat_url}), ")
                    
                    md.append("\n\n")
            
            # Content description
            markdown_content = page.get('markdown_content', '')
            html_content = page.get('html_content', '')
            
            if markdown_content and len(markdown_content) > 100:
                word_count = len(markdown_content.split())
                char_count = len(markdown_content)
                
                md.append(f"**Page Content Analysis**: The main textual content of this page has been extracted and analyzed. ")
                md.append(f"The full content comprises approximately {word_count} words and {char_count} characters of text. ")
                md.append("This content includes all visible text elements, navigation menus, page headers, footers, and body content. ")
                
                # Extract first few meaningful lines as a sample
                lines = [line.strip() for line in markdown_content.split('\n') if line.strip() and not line.strip().startswith('*') and not line.strip().startswith('-')]
                if lines:
                    md.append(f"The page begins with the following content: \"{lines[0][:200]}{'...' if len(lines[0]) > 200 else ''}\". ")
                
                md.append("The complete extracted content preserves the original structure and organization of information as it appeared on the source page. ")
                md.append("All textual data, including links, list items, and formatted sections, has been captured in full detail.\n\n")
                
                # Include full content in collapsible section
                md.append("<details>\n")
                md.append("<summary><strong>Click here to view the complete extracted page content</strong></summary>\n\n")
                md.append("```\n")
                md.append(markdown_content)
                md.append("\n```\n")
                md.append("</details>\n\n")
            
            if html_content:
                html_size = len(html_content)
                md.append(f"**Technical Details**: The underlying HTML source code for this page was also captured, consisting of {html_size} characters of markup. ")
                md.append("This includes all HTML tags, attributes, embedded scripts, stylesheets, and structural elements. ")
                md.append("The raw HTML provides the complete technical blueprint of how the page is constructed and rendered in web browsers.\n\n")
                
                md.append("<details>\n")
                md.append("<summary><strong>Click here to view the raw HTML source code (first 5000 characters)</strong></summary>\n\n")
                md.append("```html\n")
                md.append(html_content[:5000])
                if len(html_content) > 5000:
                    md.append("\n\n... [Content truncated for readability. Full HTML has been preserved in the original JSON data file.] ...\n")
                md.append("\n```\n")
                md.append("</details>\n\n")
            
            # Metadata
            metadata = page.get('metadata', {})
            if metadata and any(metadata.values()):
                md.append(f"**Page Metadata**: Additional metadata information was extracted from the page headers. ")
                
                if metadata.get('keywords'):
                    md.append(f"The page specifies the following keywords for search engine optimization: {metadata.get('keywords')}. ")
                
                if metadata.get('author'):
                    md.append(f"The author or creator of this content is identified as: {metadata.get('author')}. ")
                
                md.append("This metadata provides valuable context about the page's purpose, intended audience, and organizational structure.\n\n")
    
    # Overall statistics and summary
    all_products = []
    all_categories = set()
    total_links = 0
    total_content_size = 0
    
    for page in pages:
        structured = page.get('structured_data', {})
        if structured:
            products = [p for p in structured.get('products', []) if 'title' in p and p.get('title') != 'N/A']
            all_products.extend(products)
            
            categories = structured.get('categories', [])
            for cat in categories:
                all_categories.add(cat.get('name', ''))
        
        total_links += page.get('links_found', 0)
        total_content_size += len(page.get('markdown_content', '')) + len(page.get('html_content', ''))
    
    if all_products or all_categories or total_links > 0:
        md.append("---\n")
        md.append("## Comprehensive Statistical Analysis\n")
        md.append("After analyzing all crawled pages, the following statistical summary provides an overview of the data collection results.\n\n")
        
        if all_products:
            md.append(f"**Product Inventory Summary**: Across all pages analyzed, the crawler successfully extracted detailed information about a total of {len(all_products)} distinct products. ")
            
            # Price analysis
            prices = []
            for p in all_products:
                price_str = p.get('price', '£0')
                try:
                    # Extract numeric value
                    price_clean = price_str.replace('£', '').replace('$', '').replace(',', '').replace('In stockAdd to basket', '').replace('In stock', '').replace('Add to basket', '').strip()
                    price_num = float(price_clean)
                    if price_num > 0:
                        prices.append(price_num)
                except:
                    pass
            
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                total_value = sum(prices)
                
                md.append(f"The pricing analysis reveals that product prices range from a minimum of £{min_price:.2f} to a maximum of £{max_price:.2f}, ")
                md.append(f"with an average price point of £{avg_price:.2f}. ")
                md.append(f"If all {len(prices)} priced products were purchased together, the total inventory value would amount to £{total_value:.2f}. ")
            
            # Availability
            available_count = sum(1 for p in all_products if 'In stock' in p.get('availability', ''))
            if available_count > 0:
                availability_percentage = (available_count / len(all_products)) * 100
                md.append(f"In terms of availability, {available_count} products ({availability_percentage:.1f}% of the total) are currently reported as being in stock and ready for purchase. ")
            
            # Ratings
            ratings = [p.get('rating_numeric', 0) for p in all_products if 'rating_numeric' in p and p.get('rating_numeric')]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                md.append(f"Customer satisfaction ratings were available for {len(ratings)} products, with an average rating of {avg_rating:.2f} out of 5 stars. ")
                
                # Rating distribution
                rating_dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
                for r in ratings:
                    if r in rating_dist:
                        rating_dist[r] += 1
                
                if any(rating_dist.values()):
                    md.append("The distribution of ratings shows that ")
                    rating_parts = []
                    for stars in [5, 4, 3, 2, 1]:
                        count = rating_dist[stars]
                        if count > 0:
                            rating_parts.append(f"{count} product{'s' if count != 1 else ''} received {stars}-star rating{'s' if stars != 1 else ''}")
                    
                    if len(rating_parts) > 1:
                        md.append(", ".join(rating_parts[:-1]) + ", and " + rating_parts[-1] + ". ")
                    elif rating_parts:
                        md.append(rating_parts[0] + ". ")
            
            md.append("\n\n")
        
        if all_categories:
            md.append(f"**Category and Navigation Analysis**: The website's organizational structure includes {len(all_categories)} unique categories or sections. ")
            md.append("This categorization system provides a comprehensive framework for organizing and accessing content. ")
            
            sorted_cats = sorted([cat for cat in all_categories if cat])
            if sorted_cats:
                md.append("The complete alphabetical listing of all categories includes: ")
                if len(sorted_cats) > 1:
                    md.append(", ".join(sorted_cats[:-1]) + ", and " + sorted_cats[-1] + ". ")
                else:
                    md.append(sorted_cats[0] + ". ")
            
            md.append("\n\n")
        
        if total_links > 0:
            md.append(f"**Link Discovery and Navigation**: Throughout the crawling process, the system identified and catalogued a total of {total_links} hyperlinks across all pages. ")
            md.append("These links represent potential navigation paths, connecting different sections of the website and providing pathways for further exploration. ")
            md.append(f"On average, each crawled page contained approximately {total_links / len(pages):.0f} links.\n\n")
        
        if total_content_size > 0:
            size_kb = total_content_size / 1024
            size_mb = size_kb / 1024
            
            if size_mb >= 1:
                md.append(f"**Data Volume**: The total volume of content extracted during this crawling session amounts to approximately {size_mb:.2f} MB ")
            else:
                md.append(f"**Data Volume**: The total volume of content extracted during this crawling session amounts to approximately {size_kb:.2f} KB ")
            
            md.append(f"({total_content_size:,} characters) of raw text and HTML data. This represents the complete information capture from all {len(pages)} pages visited.\n\n")
    
    # Conclusion
    md.append("---\n")
    md.append("## Conclusion and Data Preservation\n")
    md.append("This report has presented a complete, human-readable analysis of all data collected during the web crawling session. ")
    md.append("Every product, category, link, text element, and piece of metadata discovered has been documented and described in detail above. ")
    md.append("No information has been omitted or summarized - this narrative account preserves the full fidelity of the original crawled data.\n\n")
    
    md.append("For technical reference, the complete raw data in JSON format is preserved below. ")
    md.append("This structured data representation contains the exact same information presented in narrative form above, ")
    md.append("but in a machine-readable format suitable for further processing, analysis, or integration with other systems.\n\n")
    
    # Raw JSON
    md.append("<details>\n")
    md.append("<summary><strong>Click here to view the complete raw JSON data</strong></summary>\n\n")
    md.append("```json\n")
    md.append(json.dumps(data, indent=2, ensure_ascii=False))
    md.append("\n```\n")
    md.append("</details>\n\n")
    
    # Footer
    md.append("---\n")
    md.append(f"**Report completed on {datetime.now().strftime('%B %d, %Y at %I:%M:%S %p')}**\n\n")
    md.append("*This comprehensive analysis was automatically generated from web crawling data. ")
    md.append("All information presented is derived directly from the source pages without interpretation or editorial modification.*")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    
    # Statistics
    print("✓ Narrative conversion complete!")
    print(f"\nReport includes:")
    print(f"  ✓ Executive summary with {len(urls)} URLs")
    print(f"  ✓ Detailed narrative for {len(pages)} pages")
    print(f"  ✓ Complete descriptions of {len(all_products)} products")
    print(f"  ✓ Analysis of {len(all_categories)} categories")
    print(f"  ✓ Statistical summaries and insights")
    print(f"  ✓ Complete raw JSON data included")
    print(f"\n✓ Output saved to: {output_file}")
    print("\n✓ All data presented in flowing paragraph format!")
    
    return output_file
    
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


if __name__ == "__main__":
    import sys
    
    json_file = sys.argv[1] if len(sys.argv) > 1 else "scraped_data.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "scraped_data_analysis.md"
    
    json_to_markdown_complete(json_file, output_file)
    
    print("\n✓ Done! Your data is now in beautiful narrative form!")

