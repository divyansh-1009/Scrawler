"""
Agentic AI Web Crawler using Crawl4AI and Ollama
This script crawls websites intelligently using the deepseek-r1:14b model for navigation decisions.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import ollama
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import NoExtractionStrategy
from bs4 import BeautifulSoup
from convert_to_markdown import json_to_markdown_complete


class AgenticWebCrawler:
    """
    An intelligent web crawler that uses AI to make navigation decisions.
    """
    
    def __init__(self, ollama_model: str = "deepseek-r1:14b", max_pages: int = 50):
        """
        Initialize the agentic web crawler.
        
        Args:
            ollama_model: The Ollama model to use for decision making
            max_pages: Maximum number of pages to crawl
        """
        self.ollama_model = ollama_model
        self.max_pages = max_pages
        self.visited_urls = set()
        self.scraped_data = []
        self.base_domain = None
        
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain as the base URL."""
        if not self.base_domain:
            return False
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain
    
    def _extract_structured_data(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract structured data from HTML based on common e-commerce patterns.
        
        Args:
            html: The HTML content to parse
            url: The URL being scraped (for context)
            
        Returns:
            Dictionary containing extracted structured data
        """
        soup = BeautifulSoup(html, 'lxml')
        structured_data = {
            "products": [],
            "categories": [],
            "page_type": "unknown"
        }
        
        # Detect if this is a product listing page
        # Pattern 1: Books to Scrape style (product_pod)
        product_pods = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and 'product' in x.lower())
        
        if product_pods:
            structured_data["page_type"] = "product_listing"
            
            for pod in product_pods:
                product = {}
                
                # Extract title
                title_tag = pod.find('h3')
                if title_tag:
                    title_link = title_tag.find('a')
                    if title_link:
                        product['title'] = title_link.get('title', title_link.get_text(strip=True))
                        product['url'] = title_link.get('href', '')
                
                # Extract price
                price_tag = pod.find(['p', 'span', 'div'], class_=lambda x: x and 'price' in x.lower())
                if price_tag:
                    product['price'] = price_tag.get_text(strip=True)
                
                # Extract availability/stock
                availability_tag = pod.find(['p', 'span', 'div'], class_=lambda x: x and ('stock' in x.lower() or 'availability' in x.lower()))
                if availability_tag:
                    product['availability'] = availability_tag.get_text(strip=True)
                
                # Extract rating
                rating_tag = pod.find(['p', 'span', 'div'], class_=lambda x: x and 'star-rating' in x.lower())
                if rating_tag:
                    # Rating is often in the class name like "star-rating Three"
                    classes = rating_tag.get('class', [])
                    for cls in classes:
                        if cls in ['One', 'Two', 'Three', 'Four', 'Five']:
                            product['rating'] = cls
                            break
                
                # Extract image
                img_tag = pod.find('img')
                if img_tag:
                    product['image'] = img_tag.get('src', '')
                    product['image_alt'] = img_tag.get('alt', '')
                
                # Only add if we found at least a title or price
                if 'title' in product or 'price' in product:
                    structured_data["products"].append(product)
        
        # Pattern 2: Generic product detection
        if not structured_data["products"]:
            # Try to find products by common class names
            potential_products = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['item', 'card', 'listing', 'result']
            ))
            
            for item in potential_products[:50]:  # Limit to 50 items
                product = {}
                
                # Look for price indicators
                price_element = item.find(string=lambda text: text and any(
                    symbol in text for symbol in ['$', '£', '€', '¥', 'USD', 'EUR', 'GBP']
                ))
                if price_element:
                    product['price'] = price_element.strip()
                
                # Look for title/name
                title_candidates = item.find_all(['h1', 'h2', 'h3', 'h4', 'a'], limit=3)
                for candidate in title_candidates:
                    text = candidate.get_text(strip=True)
                    if len(text) > 5 and len(text) < 200:  # Reasonable title length
                        product['title'] = text
                        break
                
                if 'price' in product and 'title' in product:
                    structured_data["products"].append(product)
        
        # Extract categories/navigation
        nav_sections = soup.find_all(['nav', 'aside', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['category', 'categories', 'nav', 'sidebar']
        ))
        
        for nav in nav_sections:
            links = nav.find_all('a', href=True)
            for link in links:
                category_text = link.get_text(strip=True)
                if category_text and len(category_text) < 50:
                    structured_data["categories"].append({
                        "name": category_text,
                        "url": link['href']
                    })
        
        # Remove duplicates from categories
        seen_categories = set()
        unique_categories = []
        for cat in structured_data["categories"]:
            if cat["name"] not in seen_categories:
                seen_categories.add(cat["name"])
                unique_categories.append(cat)
        structured_data["categories"] = unique_categories[:30]  # Limit to 30 categories
        
        return structured_data
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize and complete relative URLs."""
        url = urljoin(base_url, url)
        # Remove fragments
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    async def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML content."""
        import re
        # Simple regex to find href attributes
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        normalized_links = []
        
        for link in links:
            try:
                full_url = self._normalize_url(link, base_url)
                if self._is_same_domain(full_url) and full_url not in self.visited_urls:
                    normalized_links.append(full_url)
            except Exception:
                continue
                
        return list(set(normalized_links))
    
    async def _ask_ollama_for_navigation(self, current_url: str, available_links: List[str], content_summary: str) -> List[str]:
        """
        Use Ollama to decide which links to crawl next.
        
        Args:
            current_url: The current page URL
            available_links: List of available links to choose from
            content_summary: Summary of current page content
            
        Returns:
            List of URLs to crawl next
        """
        if not available_links:
            return []
        
        # Limit the number of links to analyze at once
        links_to_analyze = available_links[:20]
        
        prompt = f"""You are a web crawler assistant. Your task is to decide which links to crawl next.

Current URL: {current_url}
Current Page Summary: {content_summary[:500]}...

Available Links (select up to 5 most relevant):
{chr(10).join([f"{i+1}. {link}" for i, link in enumerate(links_to_analyze)])}

Analyze these links and select the TOP 5 most relevant and important links to crawl.
Consider:
1. Links that likely contain main content (not login, cart, social media)
2. Links that go deeper into the site structure
3. Links that represent different sections or categories

Respond ONLY with the numbers of the links to crawl (comma-separated, e.g., "1,3,5,7,9").
If no links are relevant, respond with "NONE".
"""
        
        try:
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt
            )
            
            answer = response['response'].strip()
            
            if answer.upper() == "NONE":
                return []
            
            # Extract numbers from response
            import re
            numbers = re.findall(r'\d+', answer)
            selected_links = []
            
            for num in numbers[:5]:  # Limit to 5 links
                idx = int(num) - 1
                if 0 <= idx < len(links_to_analyze):
                    selected_links.append(links_to_analyze[idx])
            
            return selected_links
            
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            # Fallback: return first 3 links
            return links_to_analyze[:3]
    
    async def _crawl_page(self, url: str, crawler: AsyncWebCrawler) -> Optional[Dict[str, Any]]:
        """
        Crawl a single page and extract content.
        
        Args:
            url: The URL to crawl
            crawler: The AsyncWebCrawler instance
            
        Returns:
            Dictionary containing page data or None if failed
        """
        try:
            print(f"Crawling: {url}")
            
            result = await crawler.arun(
                url=url,
                extraction_strategy=NoExtractionStrategy(),
                bypass_cache=True
            )
            
            if not result.success:
                print(f"Failed to crawl {url}")
                return None
            
            # Extract structured data from HTML
            structured_data = self._extract_structured_data(result.html, url)
            
            page_data = {
                "url": url,
                "title": result.metadata.get("title", "No title"),
                "description": result.metadata.get("description", ""),
                "html_content": result.html[:5000],  # Store first 5000 chars
                "markdown_content": result.markdown[:5000] if result.markdown else "",
                "links_found": len(result.links.get("internal", [])) if result.links else 0,
                "timestamp": datetime.now().isoformat(),
                "metadata": result.metadata,
                "structured_data": structured_data  # Add structured data
            }
            
            # Print summary of extracted data
            if structured_data["products"]:
                print(f"  → Extracted {len(structured_data['products'])} products")
            if structured_data["categories"]:
                print(f"  → Found {len(structured_data['categories'])} categories")
            
            return page_data
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None
    
    async def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Main crawling method that orchestrates the entire process.
        
        Args:
            start_url: The starting URL for crawling
            
        Returns:
            List of scraped page data
        """
        # Set base domain
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        
        print(f"Starting crawl of {start_url}")
        print(f"Using model: {self.ollama_model}")
        print(f"Max pages: {self.max_pages}")
        print("-" * 80)
        
        # Initialize the crawler
        async with AsyncWebCrawler(verbose=True) as crawler:
            # Queue of URLs to crawl
            url_queue = [start_url]
            
            while url_queue and len(self.visited_urls) < self.max_pages:
                current_url = url_queue.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(current_url)
                
                # Crawl the page
                page_data = await self._crawl_page(current_url, crawler)
                
                if page_data:
                    self.scraped_data.append(page_data)
                    
                    # Extract links from the page
                    links = await self._extract_links(page_data.get("html_content", ""), current_url)
                    
                    if links:
                        # Use AI to decide which links to crawl
                        content_summary = f"{page_data['title']}. {page_data['description']}"
                        selected_links = await self._ask_ollama_for_navigation(
                            current_url, 
                            links, 
                            content_summary
                        )
                        
                        print(f"AI selected {len(selected_links)} links to crawl from {current_url}")
                        
                        # Add selected links to queue
                        for link in selected_links:
                            if link not in self.visited_urls and link not in url_queue:
                                url_queue.append(link)
                
                print(f"Progress: {len(self.visited_urls)}/{self.max_pages} pages crawled")
                print(f"Queue size: {len(url_queue)}")
                print("-" * 80)
        
        return self.scraped_data
    
    def save_to_json(self, filename: str = "scraped_data.json"):
        """Save scraped data to JSON file."""
        output_path = os.path.join(os.getcwd(), filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "crawl_summary": {
                    "total_pages": len(self.scraped_data),
                    "urls_visited": list(self.visited_urls),
                    "timestamp": datetime.now().isoformat()
                },
                "pages": self.scraped_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nScraped data saved to: {output_path}")
        return output_path
    
    def generate_data_report(self, json_file: str) -> str:
        """
        Generate a data-focused report showing actual extracted information.
        No AI summaries - just the actual data extracted from pages.
        
        Args:
            json_file: Path to the JSON file with scraped data
            
        Returns:
            Path to the data report file
        """
        print("\n" + "=" * 80)
        print("GENERATING DATA REPORT")
        print("=" * 80)
        
        # Load the scraped data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        report = []
        report.append("# Web Crawling Data Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal Pages Crawled: {data['crawl_summary']['total_pages']}")
        report.append("\n" + "=" * 80 + "\n")
        
        # Extract all products from all pages
        all_products = []
        all_categories = set()
        
        for page in data.get('pages', []):
            structured = page.get('structured_data', {})
            if structured:
                products = structured.get('products', [])
                for product in products:
                    product['source_url'] = page['url']
                    all_products.append(product)
                
                categories = structured.get('categories', [])
                for cat in categories:
                    all_categories.add(cat['name'])
        
        # Summary
        report.append("## Extraction Summary\n")
        report.append(f"- **Total Products Extracted**: {len(all_products)}")
        report.append(f"- **Unique Categories Found**: {len(all_categories)}")
        report.append(f"- **Pages with Products**: {sum(1 for p in data['pages'] if p.get('structured_data', {}).get('products'))}")
        report.append("")
        
        # Products table
        if all_products:
            report.append("## All Products Extracted\n")
            report.append("| # | Title | Price | Rating | Availability | Source Page |")
            report.append("|---|-------|-------|--------|--------------|-------------|")
            
            for i, product in enumerate(all_products, 1):
                title = product.get('title', 'N/A')[:50]  # Truncate long titles
                price = product.get('price', 'N/A')
                rating = f"{product.get('rating', 'N/A')} ({product.get('rating_numeric', 'N/A')}/5)"
                availability = product.get('availability', 'N/A')
                source = product.get('source_url', 'N/A').split('/')[-2]  # Short URL
                
                report.append(f"| {i} | {title} | {price} | {rating} | {availability} | {source} |")
            
            report.append("")
            
            # Statistics
            report.append("## Data Statistics\n")
            
            # Price stats
            prices = []
            for p in all_products:
                price_str = p.get('price', '£0')
                try:
                    price_num = float(price_str.replace('£', '').replace('$', '').replace(',', ''))
                    prices.append(price_num)
                except:
                    pass
            
            if prices:
                report.append("### Price Analysis")
                report.append(f"- **Minimum Price**: £{min(prices):.2f}")
                report.append(f"- **Maximum Price**: £{max(prices):.2f}")
                report.append(f"- **Average Price**: £{sum(prices)/len(prices):.2f}")
                report.append(f"- **Total Value**: £{sum(prices):.2f}")
                report.append("")
            
            # Rating stats
            ratings = [p.get('rating_numeric', 0) for p in all_products if 'rating_numeric' in p]
            if ratings:
                report.append("### Rating Distribution")
                for star in [5, 4, 3, 2, 1]:
                    count = ratings.count(star)
                    if count > 0:
                        percentage = (count / len(ratings)) * 100
                        bar = '█' * int(percentage / 5)
                        report.append(f"- **{star}★**: {count} products ({percentage:.1f}%) {bar}")
                report.append(f"- **Average Rating**: {sum(ratings)/len(ratings):.2f}★")
                report.append("")
        
        # Detailed product info
        if all_products:
            report.append("## Detailed Product Data\n")
            for i, product in enumerate(all_products[:20], 1):  # First 20 products
                report.append(f"### Product {i}: {product.get('title', 'N/A')}\n")
                report.append("```json")
                # Remove source_url for cleaner display
                display_product = {k: v for k, v in product.items() if k != 'source_url'}
                report.append(json.dumps(display_product, indent=2, ensure_ascii=False))
                report.append("```\n")
        
        # Categories
        if all_categories:
            report.append("## Categories Found\n")
            for cat in sorted(all_categories)[:30]:
                report.append(f"- {cat}")
            report.append("")
        
        # Save report
        report_filename = json_file.replace('.json', '_data_report.md')
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"\nData report saved to: {report_filename}")
        return report_filename
    
    async def analyze_scraped_content(self, json_file: str) -> str:
        """
        Use Ollama to analyze the scraped content and generate a human-readable report.
        
        Args:
            json_file: Path to the JSON file with scraped data
            
        Returns:
            Path to the analysis report file
        """
        print("\n" + "=" * 80)
        print("ANALYZING SCRAPED CONTENT WITH AI")
        print("=" * 80)
        
        # Load the scraped data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analysis_report = []
        analysis_report.append("# Web Crawling Analysis Report")
        analysis_report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        analysis_report.append(f"\nTotal Pages Crawled: {data['crawl_summary']['total_pages']}")
        analysis_report.append("\n" + "=" * 80 + "\n")
        
        # Analyze overall content
        print("Generating overall summary...")
        all_titles = [page['title'] for page in data['pages']]
        all_descriptions = [page.get('description', '') for page in data['pages'] if page.get('description')]
        
        overall_prompt = f"""Analyze this website crawl data and provide a comprehensive summary.

Total pages crawled: {len(data['pages'])}

Page titles:
{chr(10).join(all_titles[:20])}

Descriptions:
{chr(10).join(all_descriptions[:10])}

Provide:
1. What type of website is this?
2. Main topics and themes covered
3. Overall structure and organization
4. Key sections identified
5. Target audience

Keep your response concise but informative."""
        
        try:
            overall_response = ollama.generate(
                model=self.ollama_model,
                prompt=overall_prompt
            )
            
            analysis_report.append("## Overall Website Summary\n")
            analysis_report.append(overall_response['response'])
            analysis_report.append("\n\n" + "=" * 80 + "\n")
            
        except Exception as e:
            print(f"Error generating overall summary: {e}")
            analysis_report.append("## Overall Website Summary\n")
            analysis_report.append(f"Error generating summary: {e}\n\n")
        
        # Analyze individual pages
        analysis_report.append("## Individual Page Analysis\n")
        
        for i, page in enumerate(data['pages'][:10]):  # Analyze first 10 pages in detail
            print(f"Analyzing page {i+1}/{min(10, len(data['pages']))}: {page['url']}")
            
            page_prompt = f"""Analyze this web page and provide a detailed breakdown in human-readable format.

URL: {page['url']}
Title: {page['title']}
Description: {page.get('description', 'N/A')}

Content excerpt:
{page.get('markdown_content', page.get('html_content', ''))[:1000]}

Provide:
1. Page purpose and main topic
2. Key information presented
3. Important elements or features
4. Relationship to overall site structure

Be specific and detailed."""
            
            try:
                page_response = ollama.generate(
                    model=self.ollama_model,
                    prompt=page_prompt
                )
                
                analysis_report.append(f"\n### Page {i+1}: {page['title']}\n")
                analysis_report.append(f"**URL:** {page['url']}\n")
                analysis_report.append(f"\n{page_response['response']}\n")
                analysis_report.append("\n" + "-" * 80 + "\n")
                
            except Exception as e:
                print(f"Error analyzing page {i+1}: {e}")
                analysis_report.append(f"\n### Page {i+1}: {page['title']}\n")
                analysis_report.append(f"Error analyzing page: {e}\n\n")
        
        # Save analysis report
        report_filename = json_file.replace('.json', '_analysis.md')
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(analysis_report))
        
        print(f"\nAnalysis report saved to: {report_filename}")
        return report_filename


