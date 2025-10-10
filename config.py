"""
Configuration settings for the Agentic Web Crawler
"""

# Ollama Settings
OLLAMA_MODEL = "deepseek-r1:14b"
OLLAMA_TIMEOUT = 60  # seconds (increased for larger model)

# Crawler Settings
DEFAULT_MAX_PAGES = 50
MAX_LINKS_PER_PAGE = 20
MAX_LINKS_TO_SELECT = 5

# Content Storage Settings
HTML_CONTENT_LIMIT = 5000  # characters
MARKDOWN_CONTENT_LIMIT = 5000  # characters

# File Output Settings
DEFAULT_JSON_OUTPUT = "scraped_data.json"
DEFAULT_ANALYSIS_OUTPUT = "scraped_data_analysis.md"

# Crawler Behavior
BYPASS_CACHE = True
VERBOSE_MODE = True
SAME_DOMAIN_ONLY = True

# Analysis Settings
MAX_PAGES_FOR_DETAILED_ANALYSIS = 10
CONTENT_EXCERPT_LENGTH = 1000  # characters

# AI Prompts
NAVIGATION_PROMPT_TEMPLATE = """You are a web crawler assistant. Your task is to decide which links to crawl next.

Current URL: {current_url}
Current Page Summary: {content_summary}

Available Links (select up to {max_links} most relevant):
{links_list}

Analyze these links and select the TOP {max_links} most relevant and important links to crawl.
Consider:
1. Links that likely contain main content (not login, cart, social media)
2. Links that go deeper into the site structure
3. Links that represent different sections or categories

Respond ONLY with the numbers of the links to crawl (comma-separated, e.g., "1,3,5,7,9").
If no links are relevant, respond with "NONE".
"""

OVERALL_ANALYSIS_PROMPT_TEMPLATE = """Analyze this website crawl data and provide a comprehensive summary.

Total pages crawled: {total_pages}

Page titles:
{titles}

Descriptions:
{descriptions}

Provide:
1. What type of website is this?
2. Main topics and themes covered
3. Overall structure and organization
4. Key sections identified
5. Target audience

Keep your response concise but informative."""

PAGE_ANALYSIS_PROMPT_TEMPLATE = """Analyze this web page and provide a detailed breakdown in human-readable format.

URL: {url}
Title: {title}
Description: {description}

Content excerpt:
{content}

Provide:
1. Page purpose and main topic
2. Key information presented
3. Important elements or features
4. Relationship to overall site structure

Be specific and detailed."""

# Link Filtering Patterns (URLs to avoid)
EXCLUDED_URL_PATTERNS = [
    'login', 'signin', 'signup', 'register',
    'cart', 'checkout', 'account',
    'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
    'youtube.com', 'mailto:', 'tel:',
    '.pdf', '.zip', '.exe', '.dmg'
]

# Headers for requests (optional, for advanced users)
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
