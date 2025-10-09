"""
USAGE EXAMPLES - Agentic Web Crawler
Copy and customize these examples for your specific use cases
"""

import asyncio
from main import AgenticWebCrawler


# ============================================================================
# EXAMPLE 1: Basic Quick Crawl (5 pages)
# ============================================================================
async def example_1_quick_crawl():
    """Quick test crawl of a small website"""
    print("EXAMPLE 1: Quick Crawl (5 pages)")
    print("-" * 80)
    
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=5
    )
    
    # Replace with your target URL
    url = "https://example.com"
    
    data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json("quick_crawl.json")
    
    print(f"\n✓ Crawled {len(data)} pages")
    print(f"✓ Saved to: {json_file}\n")


# ============================================================================
# EXAMPLE 2: Medium Crawl with Analysis (20 pages)
# ============================================================================
async def example_2_medium_crawl_with_analysis():
    """Medium crawl with AI analysis"""
    print("EXAMPLE 2: Medium Crawl with Analysis (20 pages)")
    print("-" * 80)
    
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=20
    )
    
    url = "https://your-website.com"
    
    # Crawl
    data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json("medium_crawl.json")
    
    # Analyze
    analysis_file = await crawler.analyze_scraped_content(json_file)
    
    print(f"\n✓ Crawled {len(data)} pages")
    print(f"✓ Data: {json_file}")
    print(f"✓ Analysis: {analysis_file}\n")


# ============================================================================
# EXAMPLE 3: Large Crawl (100 pages)
# ============================================================================
async def example_3_large_crawl():
    """Large scale crawl for comprehensive site mapping"""
    print("EXAMPLE 3: Large Crawl (100 pages)")
    print("-" * 80)
    
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=100
    )
    
    url = "https://large-website.com"
    
    data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json("large_crawl.json")
    
    print(f"\n✓ Crawled {len(data)} pages")
    print(f"✓ Saved to: {json_file}\n")


# ============================================================================
# EXAMPLE 4: Using Different AI Model (Mistral)
# ============================================================================
async def example_4_different_model():
    """Use a different Ollama model for better accuracy"""
    print("EXAMPLE 4: Using Mistral Model")
    print("-" * 80)
    
    # Note: Make sure you have mistral installed: ollama pull mistral:latest
    crawler = AgenticWebCrawler(
        ollama_model="mistral:latest",  # More accurate but slower
        max_pages=15
    )
    
    url = "https://example.com"
    
    data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json("mistral_crawl.json")
    
    print(f"\n✓ Crawled {len(data)} pages")
    print(f"✓ Saved to: {json_file}\n")


# ============================================================================
# EXAMPLE 5: Multiple Website Crawls
# ============================================================================
async def example_5_multiple_websites():
    """Crawl multiple websites sequentially"""
    print("EXAMPLE 5: Multiple Website Crawls")
    print("-" * 80)
    
    websites = [
        "https://website1.com",
        "https://website2.com",
        "https://website3.com"
    ]
    
    for i, url in enumerate(websites, 1):
        print(f"\nCrawling website {i}/{len(websites)}: {url}")
        
        crawler = AgenticWebCrawler(
            ollama_model="tinyllama:latest",
            max_pages=10
        )
        
        data = await crawler.crawl_website(url)
        json_file = crawler.save_to_json(f"website_{i}_crawl.json")
        
        print(f"✓ Website {i} done: {len(data)} pages crawled")
    
    print(f"\n✓ All {len(websites)} websites crawled!\n")


# ============================================================================
# EXAMPLE 6: Crawl and Get Statistics
# ============================================================================
async def example_6_with_statistics():
    """Crawl and print detailed statistics"""
    print("EXAMPLE 6: Crawl with Statistics")
    print("-" * 80)
    
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=15
    )
    
    url = "https://example.com"
    
    data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json("stats_crawl.json")
    
    # Calculate statistics
    total_pages = len(data)
    total_links = sum(page.get('links_found', 0) for page in data)
    avg_links = total_links / total_pages if total_pages > 0 else 0
    
    pages_with_titles = sum(1 for page in data if page.get('title'))
    pages_with_descriptions = sum(1 for page in data if page.get('description'))
    
    print(f"\n{'='*80}")
    print("CRAWL STATISTICS")
    print(f"{'='*80}")
    print(f"Total Pages Crawled: {total_pages}")
    print(f"Total Links Found: {total_links}")
    print(f"Average Links/Page: {avg_links:.1f}")
    print(f"Pages with Titles: {pages_with_titles}")
    print(f"Pages with Descriptions: {pages_with_descriptions}")
    print(f"{'='*80}\n")


