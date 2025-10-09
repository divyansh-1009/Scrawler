"""
Example script showing how to use the Agentic Web Crawler programmatically
"""

import asyncio
from main import AgenticWebCrawler


async def example_crawl():
    """
    Example: Crawl a website with custom settings
    """
    print("Example: Programmatic Web Crawling")
    print("=" * 80)
    
    # Initialize the crawler with custom settings
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=10  # Limit to 10 pages for this example
    )
    
    # Define the starting URL
    # Replace with your target website
    start_url = "https://example.com"
    
    print(f"\nCrawling {start_url}...\n")
    
    # Perform the crawl
    scraped_data = await crawler.crawl_website(start_url)
    
    # Save to custom filename
    json_file = crawler.save_to_json("example_output.json")
    
    print(f"\n✓ Crawled {len(scraped_data)} pages")
    print(f"✓ Data saved to: {json_file}")
    
    # Analyze the content
    print("\nAnalyzing content with AI...")
    analysis_file = await crawler.analyze_scraped_content(json_file)
    
    print(f"✓ Analysis saved to: {analysis_file}")
    
    # Print some statistics
    print("\n" + "=" * 80)
    print("CRAWL STATISTICS")
    print("=" * 80)
    print(f"Total URLs visited: {len(crawler.visited_urls)}")
    print(f"Total pages scraped: {len(scraped_data)}")
    
    # Print first 5 URLs
    print("\nFirst 5 URLs crawled:")
    for i, url in enumerate(list(crawler.visited_urls)[:5], 1):
        print(f"  {i}. {url}")
    
    print("\n" + "=" * 80)
    print("✓ Example complete!")
    print("=" * 80)


async def quick_crawl(url: str, max_pages: int = 5):
    """
    Quick crawl function for testing
    
    Args:
        url: Website URL to crawl
        max_pages: Maximum pages to crawl
    """
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=max_pages
    )
    
    scraped_data = await crawler.crawl_website(url)
    json_file = crawler.save_to_json()
    
    return scraped_data, json_file


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_crawl())
    
    # Or use the quick crawl function
    # asyncio.run(quick_crawl("https://example.com", max_pages=5))
