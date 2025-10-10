# Agentic AI Web Crawler

An intelligent, AI-powered web crawler that uses **deepseek-r1:14b** through Ollama to make smart navigation decisions while systematically crawling websites. The crawler extracts structured data, generates human-readable analysis reports, and preserves every detail in natural language format.

---

## 🌟 Features

### Core Capabilities
- 🤖 **AI-Powered Navigation**: Uses deepseek-r1:14b model to intelligently select which links to crawl
- � **Structured Data Extraction**: Automatically identifies and extracts products, prices, ratings, categories
- 📊 **Smart Link Filtering**: Excludes images, CSS, JS, and other non-content files
- 🔄 **Async Architecture**: Fast, efficient crawling using async/await patterns
- 📝 **Natural Language Reports**: Converts all scraped data to flowing paragraphs
- � **Complete Data Preservation**: Every detail saved in both JSON and human-readable formats

### Data Extraction
- **E-commerce Products**: Title, price, rating, availability, images
- **Categories & Navigation**: Complete site taxonomy and structure
- **Content**: Full HTML and Markdown content preservation
- **Metadata**: Timestamps, URLs, page titles, descriptions
- **Links**: All hyperlinks with domain filtering

### Output Formats
1. **JSON** (`scraped_data.json`): Complete structured data
2. **Markdown** (`scraped_data_analysis.md`): Natural language narrative report with:
   - Executive summary
   - Page-by-page detailed analysis
   - Product descriptions in flowing paragraphs
   - Statistical analysis
   - Complete raw JSON backup

---

## 📋 Prerequisites

### System Requirements
- **RAM**: Minimum 9GB (deepseek-r1:14b requires ~8.7GB)
- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux

### Required Software
1. **Python 3.8+**
2. **Ollama** with deepseek-r1:14b model

---

## 🚀 Installation

### Step 1: Install Ollama and Model