# ============================================================================
# EXAMPLE 7: Analysis Only (from existing JSON)
# ============================================================================
async def example_7_analysis_only():
    """Analyze previously crawled data without re-crawling"""
    print("EXAMPLE 7: Analysis Only")
    print("-" * 80)
    
    # Assuming you already have a JSON file
    existing_json = "scraped_data.json"
    
    crawler = AgenticWebCrawler()
    
    print(f"Analyzing existing data: {existing_json}")
    analysis_file = await crawler.analyze_scraped_content(existing_json)
    
    print(f"\n✓ Analysis complete: {analysis_file}\n")


# ============================================================================
# EXAMPLE 8: Custom Output Filenames
# ============================================================================
async def example_8_custom_filenames():
    """Use custom filenames for organization"""
    print("EXAMPLE 8: Custom Filenames")
    print("-" * 80)
    
    from datetime import datetime
    
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=10
    )
    
    url = "https://example.com"
    
    data = await crawler.crawl_website(url)
    
    # Create timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = url.split("//")[1].split("/")[0].replace(".", "_")
    filename = f"crawl_{domain}_{timestamp}.json"
    
    json_file = crawler.save_to_json(filename)
    
    print(f"\n✓ Saved to: {json_file}\n")


# ============================================================================
# EXAMPLE 9: Error Handling
# ============================================================================
async def example_9_with_error_handling():
    """Crawl with proper error handling"""
    print("EXAMPLE 9: Error Handling")
    print("-" * 80)
    
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=10
    )
    
    url = "https://example.com"
    
    try:
        data = await crawler.crawl_website(url)
        
        if data:
            json_file = crawler.save_to_json()
            print(f"\n✓ Successfully crawled {len(data)} pages")
            print(f"✓ Saved to: {json_file}\n")
        else:
            print("\n✗ No data was crawled\n")
            
    except Exception as e:
        print(f"\n✗ Error during crawling: {e}\n")


# ============================================================================
# EXAMPLE 10: Interactive Mode
# ============================================================================
async def example_10_interactive():
    """Interactive crawl with user input"""
    print("EXAMPLE 10: Interactive Mode")
    print("-" * 80)
    
    # Get user input
    url = input("Enter website URL: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    max_pages_input = input("Max pages (default 20): ").strip()
    max_pages = int(max_pages_input) if max_pages_input.isdigit() else 20
    
    do_analysis = input("Run AI analysis? (y/n): ").strip().lower() == 'y'
    
    # Create crawler
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=max_pages
    )
    
    # Crawl
    print(f"\nCrawling {url}...")
    data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json()
    
    print(f"\n✓ Crawled {len(data)} pages")
    
    # Optional analysis
    if do_analysis:
        print("\nRunning AI analysis...")
        analysis_file = await crawler.analyze_scraped_content(json_file)
        print(f"✓ Analysis saved to: {analysis_file}")
    
    print("\n✓ Complete!\n")


# ============================================================================
# RUN EXAMPLES
# ============================================================================

async def run_all_examples():
    """Run all examples (uncomment the ones you want to test)"""
    
    # Uncomment the example you want to run:
    
    await example_1_quick_crawl()
    # await example_2_medium_crawl_with_analysis()
    # await example_3_large_crawl()
    # await example_4_different_model()
    # await example_5_multiple_websites()
    # await example_6_with_statistics()
    # await example_7_analysis_only()
    # await example_8_custom_filenames()
    # await example_9_with_error_handling()
    # await example_10_interactive()


if __name__ == "__main__":
    print("=" * 80)
    print("AGENTIC WEB CRAWLER - USAGE EXAMPLES")
    print("=" * 80)
    print()
    
    asyncio.run(run_all_examples())
    
    print("=" * 80)
    print("Examples complete!")
    print("=" * 80)
