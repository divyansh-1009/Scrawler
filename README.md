# Agentic AI Web Crawler

An intelligent web crawler that uses AI (Ollama's deepseek-r1:14b model) to make smart navigation decisions while crawling websites. Built with `crawl4ai` for efficient web scraping and `ollama` for AI-powered decision making.

## Features

- 🤖 **AI-Powered Navigation**: Uses Ollama's deepseek-r1:14b model to intelligently decide which links to crawl
- 🌐 **Schema-less Crawling**: No predefined structure needed - the AI adapts to any website
- 📊 **JSON Export**: All scraped content is saved in structured JSON format
- 📝 **Complete Data Conversion**: Automatically converts all scraped data to human-readable markdown format
- 🔄 **Async Architecture**: Fast, efficient crawling using async/await patterns
- 🎯 **Smart Link Selection**: AI filters out irrelevant links (login, cart, social media, etc.)
- 📈 **Progress Tracking**: Real-time updates on crawling progress
- 🎁 **Structured Data Extraction**: Automatically extracts products, prices, ratings, and categories

## Prerequisites

Before running this crawler, ensure you have:

1. **Python 3.8+** installed
2. **Ollama** installed and running with the deepseek-r1:14b model

### Installing Ollama

1. Download and install Ollama from [ollama.ai](https://ollama.ai/)
2. Pull the deepseek-r1:14b model:
   ```bash
   ollama pull deepseek-r1:14b
   ```
3. Verify the model is available:
   ```bash
   ollama list
   ```

## Installation

1. **Clone or navigate to this directory**

2. **Create and activate a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the crawler:

```powershell
python main.py
```

You'll be prompted to:
1. Enter the website URL to crawl
2. Specify the maximum number of pages to crawl (default: 50)
3. Choose whether to analyze the content after crawling

### Example Session

```
Enter the website URL to crawl: example.com
Enter maximum number of pages to crawl (default: 50): 20

Starting crawl...
Crawling: https://example.com
AI selected 5 links to crawl from https://example.com
Progress: 1/20 pages crawled
...

✓ Successfully crawled 20 pages
Scraped data saved to: F:\Latest crawler\scraped_data.json

Do you want to analyze the scraped content with AI? (y/n): y

Analyzing scraped content...
✓ Analysis complete! Check scraped_data_analysis.md
```

## Output Files

### 1. scraped_data.json

Contains all raw scraped data:
```json
{
  "crawl_summary": {
    "total_pages": 20,
    "urls_visited": ["url1", "url2", ...],
    "timestamp": "2025-10-10T..."
  },
  "pages": [
    {
      "url": "https://example.com",
      "title": "Page Title",
      "description": "Page description",
      "html_content": "...",
      "markdown_content": "...",
      "links_found": 15,
      "timestamp": "2025-10-10T...",
      "metadata": {...}
    }
  ]
}
```

### 2. scraped_data_analysis.md

Human-readable analysis report including:
- Overall website summary
- Site structure and organization
- Individual page breakdowns
- Key topics and themes
- Target audience analysis

## How It Works

### 1. Crawling Phase
- Starts at the provided URL
- Extracts all content using crawl4ai
- Finds all internal links on the page

### 2. AI Navigation Phase
- Sends available links to Ollama (tinyllama model)
- AI analyzes links and selects the most relevant ones
- Filters out non-content links (login, cart, social media)
- Prioritizes links that go deeper into site structure

### 3. Data Storage Phase
- Saves all scraped content to JSON file
- Includes metadata, timestamps, and crawl summary

### 4. Analysis Phase (Optional)
- AI reads the scraped JSON data
- Generates overall website summary
- Analyzes individual pages in detail
- Creates human-readable markdown report

## Configuration

### Change AI Model

Edit `main.py` to use a different Ollama model:

```python
crawler = AgenticWebCrawler(
    ollama_model="mistral:latest",  # Change this
    max_pages=50
)
```

### Adjust Crawl Depth

Modify the `max_pages` parameter:

```python
crawler = AgenticWebCrawler(
    ollama_model="tinyllama:latest",
    max_pages=100  # Crawl up to 100 pages
)
```

### Customize Content Storage

Modify the `_crawl_page` method to adjust how much content is stored:

```python
"html_content": result.html[:5000],  # Change character limit
```

## Advanced Features

### Programmatic Usage

You can use the crawler in your own scripts:

```python
import asyncio
from main import AgenticWebCrawler

async def my_crawl():
    crawler = AgenticWebCrawler(
        ollama_model="tinyllama:latest",
        max_pages=30
    )
    
    # Crawl website
    data = await crawler.crawl_website("https://example.com")
    
    # Save to JSON
    json_file = crawler.save_to_json("my_output.json")
    
    # Analyze content
    analysis = await crawler.analyze_scraped_content(json_file)
    
    return data, analysis

# Run it
asyncio.run(my_crawl())
```

### Custom Link Selection

Modify the `_ask_ollama_for_navigation` method to change how the AI selects links:

```python
prompt = f"""Your custom prompt here...
Select links that meet your specific criteria.
"""
```

## Troubleshooting

### Issue: "Ollama connection error"
**Solution**: Make sure Ollama is running:
```bash
ollama serve
```

### Issue: "Model not found"
**Solution**: Pull the tinyllama model:
```bash
ollama pull tinyllama:latest
```

### Issue: "Crawl4ai installation fails"
**Solution**: Try installing with specific dependencies:
```powershell
pip install crawl4ai --no-cache-dir
```

### Issue: "SSL Certificate errors"
**Solution**: Add SSL verification bypass in the code (not recommended for production):
```python
# In AsyncWebCrawler initialization
async with AsyncWebCrawler(verbose=True, verify_ssl=False) as crawler:
```

## Performance Tips

1. **Use faster AI models**: Switch to `mistral:latest` or `llama2:latest` for better accuracy
2. **Limit max_pages**: Start with small numbers (10-20) for testing
3. **Adjust link analysis**: Modify the number of links analyzed per page
4. **Use SSD storage**: Faster I/O for JSON operations

## Limitations

- Only crawls pages within the same domain
- Respects basic URL normalization (removes fragments)
- Does not handle JavaScript-heavy SPAs perfectly
- AI decisions depend on model quality and prompt engineering

## License

This project is open-source and available for educational and commercial use.

## Contributing

Feel free to enhance this crawler:
- Add support for robots.txt
- Implement rate limiting
- Add proxy support
- Improve AI prompts
- Add more export formats (CSV, SQLite, etc.)

## Credits

- Built with [crawl4ai](https://github.com/unclecode/crawl4ai)
- Powered by [Ollama](https://ollama.ai/)
- Uses tinyllama model for AI decision making

## Support

For issues and questions:
1. Check the Troubleshooting section
2. Review crawl4ai documentation
3. Check Ollama documentation
4. Open an issue on the project repository

---

**Happy Crawling! 🚀**
