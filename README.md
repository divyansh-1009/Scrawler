# Agentic AI Web Crawler

A truly schema-less, intelligent web crawler powered by AI that adapts to any website and extracts information based on your specific objectives.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Code Structure](#code-structure)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

This crawler uses Large Language Models (LLMs) to intelligently navigate and extract data from websites without requiring hardcoded patterns or specific HTML structures. It's **completely schema-less** and works on any type of website.

### What Makes It Different?

**Traditional Web Scrapers:**
- Require hardcoded CSS selectors or XPath patterns
- Break when website structure changes
- Only work on specific site types
- Manual effort for each new website

**This Agentic Crawler:**
- ✅ No hardcoded patterns needed
- ✅ Works on ANY website structure
- ✅ Adapts to your specific objectives
- ✅ Learns and improves during crawling
- ✅ Intelligent navigation decisions
- ✅ Universal applicability

---

## Key Features

### 🎯 **Goal-Oriented Crawling**
- Tell it what information you want
- AI analyzes your objective and plans the crawl
- Focuses only on relevant content
- Adapts extraction strategy to your needs

### 🧠 **Schema-Less AI Extraction**
- No hardcoded BeautifulSoup patterns
- AI understands page content dynamically
- Adapts to any website structure
- Flexible data extraction

### 📊 **Two-Phase Intelligent Crawling**

**Phase 1: Reconnaissance (10% of pages)**
- Explores site to understand structure
- Identifies page types and patterns
- Learns high-value URL patterns
- Scores pages by relevance

**Phase 2: Targeted Deep Crawl (90% of pages)**
- Focuses on high-relevance sections
- Uses learned patterns to prioritize
- Avoids low-value pages
- Maximizes data quality

### 🔄 **Learning System**
- Learns URL patterns during crawl
- Recognizes valuable page types
- Improves decisions based on findings
- Self-optimizing within session

### 🚀 **Smart Navigation**
- Pre-scores URLs before crawling
- Context-aware link selection
- Balances exploration vs exploitation
- AI-guided navigation decisions

---

## How It Works

### **High-Level Process**

```
1. User Input
   ├─ Website URL
   ├─ Crawl Objective (what to extract)
   └─ Max Pages

2. AI Analyzes Objective
   ├─ Identifies data types to extract
   ├─ Plans extraction strategy
   └─ Determines URL patterns to seek/avoid

3. Phase 1: Reconnaissance
   ├─ Crawls 10% of page budget
   ├─ AI extracts content (no patterns!)
   ├─ Learns valuable URL patterns
   └─ Identifies page types

4. AI Analyzes Site Structure
   ├─ Determines site type
   ├─ Identifies high-value sections
   └─ Plans targeted strategy

5. Phase 2: Targeted Crawl
   ├─ Focuses on high-value areas
   ├─ Pre-scores URLs by relevance
   ├─ AI navigates intelligently
   └─ Continuous learning

6. Output
   ├─ scraped_data.json (extracted data)
   └─ scraped_data_analysis.md (human-readable report)
```

### **Detailed Flow**

#### **1. Objective Analysis**
When you provide an objective like "Product names, prices, and ratings", the AI:
- Identifies data types: `["products", "e-commerce items"]`
- Key fields to extract: `["name", "price", "rating", "availability"]`
- Valuable sections: `["product listings", "category pages"]`
- URL patterns to seek: `["/products/", "/catalogue/"]`
- URL patterns to avoid: `["/login", "/cart", "/checkout"]`

#### **2. AI-Powered Content Extraction**
For each page, the AI:
1. Removes noise (nav, footer, scripts)
2. Extracts main content and structure
3. Analyzes based on your objective
4. Returns:
   - Page type (e.g., "product_listing", "article", "documentation")
   - Relevance score (0-10)
   - Extracted data in flexible schema
   - Reasoning for relevance

#### **3. Intelligent Link Selection**
For each page's links, the system:
1. **Extracts with context**: anchor text, surrounding content, link position
2. **Pre-scores**: Uses heuristics and learned patterns
3. **AI decides**: Selects 3-5 best URLs to crawl next
4. **Considers**: Progress, learned patterns, exploration vs depth

#### **4. Learning System**
Throughout the crawl:
- Tracks relevance scores for all pages
- Identifies high-value URL patterns (e.g., `/products/*`)
- Remembers which page types are valuable
- Uses this knowledge for future decisions

---

## Installation

### **Prerequisites**

1. **Python 3.8+**
2. **Ollama** with deepseek-r1:14b model

### **Setup Steps**

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Ollama:**
   - Download from: https://ollama.ai
   - Install for your operating system

4. **Pull the AI model:**
```bash
ollama pull deepseek-r1:14b
```

### **Dependencies** (in requirements.txt)

```
crawl4ai>=0.3.0
ollama>=0.1.0
asyncio
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

---

## Usage

### **Basic Usage**

```bash
python main.py
```

### **Interactive Prompts**

**1. Enter Website URL:**
```
🌐 Enter the website URL to crawl: https://books.toscrape.com
```

**2. Describe Your Objective:**
```
📝 What information are you looking for?
   Examples:
   - 'Product names, prices, and availability'
   - 'Blog articles with titles and publication dates'
   - 'Documentation pages with code examples'
   - 'Contact information and team member details'

Your objective: Product names, prices, and ratings
```

**3. Set Page Limit:**
```
🔢 Maximum pages to crawl (default: 50): 20
```

### **What Happens Next**

1. **AI analyzes your objective** (~10-30 seconds)
2. **Phase 1: Reconnaissance** (2-5 pages)
3. **AI analyzes site structure** (~10-20 seconds)
4. **Phase 2: Targeted crawl** (remaining pages)
5. **Saves data** to `scraped_data.json`
6. **Optionally generates** human-readable report

### **Output Files**

#### **scraped_data.json**
Clean JSON with only extracted data:
```json
{
  "objective": "Product names, prices, and ratings",
  "extracted_data": [
    {
      "url": "https://example.com/products",
      "extracted_content": {
        "items": [
          {
            "name": "Product Name",
            "price": "$29.99",
            "rating": "4.5/5"
          }
        ]
      },
      "relevance": 9
    }
  ]
}
```

#### **scraped_data_analysis.md** (optional)
Human-readable report with all extracted data formatted nicely:
```markdown
# Extracted Data Analysis Report

**Search Objective**: Product names, prices, and ratings

## Summary
Found 12 pages with relevant information.

## Source 1
**Relevance Score**: 9/10

### Items
### Item 1
**Name**: Product Name
**Price**: $29.99
**Rating**: 4.5/5

**Source URL**: https://example.com/products
```

---

## Architecture

### **Core Components**

#### **1. ImprovedAgenticWebCrawler Class**

Main crawler class that orchestrates the entire process.

**Key Attributes:**
- `crawl_objective`: User's search objective
- `crawl_objective_analysis`: AI's understanding of objective
- `site_understanding`: Learned patterns and site structure
- `page_relevance_scores`: Relevance tracking for all pages
- `high_value_pages`: List of most valuable pages found

**Key Methods:**

##### **analyze_user_objective(objective: str)**
- Uses AI to understand what user wants
- Returns: data types, key fields, URL patterns, strategy

##### **_extract_content_with_ai(html: str, url: str, markdown: str)**
- Schema-less AI extraction
- Adapts to page structure dynamically
- Returns: page type, relevance, extracted content

##### **_extract_links_with_context(html: str, base_url: str)**
- Extracts links with rich context
- Returns: URL, anchor text, surrounding context, position info

##### **_score_url_relevance(link_info: Dict)**
- Pre-scores URLs before crawling
- Uses: learned patterns, historical data, heuristics

##### **_ask_ollama_for_navigation_advanced(...)**
- AI navigation decisions
- Considers: pre-scores, progress, learned patterns
- Returns: 3-5 best URLs to crawl

##### **_crawl_page(url: str, crawler: AsyncWebCrawler)**
- Crawls single page
- Extracts content with AI
- Returns: page data with AI extraction results

##### **_analyze_site_structure()**
- Analyzes reconnaissance results
- Identifies: site type, valuable sections, strategy

##### **crawl_website(start_url: str)**
- Main orchestration method
- Implements two-phase crawling
- Returns: all scraped data

##### **save_to_json(filename: str)**
- Saves only extracted relevant data
- Filters by relevance (≥ 5/10)
- Clean, focused output

#### **2. convert_to_markdown.py**

Converts JSON to human-readable report.

##### **json_to_markdown_complete(json_file: str, output_file: str)**
- Reads scraped_data.json
- Formats all extracted data
- Outputs comprehensive markdown report
- Focuses only on extracted information (no metadata)

##### **_format_content(content: Any, level: int)**
- Recursively formats nested data
- Handles: dicts, lists, primitives
- Creates readable markdown structure

---

## Code Structure

### **File Organization**

```
Latest crawler/
├── main.py                    # Main crawler implementation
├── convert_to_markdown.py     # Report generation
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── scraped_data.json          # Output: Extracted data (generated)
└── scraped_data_analysis.md   # Output: Human-readable report (generated)
```

### **main.py Structure** (~870 lines)

```python
# Imports (lines 1-24)
# - asyncio, json, os, re, datetime
# - ollama, crawl4ai, BeautifulSoup

# ImprovedAgenticWebCrawler Class (lines 27-814)
class ImprovedAgenticWebCrawler:
    # Initialization (lines 32-70)
    def __init__(...)
    
    # Objective Analysis (lines 72-150)
    async def analyze_user_objective(...)
    
    # Helper Methods (lines 152-188)
    def _is_same_domain(...)
    def _extract_url_pattern(...)
    def _find_similar_visited_urls(...)
    
    # AI Content Extraction (lines 190-303)
    async def _extract_content_with_ai(...)
    
    # Learning System (lines 305-327)
    def _update_site_knowledge(...)
    
    # URL Management (lines 329-392)
    def _normalize_url(...)
    async def _extract_links_with_context(...)
    
    # URL Scoring (lines 394-429)
    async def _score_url_relevance(...)
    
    # AI Navigation (lines 431-517)
    async def _ask_ollama_for_navigation_advanced(...)
    
    # Page Crawling (lines 519-576)
    async def _crawl_page(...)
    
    # Site Analysis (lines 578-653)
    async def _analyze_site_structure(...)
    
    # Main Crawl Logic (lines 655-790)
    async def crawl_website(...)
    
    # Data Saving (lines 792-814)
    def save_to_json(...)

# Main Function (lines 817-882)
async def main():
    # User interaction
    # Crawler initialization
    # Execution
    # Report generation

# Entry Point (lines 885-886)
if __name__ == "__main__":
    asyncio.run(main())
```

### **Key Design Patterns**

#### **1. Two-Phase Strategy Pattern**
```python
# Phase 1: Explore
reconnaissance_phase()
analyze_findings()

# Phase 2: Exploit
targeted_deep_crawl()
```

#### **2. Learning System Pattern**
```python
# Learn from each page
extract_content() → score_relevance() → update_knowledge()

# Apply learned knowledge
score_new_url() → use_learned_patterns()
```

#### **3. AI Decision Making Pattern**
```python
# Gather context
context = collect_all_relevant_info()

# AI decides
decision = ai_analyze(context, objective)

# Execute decision
take_action(decision)
```

---

## Configuration

### **Changing AI Models**

Edit lines 852-855 in `main.py`:

**For Speed (Lower Quality):**
```python
crawler = ImprovedAgenticWebCrawler(
    decision_model="tinyllama:latest",
    extraction_model="tinyllama:latest",
    max_pages=max_pages
)
```

**For Balance:**
```python
crawler = ImprovedAgenticWebCrawler(
    decision_model="qwen2.5:7b",
    extraction_model="qwen2.5:7b",
    max_pages=max_pages
)
```

**For Best Quality (Current):**
```python
crawler = ImprovedAgenticWebCrawler(
    decision_model="deepseek-r1:14b",
    extraction_model="deepseek-r1:14b",
    max_pages=max_pages
)
```

**Mixed Approach (Recommended for 8GB+ RAM):**
```python
crawler = ImprovedAgenticWebCrawler(
    decision_model="qwen2.5:7b",        # Strategic decisions
    extraction_model="tinyllama:latest", # Fast extraction
    max_pages=max_pages
)
```

### **Model Comparison**

| Model | Size | Speed | Quality | RAM | Best For |
|-------|------|-------|---------|-----|----------|
| tinyllama:latest | 637MB | Very Fast | Good | 2GB | Testing, low-spec hardware |
| qwen2.5:7b | 4.7GB | Moderate | Excellent | 6GB | Production, balanced |
| deepseek-r1:14b | 8.7GB | Slow | Excellent | 10GB | Complex extraction, reasoning |

### **Adjusting Crawl Parameters**

#### **Reconnaissance Budget** (line 680)
```python
# Current: 10% of pages
recon_budget = max(5, self.max_pages // 10)

# More thorough (slower): 15%
recon_budget = max(5, self.max_pages // 7)

# Faster (less thorough): 5%
recon_budget = max(3, self.max_pages // 20)
```

#### **Relevance Threshold** (line 799)
```python
# Current: Include pages with relevance ≥ 5
if page.get('relevance_score', 0) >= 5:

# More strict: Only high-relevance pages
if page.get('relevance_score', 0) >= 7:

# More inclusive: Include more pages
if page.get('relevance_score', 0) >= 3:
```

#### **Content Analysis Size** (line 213)
```python
# Current: 4000 characters
content_to_analyze = markdown[:4000]

# More context (slower)
content_to_analyze = markdown[:6000]

# Less context (faster)
content_to_analyze = markdown[:2000]
```

---

## Examples

### **Example 1: E-Commerce Product Extraction**

**Input:**
```
URL: https://books.toscrape.com
Objective: Product names, prices, ratings, and availability
Max Pages: 20
```

**Process:**
1. AI identifies: e-commerce site, looking for product data
2. Reconnaissance finds: product listings and category pages
3. Learns pattern: `/catalogue/category/*` = high value
4. Targeted crawl: Focuses on product pages
5. Extracts: 40+ products with all requested fields

**Output (scraped_data.json):**
```json
{
  "objective": "Product names, prices, ratings, and availability",
  "extracted_data": [
    {
      "url": "https://books.toscrape.com/catalogue/category/books_1/index.html",
      "extracted_content": {
        "items": [
          {
            "title": "A Light in the Attic",
            "price": "£51.77",
            "rating": "Three stars",
            "availability": "In stock"
          },
          {
            "title": "Tipping the Velvet",
            "price": "£53.74",
            "rating": "One star",
            "availability": "In stock"
          }
        ]
      },
      "relevance": 9
    }
  ]
}
```

### **Example 2: Blog Article Extraction**

**Input:**
```
URL: https://blog.example.com
Objective: Article titles, authors, publication dates, and summaries
Max Pages: 15
```

**Process:**
1. AI identifies: blog/news site, looking for article metadata
2. Reconnaissance finds: article pages and archive listings
3. Learns pattern: `/blog/2024/*` = high value
4. Targeted crawl: Focuses on article pages
5. Extracts: Metadata from all articles

**Output Structure:**
```json
{
  "objective": "Article titles, authors, dates, summaries",
  "extracted_data": [
    {
      "url": "https://blog.example.com/article-1",
      "extracted_content": {
        "article": {
          "title": "Understanding AI",
          "author": "John Doe",
          "date": "2024-01-15",
          "summary": "An introduction to..."
        }
      },
      "relevance": 8
    }
  ]
}
```

### **Example 3: Documentation Extraction**

**Input:**
```
URL: https://docs.example.com
Objective: API endpoints with parameters and code examples
Max Pages: 25
```

**Process:**
1. AI identifies: documentation site, looking for API details
2. Reconnaissance finds: API reference pages
3. Learns pattern: `/api/reference/*` = high value
4. Targeted crawl: Focuses on endpoint documentation
5. Extracts: Endpoints, parameters, examples

### **Example 4: Contact Information**

**Input:**
```
URL: https://company.example.com
Objective: Team member names, titles, and email addresses
Max Pages: 10
```

**Process:**
1. AI identifies: business site, looking for contact info
2. Reconnaissance finds: about page, team page
3. Learns pattern: `/about/*`, `/team/*` = high value
4. Targeted crawl: Focuses on people pages
5. Extracts: Contact information

---

## Troubleshooting

### **Common Issues**

#### **1. "Model not found" Error**

**Problem:** Ollama model not installed

**Solution:**
```bash
ollama pull deepseek-r1:14b
```

Verify installation:
```bash
ollama list
```

#### **2. Crawler Hangs on "Analyzing objective"**

**Problem:** Model is slow or system is low on resources

**Solutions:**
- Switch to faster model (tinyllama)
- Close other applications
- Increase available RAM
- Wait longer (deepseek-r1 can take 30-60 seconds)

#### **3. "JSON parsing error"**

**Problem:** AI returned malformed JSON

**Solution:** 
- This is handled automatically with fallback extraction
- Results are still useful
- Consider using more reliable model (qwen2.5:7b)

#### **4. No Data Extracted**

**Problem:** Pages not matching objective or low relevance

**Solutions:**
- Make objective more specific
- Try different URL
- Increase page count
- Lower relevance threshold in code (line 799)

#### **5. Slow Crawling**

**Problem:** Model taking long time per page

**Solutions:**
1. Use faster model:
   ```python
   decision_model="tinyllama:latest"
   extraction_model="tinyllama:latest"
   ```

2. Reduce content size (line 213):
   ```python
   content_to_analyze = markdown[:2000]
   ```

3. Reduce page count:
   ```
   Max pages: 10
   ```

#### **6. Memory Errors**

**Problem:** Not enough RAM for model

**Solutions:**
- Close other applications
- Use smaller model (tinyllama or qwen2.5:3b)
- Reduce max pages
- Restart Ollama service

#### **7. Connection Errors**

**Problem:** Can't reach website

**Solutions:**
- Check internet connection
- Verify URL is correct
- Try different website
- Check if site blocks scrapers (use robots.txt)

### **Debugging Tips**

#### **Enable Verbose Output**

In `main.py`, line 686:
```python
async with AsyncWebCrawler(verbose=True) as crawler:
```

#### **Check Ollama Logs**

```bash
# Check if Ollama is running
ollama list

# Test model directly
ollama run deepseek-r1:14b "Hello"
```

#### **Reduce Complexity**

Start with small tests:
```
Max pages: 5
Objective: Just product names
```

#### **Check Output Files**

After crawl:
1. Check `scraped_data.json` exists
2. Verify it has `extracted_data` array
3. Check relevance scores
4. Review extracted content structure

---

## Technical Details

### **AI Model Usage**

#### **1. Objective Analysis**
- **Input:** User's objective description
- **Process:** AI parses intent and plans strategy
- **Output:** Data types, key fields, URL patterns
- **Frequency:** Once per crawl

#### **2. Content Extraction**
- **Input:** Page HTML/markdown + objective
- **Process:** AI identifies relevant data
- **Output:** Page type, relevance, structured content
- **Frequency:** Once per page crawled

#### **3. Site Structure Analysis**
- **Input:** Reconnaissance results summary
- **Process:** AI identifies site type and valuable sections
- **Output:** Site type, valuable page types, strategy
- **Frequency:** Once after reconnaissance

#### **4. Navigation Decisions**
- **Input:** Pre-scored URLs + crawl context
- **Process:** AI selects best URLs to crawl
- **Output:** 3-5 URLs to visit next
- **Frequency:** After each page in deep crawl phase

### **Performance Characteristics**

**Time Estimates (deepseek-r1:14b on mid-range hardware):**
- Objective analysis: 10-30 seconds
- Page extraction: 15-30 seconds per page
- Site analysis: 10-20 seconds
- Navigation decision: 10-20 seconds

**Total for 20 pages:** ~10-20 minutes

**With tinyllama:latest:**
- Objective analysis: 5-10 seconds
- Page extraction: 3-5 seconds per page
- Total for 20 pages: ~3-5 minutes

### **Data Flow**

```
User Input
    ↓
Objective Analysis (AI) → Strategy
    ↓
Phase 1: Reconnaissance
    ├→ Crawl Page → AI Extract → Update Knowledge
    ├→ Crawl Page → AI Extract → Update Knowledge
    └→ Crawl Page → AI Extract → Update Knowledge
    ↓
Site Analysis (AI) → Refined Strategy
    ↓
Phase 2: Targeted Crawl
    ├→ Pre-score URLs → AI Select → Crawl → Extract
    ├→ Pre-score URLs → AI Select → Crawl → Extract
    └→ Pre-score URLs → AI Select → Crawl → Extract
    ↓
Save to JSON (filtered by relevance)
    ↓
Generate Report (optional)
```

---

## Advanced Usage

### **Programmatic Usage**

```python
import asyncio
from main import ImprovedAgenticWebCrawler

async def custom_crawl():
    # Initialize crawler
    crawler = ImprovedAgenticWebCrawler(
        decision_model="deepseek-r1:14b",
        extraction_model="deepseek-r1:14b",
        max_pages=30
    )
    
    # Set objective
    crawler.crawl_objective = "Product prices and descriptions"
    
    # Analyze objective
    await crawler.analyze_user_objective(crawler.crawl_objective)
    
    # Crawl
    results = await crawler.crawl_website("https://example.com")
    
    # Save
    json_file = crawler.save_to_json("my_data.json")
    
    # Access results directly
    for page in results:
        print(f"URL: {page['url']}")
        print(f"Relevance: {page['relevance_score']}")
        print(f"Content: {page['ai_extraction']['key_content']}")
        print("---")

# Run
asyncio.run(custom_crawl())
```

### **Custom Processing**

```python
# After crawling
crawler = ImprovedAgenticWebCrawler(...)
results = await crawler.crawl_website(url)

# Filter by high relevance
high_quality = [p for p in results if p['relevance_score'] >= 8]

# Extract specific data type
products = []
for page in results:
    content = page.get('ai_extraction', {}).get('key_content', {})
    if 'items' in content:
        products.extend(content['items'])

# Custom analysis
print(f"Total products found: {len(products)}")
```

---

## License

This project is provided as-is for educational and commercial use.

---

## Credits

**Technologies Used:**
- [Crawl4AI](https://github.com/unclecode/crawl4ai) - Async web crawling
- [Ollama](https://ollama.ai) - Local LLM inference
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [DeepSeek](https://www.deepseek.com/) - AI model

---

## Summary

This Agentic AI Web Crawler represents a new approach to web scraping:

✅ **No hardcoded patterns** - Works on any site structure
✅ **Goal-driven** - Adapts to your specific needs
✅ **Intelligent** - Learns and improves during crawl
✅ **Universal** - E-commerce, blogs, docs, any content type
✅ **Clean output** - Only relevant extracted data
✅ **Production-ready** - Robust error handling and fallbacks

**Perfect for:**
- Dynamic data extraction projects
- Research and data collection
- Competitive intelligence
- Content aggregation
- API alternative for websites without APIs

**Get started:**
```bash
python main.py
```

And let AI handle the complexity of web scraping! 🚀