1. Download and install Ollama from [ollama.ai](https://ollama.ai/)

2. Pull the deepseek-r1:14b model:
   ```bash
   ollama pull deepseek-r1:14b
   ```

3. Verify installation:
   ```bash
   ollama list
   ```
   You should see `deepseek-r1:14b` in the list.

### Step 2: Set Up Python Environment

1. **Clone or navigate to the project directory**

2. **Create virtual environment**:
   ```powershell
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   ```bash
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Verify Installation

Run the setup check:
```bash
python -c "import main; print('✓ Installation successful!')"
```

---

## 💻 Usage

### Basic Usage

1. **Activate virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate      # Linux/Mac
   ```

2. **Run the crawler**:
   ```bash
   python main.py
   ```

3. **Follow the prompts**:
   ```
   Enter the website URL to crawl: https://example.com
   Enter maximum number of pages to crawl (default: 50): 20
   ```

4. **Wait for crawling to complete**

5. **Generate analysis report** (when prompted):
   ```
   Generate human-readable analysis report? (y/n): y
   ```

### Output Files

After crawling, you'll have:
- **`scraped_data.json`**: Complete structured data
- **`scraped_data_analysis.md`**: Human-readable report (if generated)

---

## 📁 Project Structure

```
f:\Latest crawler\
├── venv/                      # Virtual environment
├── config.py                  # Configuration settings
├── main.py                    # Main crawler application
├── convert_to_markdown.py     # JSON to Markdown converter
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                # Git ignore rules
├── scraped_data.json         # Generated: Raw crawl data
└── scraped_data_analysis.md  # Generated: Human-readable report
```

---

## ⚙️ Configuration

Edit `config.py` to customize crawler behavior:

```python
# AI Model
OLLAMA_MODEL = "deepseek-r1:14b"
OLLAMA_TIMEOUT = 60  # seconds

# Crawler Settings
DEFAULT_MAX_PAGES = 50
MAX_LINKS_PER_PAGE = 20
MAX_LINKS_TO_SELECT = 5

# Content Storage
HTML_CONTENT_LIMIT = 5000
MARKDOWN_CONTENT_LIMIT = 5000

# Output Files
DEFAULT_JSON_OUTPUT = "scraped_data.json"
DEFAULT_ANALYSIS_OUTPUT = "scraped_data_analysis.md"

# Behavior
BYPASS_CACHE = True
VERBOSE_MODE = True
SAME_DOMAIN_ONLY = True
```

---

## 🔧 How It Works

### Crawling Process

1. **Initialization**
   - User provides starting URL and max pages
   - Crawler extracts base domain for filtering
   - Queue initialized with start URL

2. **Page Crawling**
   ```
   For each URL in queue:
   ├── Fetch page using Crawl4AI
   ├── Extract HTML and Markdown content
   ├── Parse structured data (products, categories)
   ├── Extract all links from page
   ├── Filter out images, CSS, JS, etc.
   ├── Send filtered links to AI
   └── AI selects top 5 relevant links
   ```

3. **AI Navigation Decision**
   - AI analyzes current page context
   - Evaluates available links
   - Selects most relevant content pages
   - Avoids login pages, carts, social media

4. **Data Extraction**
   - **Products**: Uses BeautifulSoup with CSS selectors
     - `article.product_pod` → Product containers
     - `h3 > a` → Product titles and URLs
     - `p.price_color` → Prices
     - `p.star-rating` → Ratings
     - `p.instock.availability` → Stock status
     - `img` → Product images
   
   - **Categories**: Extracts from navigation menus
     - Searches `<nav>`, `<aside>`, category divs
     - Limits to 30 unique categories
   
   - **Content**: Full HTML and Markdown preservation

5. **Queue Management**
   - Adds AI-selected links to queue
   - Tracks visited URLs to avoid duplicates
   - Continues until max_pages or queue empty
   - **No fallback**: If AI fails, link selection is skipped

6. **Output Generation**
   - Saves JSON with complete structured data
   - Optionally generates natural language report
   - Every detail preserved in narrative format

### Link Filtering

Automatically excludes:
```
✗ Images: .jpg, .jpeg, .png, .gif, .svg, .ico, .webp
✗ Styles/Scripts: .css, .js, .woff, .ttf, .eot
✗ Documents: .pdf, .zip, .tar, .gz, .rar, .exe
✗ Media: .mp4, .mp3, .avi, .mov, .wav
✗ Auth pages: login, signin, signup, register, logout
✗ E-commerce: cart, checkout, wishlist, account
✗ Social: facebook.com, twitter.com, instagram.com, etc.
✗ Special: mailto:, tel:, javascript:
```

---

## 📊 Data Structure

### JSON Output Schema

```json
{
  "crawl_summary": {
    "total_pages": 10,
    "urls_visited": ["url1", "url2", ...],
    "timestamp": "2025-10-10T05:41:03.580181"
  },
  "pages": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "description": "Meta description",
      "html_content": "<html>...</html>",
      "markdown_content": "# Converted markdown...",
      "links_found": 73,
      "timestamp": "2025-10-10T05:41:01.363554",
      "metadata": {
        "title": "Page Title",
        "description": "...",
        "keywords": null,
        "author": null
      },
      "structured_data": {
        "products": [
          {
            "title": "Product Name",
            "url": "/product-url",
            "price": "£29.99",
            "availability": "In stock",
            "rating": "Five",
            "rating_numeric": 5,
            "image": "/path/to/image.jpg",
            "image_alt": "Product description"
          }
        ],
        "categories": [
          {
            "name": "Category Name",
            "url": "/category/url"
          }
        ],
        "page_type": "product_listing"
      }
    }
  ]
}
```

### Markdown Report Structure

1. **Executive Summary**
   - Crawl session overview
   - Total pages and URLs
   - Timestamp information

2. **Detailed Page Analysis**
   - For each page:
     - Location and basic info (paragraphs)
     - Product descriptions (flowing text)
     - Category explanations (sentences)
     - Content analysis (word counts, excerpts)
     - Full content (collapsible)
     - Raw HTML (collapsible)

3. **Statistical Analysis**
   - Product inventory summary
   - Price analysis (min, max, average, total value)
   - Rating distribution
   - Availability status
   - Category taxonomy
   - Link discovery metrics
   - Data volume statistics

4. **Raw JSON Backup**
   - Complete JSON embedded in markdown
   - Collapsible for reference

---

## 🎯 Use Cases

### E-commerce Product Research
```bash
python main.py
# Enter: https://books.toscrape.com/catalogue/category/books/fantasy_19/
# Max pages: 10
```
**Result**: Complete product catalog with prices, ratings, availability

### News Article Collection
```bash
python main.py
# Enter: https://www.aljazeera.com/
# Max pages: 20
```
**Result**: Article titles, content, categories, publication data

### Website Structure Analysis
```bash
python main.py
# Enter: https://example.com/
# Max pages: 50
```
**Result**: Complete site map, navigation structure, category taxonomy

### Content Aggregation
- Blog posts
- Documentation pages
- Directory listings
- Category pages
- Search results

---

## 🛠️ Advanced Usage

### Convert Existing JSON to Markdown

If you already have a `scraped_data.json` file:

```bash
python convert_to_markdown.py scraped_data.json output.md
```

Or with custom names:
```bash
python convert_to_markdown.py my_data.json my_report.md
```

### Programmatic Usage

```python
import asyncio
from main import AgenticWebCrawler
from convert_to_markdown import json_to_markdown_complete

async def crawl_site():
    # Initialize crawler
    crawler = AgenticWebCrawler(
        ollama_model="deepseek-r1:14b",
        max_pages=20
    )
    
    # Crawl website
    data = await crawler.crawl_website("https://example.com")
    
    # Save to JSON
    json_file = crawler.save_to_json("my_crawl.json")
    
    # Generate markdown report
    json_to_markdown_complete(json_file, "my_report.md")
    
    return data

