# 🤖 Agentic AI Web Crawler

An intelligent, schema-less web crawler powered by Large Language Models (LLMs) that understands your objectives and automatically extracts relevant information from websites.

## 🌟 What Makes This Special?

Unlike traditional web scrapers that require predefined extraction rules, this crawler:

- **Understands Natural Language**: Tell it what you want in plain English
- **AI-Powered Navigation**: Decides which links to follow based on relevance
- **Schema-less Extraction**: Adapts to any website structure automatically
- **Section-Based Analysis**: Scores each page section independently for surgical precision
- **Smart Link Filtering**: Intelligently selects relevant links using heuristics and AI
- **Parallel Processing**: 2-3x faster with concurrent page crawling
- **Intelligent Screening**: Evaluates content quality with 0-10 relevance scoring
- **Comprehensive Answers**: Generates detailed, human-readable responses to your questions

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Detailed Functionality](#-detailed-functionality)
- [Configuration](#️-configuration)
- [Output Files](#-output-files)
- [Advanced Usage](#-advanced-usage)
- [Performance & Optimization](#-performance--optimization)
- [Troubleshooting](#-troubleshooting)
- [Best Practices](#-best-practices)

## 🔧 Prerequisites

### Required Software

1. **Python 3.8+**
   - Download from: https://python.org

2. **Ollama** (Local LLM Runtime)
   - Download from: https://ollama.com
   - Required for running AI models locally

3. **DeepSeek R1 14B Model** (or alternative)
   ```bash
   ollama pull deepseek-r1:14b
   ```
   - Model size: ~8.7GB
   - RAM requirement: ~16GB recommended

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 16GB
- Storage: 15GB free space
- OS: Windows, macOS, or Linux

**Recommended:**
- CPU: 8+ cores
- RAM: 32GB
- GPU: NVIDIA GPU with CUDA support (optional, for faster inference)
- Storage: 20GB+ free space

## 📦 Installation

Choose your preferred installation method:

### 🐳 Option 1: Docker (Recommended - Easiest Setup)

**Prerequisites**: 
- Docker and Docker Compose installed
- 16GB+ RAM for DeepSeek R1 model
- 20GB+ free disk space

**Quick Start**:
```bash
# Clone the repository
git clone <repository-url>
cd Scrawler

# Start everything with one command
sudo docker compose up --build -d

# Pull AI models (takes 5-15 minutes)
sudo docker exec scrawler-ollama ollama pull deepseek-r1:14b
sudo docker exec scrawler-ollama ollama pull qwen2.5:7b

# Run the crawler
sudo docker exec -it scrawler-app python agentic_crawler.py
```

**What Docker Sets Up**:
- ✅ Isolated Python environment with all dependencies
- ✅ Ollama server with model management  
- ✅ Playwright browsers pre-installed
- ✅ Persistent data volumes for output
- ✅ No conflicts with your system

### 🔧 Option 2: Native Installation

**Step 1: Clone or Download**

Download the project files:
- `agentic_crawler.py` - Main crawler script with all optimizations
- `requirements.txt` - Python dependencies
- `web_crawler_colab.ipynb` - Google Colab version (GPU-accelerated)

**Step 2: Install Python Dependencies**

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install crawl4ai>=0.3.0 ollama>=0.1.0 aiohttp>=3.9.0 beautifulsoup4>=4.12.0 lxml>=4.9.0 requests>=2.31.0
```

**Step 3: Install Playwright Browsers**

Crawl4AI uses Playwright for browser automation:

```bash
playwright install chromium
```

On Linux, install system dependencies:
```bash
playwright install-deps chromium
```

**Step 4: Install and Setup Ollama**

Install Ollama:
```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com
```

Start Ollama server:
```bash
ollama serve
```

Pull required models:
```bash
ollama pull deepseek-r1:14b  # Primary model (8.7GB)
ollama pull qwen2.5:7b       # Backup model (4.4GB)
```

Verify installation:
```bash
ollama list
```

You should see both models in the list.

## 🚀 Quick Start

### 🐳 Docker Usage (Recommended)

1. **Start Services**:
   ```bash
   sudo docker compose up --build -d
   ```

2. **Pull AI Models** (first time only):
   ```bash
   sudo docker exec scrawler-ollama ollama pull deepseek-r1:14b
   ```

3. **Run the Crawler**:
   ```bash
   sudo docker exec -it scrawler-app python agentic_crawler.py
   ```

4. **Access Output Files**:
   - Files saved to `./output/` directory on your host machine
   - `scraped_data.json` - Raw extracted data  
   - `ai_answer.md` - Comprehensive AI-generated answer

### 🔧 Native Usage

1. **Start Ollama** (in one terminal):
   ```bash
   ollama serve
   ```

2. **Run the Crawler** (in another terminal):
   ```bash
   python agentic_crawler.py
   ```

3. **Provide Inputs**:
   - **URL**: `https://example.com`
   - **Objective**: `"Find all product names and prices"`
   - **Max Pages**: `50` (or press Enter for default)
   - **Concurrency**: `3` (or press Enter for default - higher = faster)

4. **Wait for Results**: The crawler will process and generate files:
   - `scraped_data.json` - Raw extracted data
   - `ai_answer.md` - Comprehensive answer to your question

### Example Session

```
🤖 AGENTIC WEB CRAWLER - LOCAL EDITION
================================================================================

🌐 Enter the website URL to crawl: https://example-shop.com

📝 What information are you looking for?
Your objective: Find all laptop models with their specifications and prices

🔢 Maximum pages to crawl (default: 50): 30

⚡ Concurrency settings:
   Higher = Faster but more resource intensive
   Recommended: 2-5 for most systems
🔢 Concurrent pages to process (default: 3): 3

🤖 Analyzing your objective with AI...
✓ Objective Analysis Complete:
  • Data Types: products, electronics
  • Key Fields: model_name, specifications, price, availability
  • Focus Areas: product pages, category listings

📡 PHASE 1: RECONNAISSANCE (3 pages)
────────────────────────────────────────────────────────────────────────────────
🔄 Processing batch of 3 pages...
📄 Crawling: https://example-shop.com
  ✓ Type: homepage | Relevance: 6/10 | Sections: 4
  → 1 high-value section(s) found
  → Smart filter: 32 links → 8 relevant
  Progress: 3/3 recon pages
...

🎯 PHASE 2: TARGETED DEEP CRAWL (27 pages)
────────────────────────────────────────────────────────────────────────────────
🔗 Seeding deep crawl queue from high-value pages...
  ✓ Queue seeded with 23 promising links

📄 Crawling: https://example-shop.com/laptops
  ✓ Type: product listing | Relevance: 9/10 | Sections: 5
  → 3 high-value section(s) found
  → AI selected 4 links
...

✅ CRAWL COMPLETE
================================================================================
Total pages: 30
High-value pages: 18
Avg relevance: 7.2/10

🤖 Analyzing all scraped data to answer your question...
📊 Processing 18 pages of extracted content...

✨ COMPREHENSIVE ANSWER TO YOUR QUESTION
================================================================================
[Detailed answer with all laptop models, specs, and prices]

✅ Saved: scraped_data.json
✅ Saved: ai_answer.md

🎉 CRAWLING AND ANALYSIS COMPLETE!
```

## 🧠 How It Works

### Architecture Overview

The crawler uses a sophisticated multi-phase approach:

```
┌─────────────────────────────────────────────────────────────┐
│  1. OBJECTIVE ANALYSIS                                      │
│  AI analyzes your question to understand:                   │
│  • What data types you need                                 │
│  • What fields to extract                                   │
│  • What URL patterns to seek/avoid                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PHASE 1: RECONNAISSANCE (10% of pages)                  │
│  • Explores diverse areas of the website                    │
│  • AI evaluates each page's relevance (0-10 scale)          │
│  • Learns high-value URL patterns                           │
│  • Identifies content types and structure                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. SITE STRUCTURE ANALYSIS                                 │
│  AI analyzes reconnaissance data:                           │
│  • Determines website type                                  │
│  • Identifies most valuable sections                        │
│  • Recommends focused crawl strategy                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. PHASE 2: TARGETED DEEP CRAWL (90% of pages)             │
│  • Focuses on high-value areas from Phase 1                 │ 
│  • AI-guided link selection                                 │
│  • Prioritizes relevant content                             │
│  • Extracts comprehensive data                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. AI-POWERED ANSWER GENERATION                            │
│  • Analyzes all extracted data (pages with 4+ relevance)    │
│  • Generates comprehensive answer to your question          │
│  • Includes all relevant details and findings               │
│  • Assesses data completeness                               │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Objective Analyzer
- **Purpose**: Understand what the user is asking for
- **Process**: 
  - Sends user's objective to LLM
  - Extracts data types, key fields, valuable sections
  - Identifies URL patterns to seek/avoid
- **Output**: Strategic crawl plan

#### 2. Content Extractor (Section-Based) ✨ NEW
- **Purpose**: Extract relevant information with surgical precision
- **Process**:
  1. Identifies distinct sections on page (semantic HTML or content divs)
  2. AI scores EACH section independently (0-10)
  3. Extracts only from relevant sections (4+ score)
  4. Overall page relevance = highest section score
- **AI Evaluation**: Scores each section 0-10 for relevance
  - **9-10**: Directly answers objective with specific details
  - **7-8**: Significant relevant information
  - **5-6**: Moderately relevant
  - **3-4**: Tangentially related
  - **1-2**: Barely related
  - **0**: Completely irrelevant
- **Adaptive Extraction**:
  - High sections (7+): Extract everything in detail
  - Medium sections (4-6): Extract key points
  - Low sections (0-3): Skip entirely (no extraction)
- **Benefit**: Reduces noise, focuses on truly relevant content

#### 3. Smart Link Selection ✨ NEW
- **Purpose**: Intelligently filter and prioritize links before crawling
- **Heuristic Scoring**:
  - Penalizes low-value pages (privacy, login, cart) -3 points
  - Boosts main content links +2 points
  - Boosts prominent links (in headers) +1.5 points
  - Boosts objective keyword matches +2 points
  - Ensures diversity (max 2 links per URL pattern)
- **During Reconnaissance**: Selects top 8 links by score
- **During Deep Crawl**: AI refines selection from pre-scored candidates
- **Benefit**: Avoids wasting budget on irrelevant pages

#### 4. Navigation AI
- **Purpose**: Final decision on which links to follow (deep crawl only)
- **Method**:
  - Pre-scores links using heuristics
  - Presents top candidates to LLM
  - LLM selects 3-5 most promising URLs
- **Learning**: Improves decisions based on discovered patterns

#### 5. Site Knowledge System
- **Tracks**:
  - High-value URL patterns (e.g., `/products/*/details`)
  - Content types and their average relevance
  - Successful navigation paths
- **Benefits**: Improves accuracy as crawling progresses

#### 6. Parallel Processing ⚡ NEW
- **Purpose**: Speed up crawling without changing logic
- **Features**:
  - Concurrent page crawling (configurable 1-10 pages)
  - Async AI calls using thread pool
  - Batch link extraction (5 pages at once)
  - Parallel queue seeding
- **Performance**: 2-3x faster than sequential processing
- **Configurable**: Adjust concurrency based on system resources

#### 7. Answer Generator
- **Purpose**: Create comprehensive answer to user's question
- **Process**:
  - Compiles data from all relevant pages (4+ relevance)
  - Analyzes up to 20 pages in detail
  - Generates structured, detailed response
  - Assesses completeness of findings

## 🔬 Detailed Functionality

### Phase 1: Reconnaissance

**Objective**: Understand the website structure

**Budget**: 10% of max_pages (minimum 5)

**Process**:
1. Start from the provided URL
2. Extract and evaluate content with AI
3. Follow 8 diverse links per page
4. Score each page for relevance
5. Learn URL patterns that lead to valuable content

**Example**:
```python
# For max_pages=50
recon_budget = max(5, 50 // 10)  # = 5 pages
```

**Output**:
- Visited URLs
- Relevance scores
- High-value URL patterns discovered
- Content type distribution

### Phase 2: Targeted Deep Crawl

**Objective**: Collect comprehensive data from relevant areas

**Budget**: 90% of max_pages

**Process**:
1. Build initial queue from pages scoring 5+ in reconnaissance
2. Extract links from high-value pages
3. For each page:
   - Extract content with AI
   - Get contextual information about links
   - AI selects 3-5 best links to follow
4. Prioritize:
   - Pages matching learned high-value patterns
   - Links from highly relevant pages
   - URLs matching objective's seek patterns

**Example**:
```python
# Only follow links from pages scoring 5+
if page.get('relevance_score', 0) >= 5:
    # Extract up to 7 links per page
    for link in links[:7]:
        url_queue.append(link['url'])
```

### AI Prompting Strategy

#### Objective Analysis Prompt
```
Analyze user's objective: "Find product prices"

Determine:
1. Data types needed (products, pricing)
2. Key fields (name, price, currency, stock)
3. Valuable sections (product pages, catalogs)
4. URL patterns to seek (/products/, /items/)
5. URL patterns to avoid (/login/, /cart/)
```

#### Content Extraction Prompt
```
Page URL: https://example.com/product/123

Objective: Find product prices

Task:
1. Understand what user is asking for
2. Rate relevance 0-10 (be accurate, not generous)
3. Extract based on relevance:
   - High (7+): Everything in detail
   - Moderate (4-6): Key points
   - Low (1-3): Only specific relevant parts
4. Explain reasoning for score
```

#### Navigation Decision Prompt
```
Current page: Product listing (relevance: 8/10)

Top candidate links:
1. [7.5] Product A Details → /products/a/details
2. [7.2] Product B Details → /products/b/details
3. [6.8] Reviews → /products/a/reviews
4. [5.1] About Us → /about
...

Select 3-5 URLs that best match objective.
Respond with numbers: "1,2,3"
```

### Relevance Scoring System

**Thresholds Used**:
- **High-value pages**: 6+ (tracked for pattern learning)
- **Deep crawl trigger**: 5+ (pages to extract links from)
- **Links per page**: 7 (balance breadth vs depth)
- **Final analysis**: 4+ (included in AI answer)

**Why These Thresholds**:
- Balances comprehensiveness with quality
- Reduces noise while maintaining coverage
- Empirically tested for best results
- Adapts to improved AI accuracy

### Data Flow

```
User Input
    ↓
Objective Analysis (LLM)
    ↓
Start URL → Reconnaissance Phase
    ↓
For each page:
    HTML → BeautifulSoup → Clean Text
    ↓
    Clean Text → LLM → {
        page_type,
        relevance_score,
        key_content,
        reasoning,
        summary
    }
    ↓
    Update Site Knowledge
    ↓
    Extract Links with Context
    ↓
    AI Selects Next URLs
    ↓
Deep Crawl Phase (repeat above)
    ↓
All Extracted Data
    ↓
AI Answer Generation
    ↓
Output Files (JSON + Markdown)
```

## ⚙️ Configuration

### Model Selection

Change the AI model by editing the script:

```python
crawler = ImprovedAgenticWebCrawler(
    decision_model="qwen2.5:7b",     # For navigation decisions
    extraction_model="qwen2.5:7b",   # For content extraction
    max_pages=50,
    concurrency=3  # ✨ NEW: Pages to process concurrently (1-10)
)
```

**Recommended Models**:

| Model | Size | RAM | Speed | Quality | Use Case |
|-------|------|-----|-------|---------|----------|
| deepseek-r1:14b | 8.7GB | 16GB | Slow | Excellent | Best quality |
| qwen2.5:7b | 4.4GB | 8GB | Medium | Very Good | Balanced |
| llama3:8b | 4.7GB | 8GB | Medium | Good | General use |
| mistral:7b | 4.1GB | 8GB | Fast | Good | Speed priority |
| tinyllama:1b | 0.6GB | 2GB | Very Fast | Basic | Testing/low memory |

### Crawl Parameters

```python
# In main() function or when initializing
max_pages = 100  # Crawl more pages
concurrency = 5  # ✨ NEW: Process more pages in parallel (faster but more resource-intensive)

# Concurrency Guidelines:
# - 1-2: Conservative (low-end PC, slow connection)
# - 3-4: Balanced (recommended for most systems)
# - 5-7: Aggressive (powerful PC, fast internet)
# - 8-10: Maximum (server-grade hardware only)

# In crawler class
recon_budget = max(10, max_pages // 5)  # More reconnaissance

# Link extraction
for link in links[:10]:  # Follow more links per page
```

### Relevance Thresholds

**Current (Balanced)**:
```python
if relevance >= 6:  # High-value pages
if page.get('relevance_score', 0) >= 5:  # Deep crawl
all_pages = [p for p in scraped_data if p.get('relevance_score', 0) >= 4]  # Analysis
```

**More Comprehensive** (slower, more data):
```python
if relevance >= 5:  # High-value pages
if page.get('relevance_score', 0) >= 4:  # Deep crawl
all_pages = [p for p in scraped_data if p.get('relevance_score', 0) >= 3]  # Analysis
```

**More Selective** (faster, higher quality):
```python
if relevance >= 7:  # High-value pages
if page.get('relevance_score', 0) >= 6:  # Deep crawl
all_pages = [p for p in scraped_data if p.get('relevance_score', 0) >= 5]  # Analysis
```

## 📄 Output Files

### 1. scraped_data.json

**Structure**:
```json
{
  "objective": "Find product prices",
  "total_pages_crawled": 50,
  "high_value_pages": 28,
  "extracted_data": [
    {
      "url": "https://example.com/product/laptop-x",
      "page_type": "product page",
      "relevance": 9,
      "extracted_content": {
        "product_name": "Laptop X Pro",
        "specifications": {
          "cpu": "Intel i7",
          "ram": "16GB",
          "storage": "512GB SSD"
        },
        "price": "$1299",
        "availability": "In Stock"
      }
    },
    ...
  ]
}
```

**Use Cases**:
- Feed data to other systems
- Further processing with custom scripts
- Database import
- API responses

### 2. ai_answer.md

**Structure**:
```markdown
# AI-Generated Answer

**Question/Objective**: Find product prices

**Generated**: January 15, 2025 at 02:30 PM

---

## DIRECT ANSWER

Found 45 products with pricing information across 28 relevant pages...

## COMPLETE FINDINGS

### Laptops
1. **Laptop X Pro** - $1,299
   - Specifications: Intel i7, 16GB RAM, 512GB SSD
   - Availability: In Stock
   ...

### SUPPORTING DETAILS
...

### DATA COMPLETENESS
The crawl successfully found pricing for all major product categories...

### CONCLUSION
...
```

**Use Cases**:
- Human-readable reports
- Documentation
- Stakeholder presentations
- Knowledge base articles

## 🚀 Advanced Usage

### Programmatic Usage

Use the crawler in your own Python scripts:

```python
import asyncio
from agentic_crawler_local import (
    ImprovedAgenticWebCrawler,
    generate_ai_answer,
    save_results
)

async def custom_crawl():
    # Initialize
    crawler = ImprovedAgenticWebCrawler(
        decision_model="deepseek-r1:14b",
        extraction_model="deepseek-r1:14b",
        max_pages=30
    )
    
    # Set objective
    crawler.crawl_objective = "Find contact information for team members"
    
    # Analyze objective
    analysis = await crawler.analyze_user_objective(crawler.crawl_objective)
    print(f"Will look for: {analysis['data_types']}")
    
    # Crawl
    scraped_data = await crawler.crawl_website("https://example.com")
    
    # Access data directly
    for page in scraped_data:
        if page['relevance_score'] >= 7:
            print(f"High-value: {page['url']}")
            print(f"Content: {page['ai_extraction']['key_content']}")
    
    # Generate answer
    ai_summary = await generate_ai_answer(scraped_data, crawler.crawl_objective)
    
    # Save results
    save_results(scraped_data, ai_summary, crawler.crawl_objective, output_dir="./results")

# Run
asyncio.run(custom_crawl())
```

### Batch Crawling

Crawl multiple websites:

```python
async def batch_crawl(urls, objective, max_pages=30):
    results = {}
    
    for url in urls:
        print(f"\n{'='*80}")
        print(f"Crawling: {url}")
        print(f"{'='*80}\n")
        
        crawler = ImprovedAgenticWebCrawler(max_pages=max_pages)
        crawler.crawl_objective = objective
        
        await crawler.analyze_user_objective(objective)
        data = await crawler.crawl_website(url)
        
        results[url] = {
            'pages_crawled': len(data),
            'high_value_pages': len([p for p in data if p['relevance_score'] >= 6]),
            'avg_relevance': sum(p['relevance_score'] for p in data) / len(data)
        }
    
    return results

# Usage
urls = [
    "https://competitor1.com",
    "https://competitor2.com",
    "https://competitor3.com"
]
results = asyncio.run(batch_crawl(urls, "Find pricing information", max_pages=20))
```

### Custom Prompts

Modify AI behavior by editing prompts in the script:

```python
# In _extract_content_with_ai method
prompt = f"""You are a specialized product data extractor.

Focus ONLY on:
- Product names
- Prices (in any currency)
- Stock availability

Ignore:
- Reviews
- Related products
- Advertisements

...
"""
```

### Integration with APIs

Send results to an API:

```python
import requests

async def crawl_and_send():
    crawler = ImprovedAgenticWebCrawler(max_pages=20)
    crawler.crawl_objective = "Extract product data"
    
    await crawler.analyze_user_objective(crawler.crawl_objective)
    data = await crawler.crawl_website("https://example.com")
    
    # Prepare for API
    products = []
    for page in data:
        if page['relevance_score'] >= 6:
            content = page['ai_extraction']['key_content']
            products.append(content)
    
    # Send to API
    response = requests.post(
        "https://api.example.com/products",
        json={"products": products}
    )
    
    print(f"API Response: {response.status_code}")

asyncio.run(crawl_and_send())
```

## 📊 Performance & Optimization

### ⚡ NEW: Parallel Processing

The crawler now features **built-in parallelization** for 2-3x faster execution:

**Before Optimizations** (Sequential):
- DeepSeek R1 14B: ~6 seconds per page
- 50 pages: ~5 minutes total

**After Optimizations** (concurrency=3, default):
- DeepSeek R1 14B: ~2 seconds effective per page
- 50 pages: ~2.5 minutes total
- **Speedup: 2x faster**

**With Higher Concurrency** (concurrency=5):
- DeepSeek R1 14B: ~1.5 seconds effective per page
- 50 pages: ~1.6 minutes total
- **Speedup: 3x faster**

**How It Works:**
- Multiple pages crawled concurrently
- AI calls run in parallel using thread pool
- Batch link extraction (5 pages at once)
- No logic changes - same quality, faster execution

### Performance Metrics by Model

**DeepSeek R1 14B** (CPU, concurrency=3):
- Time per page: 5-8 seconds (effective: 2-3s with parallelization)
- 50 pages: ~2.5 minutes with parallel processing
- Memory: ~16GB peak
- Quality: Excellent

**Qwen 2.5 7B** (CPU, concurrency=3):
- Time per page: 3-5 seconds (effective: 1-2s with parallelization)
- 50 pages: ~1.5 minutes with parallel processing
- Memory: ~8GB peak
- Quality: Very Good

**With GPU** (NVIDIA):
- Additional 2-3x faster inference
- DeepSeek: 2-3 seconds/page → under 1s effective
- Qwen: 1-2 seconds/page → under 0.5s effective

### Optimization Tips

#### 1. Use Appropriate Model
```python
# For testing/development
decision_model="qwen2.5:7b"

# For production/best quality
decision_model="deepseek-r1:14b"
```

#### 2. Adjust Crawl Depth
```python
# Quick scan (10-15 pages)
max_pages=15

# Balanced (30-50 pages)
max_pages=40

# Comprehensive (100+ pages)
max_pages=100
```

#### 3. Limit Context Size
```python
# In _extract_content_with_ai
content_to_analyze = markdown[:3000]  # Reduced from 4000

# In generate_ai_answer
context[:12000]  # Reduced from 15000
```

#### 4. Adjust Concurrency ✨ NEW
```python
# Conservative (slow connection, low-end PC)
concurrency=2  # Still 2x faster than sequential

# Balanced (recommended for most systems)
concurrency=3  # 2-3x faster, good resource usage

# Aggressive (powerful PC, fast internet)
concurrency=5  # 3x faster, higher memory usage

# Maximum (server-grade hardware)
concurrency=8  # Maximum speed, highest resource usage
```

**Note:** Concurrency is now built-in! No need for custom parallel code.

### Memory Management

**Monitor Memory**:
```python
import psutil

def check_memory():
    mem = psutil.virtual_memory()
    print(f"Memory usage: {mem.percent}%")
    print(f"Available: {mem.available / 1024**3:.1f} GB")

# Call periodically
check_memory()
```

**Reduce Memory Usage**:
1. Use smaller model (qwen2.5:7b)
2. Lower max_pages
3. Process in batches
4. Clear crawler cache periodically

## 🔧 Troubleshooting

### Common Issues

#### 1. Ollama Connection Error

**Error**: `Could not connect to Ollama`

**Solutions**:
```bash
# Check if Ollama is running
ps aux | grep ollama  # Linux/Mac
tasklist | findstr ollama  # Windows

# Start Ollama
ollama serve

# Check connectivity
curl http://localhost:11434/api/tags
```

#### 2. Model Not Found

**Error**: `model 'deepseek-r1:14b' not found`

**Solutions**:
```bash
# List available models
ollama list

# Pull the model
ollama pull deepseek-r1:14b

# Verify
ollama list | grep deepseek
```

#### 3. Out of Memory

**Error**: `Out of memory` or system freeze

**Solutions**:
1. Close other applications
2. Use smaller model:
   ```python
   decision_model="qwen2.5:7b"
   ```
3. Reduce max_pages:
   ```python
   max_pages=20
   ```
4. Add swap space (Linux)
5. Restart Ollama:
   ```bash
   pkill ollama
   ollama serve
   ```

#### 4. Playwright Browser Error

**Error**: `Executable doesn't exist`

**Solutions**:
```bash
# Install browsers
playwright install chromium

# Linux: Install dependencies
playwright install-deps chromium

# Verify
playwright --version
```

#### 5. Slow Performance

**Symptoms**: Takes > 30 seconds per page

**Solutions**:
1. Use faster model (qwen2.5:7b)
2. Use GPU if available
3. Reduce context size in prompts
4. Check system resources
5. Close background applications

#### 6. JSON Parsing Errors

**Error**: `JSON decode error`

**Cause**: LLM response not valid JSON

**Solutions**:
- Already handled in code with fallback
- If persistent, try different model
- Check Ollama logs for issues

#### 7. Website Blocks Requests

**Error**: 403 Forbidden or similar

**Solutions**:
1. Add delays between requests (not implemented by default)
2. Check robots.txt compliance
3. Use different user agent (requires code modification)
4. Website may not allow scraping

### Debug Mode

Enable verbose output:

```python
# In crawl_website method
async with AsyncWebCrawler(verbose=True) as crawler:  # Set to True
    ...
```

### Logging

Add custom logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# In your code
logger.info(f"Crawling: {url}")
logger.error(f"Failed: {error}")
```

## 💡 Best Practices

### 1. Objective Formulation

**Good Objectives** (Specific):
- ✅ "Find all product names with their prices and stock availability"
- ✅ "Extract blog post titles, authors, and publication dates"
- ✅ "Collect team member names, roles, and contact emails"

**Poor Objectives** (Vague):
- ❌ "Get information"
- ❌ "Scrape the website"
- ❌ "Find data"

### 2. Max Pages Selection

| Website Size | Objective Scope | Recommended max_pages |
|--------------|----------------|----------------------|
| Small (< 50 pages) | Comprehensive | 30-50 |
| Medium (100-500 pages) | Specific topic | 40-80 |
| Large (> 500 pages) | Narrow focus | 50-100 |
| Very Large | Very specific | 100-200 |

### 3. Iterative Refinement

1. **First Run** (quick scan):
   - Use max_pages=15
   - Review results
   - Refine objective if needed

2. **Second Run** (comprehensive):
   - Adjust objective based on findings
   - Increase max_pages=50
   - Get full dataset

### 4. Ethical Considerations

✅ **Do**:
- Respect robots.txt
- Crawl during off-peak hours
- Stay within same domain
- Review website terms of service

❌ **Don't**:
- Hammer servers (add delays for heavy scraping)
- Ignore access restrictions
- Scrape copyrighted content without permission
- Violate privacy policies

### 5. Data Validation

Always verify extracted data:

```python
# Check relevance distribution
for page in scraped_data:
    print(f"{page['url']}: {page['relevance_score']}")

# Validate extraction
high_value = [p for p in scraped_data if p['relevance_score'] >= 7]
if len(high_value) < 3:
    print("Warning: Few high-value pages found. Adjust objective?")
```

### 6. Result Review

Before relying on results:
1. Check average relevance score (should be > 5)
2. Review top 5 high-value pages
3. Verify AI answer matches raw data
4. Look for patterns in extracted content

## 📚 Additional Resources

### Files Included

- `agentic_crawler_local.py` - Main crawler script
- `web_crawler_colab.ipynb` - Google Colab version
- `requirements.txt` - Python dependencies
- `README.md` - This file

### External Documentation

- **Crawl4AI**: https://github.com/unclecode/crawl4ai
- **Ollama**: https://ollama.com/docs
- **DeepSeek**: https://www.deepseek.com
- **Playwright**: https://playwright.dev/python

### Community & Support

For issues and questions:
1. Check this README thoroughly
2. Review troubleshooting section
3. Check Ollama/Crawl4AI documentation
4. GitHub issues (if applicable)

## 📝 License

[Specify your license here]

## 🙏 Acknowledgments

Built with:
- **Crawl4AI** - Intelligent web crawling framework
- **Ollama** - Local LLM runtime
- **DeepSeek** - Advanced reasoning model
- **Playwright** - Browser automation
- **BeautifulSoup** - HTML parsing

---

**Created by**: [Your Name]
**Version**: 1.0.0
**Last Updated**: January 2025

**Happy Crawling! 🕷️**