async def main():
    """Main execution function."""
    print("=" * 80)
    print("AGENTIC WEB CRAWLER WITH AI NAVIGATION")
    print("=" * 80)
    print()
    
    # Get user input
    start_url = input("Enter the website URL to crawl: ").strip()
    
    if not start_url.startswith(('http://', 'https://')):
        start_url = 'https://' + start_url
    
    max_pages_input = input("Enter maximum number of pages to crawl (default: 50): ").strip()
    max_pages = int(max_pages_input) if max_pages_input.isdigit() else 50
    
    # Initialize crawler
    crawler = AgenticWebCrawler(
        ollama_model="deepseek-r1:14b",
        max_pages=max_pages
    )
    
    # Start crawling
    print("\nStarting crawl...\n")
    scraped_data = await crawler.crawl_website(start_url)
    
    # Save data
    json_file = crawler.save_to_json()
    
    print(f"\n✓ Successfully crawled {len(scraped_data)} pages")
    
    # Check if any products were extracted
    total_products = sum(len(page.get('structured_data', {}).get('products', [])) for page in scraped_data)
    
    if total_products > 0:
        print(f"✓ Extracted {total_products} products from the pages")
    
    # Generate human-readable report
    generate_report = input("\nGenerate human-readable analysis report? (y/n): ").strip().lower()
    
    if generate_report == 'y':
        analysis_file = json_file.replace('.json', '_analysis.md')
        json_to_markdown_complete(json_file, analysis_file)
        print(f"\n✓ Analysis complete! Check {analysis_file}")
    
    print("\n" + "=" * 80)
    print("CRAWLING COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