# Run
asyncio.run(crawl_site())
```

---

## ⚠️ Important Notes

### Memory Requirements
- **deepseek-r1:14b requires ~8.7GB RAM**
- Ensure your system has at least **10GB total RAM**
- If you experience memory errors:
  - Close other applications
  - Reduce max_pages
  - Consider using a smaller model (edit config.py)

### AI Behavior
- **No fallback logic**: If AI fails due to memory, link selection is skipped for that page
- Crawler continues with remaining URLs in queue
- Link filtering prevents crawling static assets even if AI unavailable

### Rate Limiting
- Be respectful of target websites
- Implement delays if needed (modify crawler)
- Check robots.txt compliance
- Consider Terms of Service

### Legal Considerations
- Ensure you have permission to crawl target sites
- Respect robots.txt directives
- Don't overload servers
- Use scraped data responsibly

---

## 🐛 Troubleshooting

### Issue: "Model requires more system memory"
**Solution**: 
- Your system doesn't have enough RAM
- Close other applications
- Or edit `config.py` to use a smaller model like `qwen2.5:3b`

### Issue: Crawler stops early (e.g., 4 pages instead of 20)
**Possible Causes**: 
- AI failed due to memory (now handled gracefully)
- Queue exhausted (no auto-refill logic)
- All same-domain URLs already visited

**Solution**:
- Check terminal output for AI errors
- Verify link filtering isn't too aggressive
- Ensure starting URL has many internal links

### Issue: No products extracted
**Solution**:
- The site may use different HTML structure
- Check if products use `article.product_pod` class
- Modify `_extract_structured_data()` in main.py for your site

### Issue: "Ollama not responding"
**Solution**:
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
# Windows: Restart the Ollama application
# Linux/Mac: sudo systemctl restart ollama
```

### Issue: Import errors
**Solution**:
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Dependencies

```
crawl4ai >= 0.3.0      # Web crawling framework
ollama >= 0.1.0        # AI model integration
beautifulsoup4         # HTML parsing
lxml                   # XML/HTML parser
aiohttp                # Async HTTP client
```

Full list in `requirements.txt`

---

## 🔄 Development

### Adding Custom Extractors

Edit `_extract_structured_data()` in `main.py`:

```python
def _extract_structured_data(self, html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    structured_data = {
        "products": [],
        "categories": [],
        "page_type": "unknown"
    }
    
    # Add your custom extraction logic here
    custom_items = soup.find_all('div', class_='your-class')
    for item in custom_items:
        # Extract custom fields
        pass
    
    return structured_data
```

### Modifying AI Prompts

Edit prompts in `_ask_ollama_for_navigation()` or `config.py`

---

## 📝 Output Examples

### Console Output
```
================================================================================
AGENTIC WEB CRAWLER WITH AI NAVIGATION
================================================================================

NOTE: This crawler uses deepseek-r1:14b which requires ~8.7GB RAM

Enter the website URL to crawl: https://books.toscrape.com
Enter maximum number of pages to crawl (default: 50): 10

Starting crawl...

Starting crawl of https://books.toscrape.com
Using model: deepseek-r1:14b
Max pages: 10
--------------------------------------------------------------------------------
[FETCH]... ↓ https://books.toscrape.com
| ✓ | ⏱: 2.87s
[SCRAPE].. ◆ https://books.toscrape.com
| ✓ | ⏱: 0.11s
  → Found 30 categories
AI selected 5 links to crawl
Progress: 1/10 pages crawled
Queue size: 5
--------------------------------------------------------------------------------
...
✓ Successfully crawled 10 pages
✓ Extracted 120 products from the pages

Generate human-readable analysis report? (y/n): y
✓ Analysis complete! Check scraped_data_analysis.md
```

### Markdown Report Sample
```markdown
# Web Crawling Analysis Report - Complete Human-Readable Summary

**Report Generated**: October 10, 2025 at 05:49 AM

## Executive Summary

This comprehensive analysis report documents the complete web crawling session 
conducted on October 10, 2025 at 05:41 AM. During this crawling session, 
the system successfully visited and extracted data from 10 web pages...

## Detailed Page-by-Page Analysis

### Page 1 - Complete Analysis

**Location and Basic Information**: This page is located at 
https://books.toscrape.com/catalogue/category/books/fantasy_19/index.html. 
The page carries the title "Fantasy | Books to Scrape - Sandbox". The content 
was extracted on October 10, 2025 at 05:41 AM...

**Product 1: Unicorn Tracks**

The 1st product discovered on this page is titled "Unicorn Tracks". This 
product is currently priced at £18.78. According to the availability information 
extracted from the page, this item is reported as "In stock"...
```

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🙏 Acknowledgments

- **Crawl4AI**: Excellent async web crawling framework
- **Ollama**: Local AI model hosting
- **DeepSeek**: Powerful reasoning model for intelligent navigation
- **BeautifulSoup**: Reliable HTML parsing

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure deepseek-r1:14b model is pulled and running

---

**Version**: 3.0  
**Last Updated**: October 10, 2025  
**Model**: deepseek-r1:14b  
**Python**: 3.8+
