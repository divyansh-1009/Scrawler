"""
Agentic AI Web Crawler using Crawl4AI and Ollama
This script crawls websites intelligently using AI models for navigation decisions and schema-less content extraction.
Features:
- Goal-oriented crawling based on user objectives
- AI-powered schema-less content extraction
- Two-phase crawling (reconnaissance + targeted deep dive)
- Learning system that improves from experience
- Context-aware navigation with memory
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import ollama
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import NoExtractionStrategy
from bs4 import BeautifulSoup
from convert_to_markdown import json_to_markdown_complete


class ImprovedAgenticWebCrawler:
    """
    An intelligent web crawler that uses AI to make navigation decisions and extract content schema-lessly.
    """
    
    def __init__(self, 
                 decision_model: str = "deepseek-r1:14b",
                 extraction_model: str = "deepseek-r1:14b",
                 max_pages: int = 50):
        """
        Initialize the improved agentic web crawler.
        
        Args:
            decision_model: The Ollama model to use for strategic decisions
            extraction_model: The Ollama model to use for content extraction
            max_pages: Maximum number of pages to crawl
        """
        self.decision_model = decision_model
        self.extraction_model = extraction_model
        self.max_pages = max_pages
        self.visited_urls = set()
        self.scraped_data = []
        self.base_domain = None
        
        # Goal-driven attributes
        self.crawl_objective = ""
        self.crawl_objective_analysis = {}
        self.desired_data_types = []
        
        # Site understanding and learning
        self.site_understanding = {
            "site_type": None,
            "main_sections": [],
            "content_patterns": defaultdict(list),
            "high_value_url_patterns": [],
            "recommended_focus": ""
        }
        
        # Track page values for learning
        self.page_relevance_scores = {}
        self.high_value_pages = []
        
        # Crawl phases
        self.current_phase = "initialization"  # initialization, reconnaissance, deep_crawl
        
    async def analyze_user_objective(self, objective: str) -> Dict[str, Any]:
        """
        Use AI to analyze user's crawl objective and understand what they're looking for.
        
        Args:
            objective: User's description of what information they want
            
        Returns:
            Analysis including data types, extraction strategies, and focus areas
        """
        print("\n🤖 Analyzing your objective with AI...")
        
        prompt = f"""You are helping to plan a web crawling operation. Analyze the user's objective and provide a detailed crawl strategy.

USER'S OBJECTIVE: "{objective}"

Analyze this objective and provide:
1. What TYPE of data they're looking for (e.g., products, articles, contact info, documentation, etc.)
2. What specific FIELDS or attributes they likely want extracted
3. What sections of a website would be most valuable
4. What URL patterns to prioritize
5. What URL patterns to avoid

Respond in JSON format:
{{
  "data_types": ["primary type", "secondary type"],
  "key_fields": ["field1", "field2", "field3"],
  "valuable_sections": ["section1", "section2"],
  "url_patterns_to_seek": ["pattern1", "pattern2"],
  "url_patterns_to_avoid": ["pattern1", "pattern2"],
  "extraction_strategy": "Description of how to approach extraction",
  "success_criteria": "How to know when we have enough data"
}}

Be specific and actionable."""

        try:
            response = ollama.generate(
                model=self.decision_model,
                prompt=prompt
            )
            
            # Try to extract JSON from response
            response_text = response['response'].strip()
            
            # Handle markdown code blocks
            if '```json' in response_text:
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif '```' in response_text:
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            analysis = json.loads(response_text)
            
            print("\n✓ Objective Analysis Complete:")
            print(f"  • Data Types: {', '.join(analysis.get('data_types', []))}")
            print(f"  • Key Fields: {', '.join(analysis.get('key_fields', []))}")
            print(f"  • Focus Areas: {', '.join(analysis.get('valuable_sections', []))}")
            
            self.crawl_objective_analysis = analysis
            self.desired_data_types = analysis.get('data_types', [])
            
            return analysis
            
        except Exception as e:
            print(f"⚠ Analysis error: {e}")
            # Fallback to basic analysis
            return {
                "data_types": ["general content"],
                "key_fields": ["title", "content", "links"],
                "valuable_sections": ["main content"],
                "url_patterns_to_seek": [],
                "url_patterns_to_avoid": ["login", "signup", "cart"],
                "extraction_strategy": "Extract all available content",
                "success_criteria": "Crawl specified number of pages"
            }
        
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain as the base URL."""
        if not self.base_domain:
            return False
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain
    
    def _extract_url_pattern(self, url: str) -> str:
        """
        Extract pattern from URL for learning purposes.
        Example: /products/123/details -> /products/*/details
        """
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        pattern_parts = []
        for part in path_parts:
            # Replace numeric IDs and long strings with wildcards
            if part.isdigit() or len(part) > 30:
                pattern_parts.append('*')
            else:
                pattern_parts.append(part)
        
        return '/' + '/'.join(pattern_parts) if pattern_parts else '/'
    
    def _find_similar_visited_urls(self, url: str, limit: int = 3) -> List[str]:
        """Find similar URLs we've already visited for learning."""
        pattern = self._extract_url_pattern(url)
        similar = []
        
        for visited in self.visited_urls:
            if self._extract_url_pattern(visited) == pattern:
                similar.append(visited)
                if len(similar) >= limit:
                    break
        
        return similar
    
    async def _extract_content_with_ai(self, html: str, url: str, markdown: str = "") -> Dict[str, Any]:
        """
        Use AI to understand and extract relevant content WITHOUT hardcoded patterns.
        The AI decides what's important based on the crawl objective.
        
        Args:
            html: The HTML content to parse
            url: The URL being scraped
            markdown: Markdown version of content (if available)
            
        Returns:
            Dictionary containing AI-extracted structured data
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove navigation, footer, header to focus on main content
        for tag in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
            tag.decompose()
        
        # Get clean text content
        page_text = soup.get_text(separator='\n', strip=True)
        
        # Use markdown if available (cleaner), otherwise use text
        content_to_analyze = markdown[:4000] if markdown else page_text[:4000]
        
        # Get structural hints
        headers = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)][:15]
        
        # Get main content links
        main_links = []
        for a in soup.find_all('a', href=True)[:30]:
            text = a.get_text(strip=True)
            if text and len(text) > 2:
                main_links.append(text)
        
        prompt = f"""You are analyzing a web page to extract relevant information based on a specific objective.

CRAWL OBJECTIVE: {self.crawl_objective}

TARGET DATA TYPES: {', '.join(self.desired_data_types)}
KEY FIELDS TO EXTRACT: {', '.join(self.crawl_objective_analysis.get('key_fields', []))}

PAGE URL: {url}

PAGE HEADERS:
{chr(10).join(headers[:10])}

PAGE CONTENT (excerpt):
{content_to_analyze}

MAIN LINKS:
{', '.join(main_links[:15])}

YOUR TASK:
1. Determine the TYPE of page this is (e.g., "product listing", "article", "documentation", "about page", "homepage", etc.)
2. Rate how RELEVANT this page is to the crawl objective (0-10 scale)
3. Extract ALL relevant structured data that matches the objective
4. Be FLEXIBLE - adapt your extraction schema to what's actually on the page

Respond in JSON format:
{{
  "page_type": "...",
  "relevance_score": 0-10,
  "key_content": {{
    // Extract whatever structured data is relevant
    // Examples: "items": [...], "article_text": "...", "metadata": {{...}}
    // Adapt to the page content and objective
  }},
  "reasoning": "Brief explanation of why this page is/isn't relevant",
  "content_summary": "One sentence summary of page content"
}}

Be thorough but concise. Extract actual data, not descriptions."""

        try:
            response = ollama.generate(
                model=self.extraction_model,
                prompt=prompt
            )
            
            # Extract JSON from response
            response_text = response['response'].strip()
            
            # Handle markdown code blocks
            if '```json' in response_text:
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif '```' in response_text:
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            extracted = json.loads(response_text)
            
            # Update site understanding
            self._update_site_knowledge(url, extracted)
            
            return extracted
            
        except Exception as e:
            print(f"  ⚠ AI extraction error: {str(e)[:100]}")
            # Fallback to basic extraction
            return {
                "page_type": "unknown",
                "relevance_score": 5,
                "key_content": {
                    "title": soup.find('title').get_text() if soup.find('title') else "No title",
                    "headers": headers,
                    "text_excerpt": page_text[:500]
                },
                "reasoning": "Fallback extraction due to error",
                "content_summary": "Content extracted with fallback method"
            }
    
    def _update_site_knowledge(self, url: str, extraction_result: Dict):
        """
        Learn from each page to improve future decisions.
        """
        relevance = extraction_result.get('relevance_score', 0)
        self.page_relevance_scores[url] = relevance
        
        if relevance >= 7:  # High-value page
            self.high_value_pages.append(url)
            
            # Learn URL pattern
            url_pattern = self._extract_url_pattern(url)
            if url_pattern not in self.site_understanding['high_value_url_patterns']:
                self.site_understanding['high_value_url_patterns'].append(url_pattern)
            
            # Learn content patterns
            page_type = extraction_result.get('page_type')
            if page_type:
                self.site_understanding['content_patterns'][page_type].append({
                    'url': url,
                    'pattern': url_pattern,
                    'relevance': relevance
                })
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize and complete relative URLs."""
        url = urljoin(base_url, url)
        # Remove fragments
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    async def _extract_links_with_context(self, html: str, base_url: str) -> List[Dict]:
        """
        Extract links WITH their surrounding context for better AI decision-making.
        """
        soup = BeautifulSoup(html, 'lxml')
        links_with_context = []
        
        # Patterns to exclude from objective analysis
        avoid_patterns = self.crawl_objective_analysis.get('url_patterns_to_avoid', [])
        avoid_patterns.extend(['javascript:', 'mailto:', 'tel:', '#', '.jpg', '.png', '.pdf', '.css', '.js'])
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Skip obvious bad links
            if any(pattern.lower() in href.lower() for pattern in avoid_patterns):
                continue
            
            try:
                full_url = self._normalize_url(href, base_url)
            except:
                    continue
                
            if not self._is_same_domain(full_url) or full_url in self.visited_urls:
                continue
            
            # Gather rich context
            anchor_text = link.get_text(strip=True)
            if not anchor_text or len(anchor_text) < 2:
                continue
                
            # Get surrounding text (parent element context)
            parent = link.parent
            context_text = parent.get_text(strip=True)[:200] if parent else ""
            
            # Get any title or aria-label
            title = link.get('title', '')
            aria_label = link.get('aria-label', '')
            
            # Get link position/importance
            is_in_nav = bool(link.find_parent(['nav', 'header']))
            is_in_main = bool(link.find_parent('main'))
            is_prominent = bool(link.find_parent(['h1', 'h2', 'h3']))
            
            links_with_context.append({
                'url': full_url,
                'anchor_text': anchor_text,
                'context': context_text,
                'title': title,
                'aria_label': aria_label,
                'is_navigation': is_in_nav,
                'is_main_content': is_in_main,
                'is_prominent': is_prominent,
                'url_path': urlparse(full_url).path
            })
        
        return links_with_context
    
    async def _score_url_relevance(self, link_info: Dict) -> Dict:
        """
        Use AI to predict how relevant a URL is before crawling it.
        This saves time by avoiding low-value pages.
        """
        url = link_info['url']
        
        # Learn from history
        similar_urls = self._find_similar_visited_urls(url)
        historical_scores = [self.page_relevance_scores.get(u, 0) for u in similar_urls]
        
        # Check if URL pattern matches known high-value patterns
        url_pattern = self._extract_url_pattern(url)
        pattern_bonus = 2 if url_pattern in self.site_understanding['high_value_url_patterns'] else 0
        
        # Quick heuristic score
        heuristic_score = 5 + pattern_bonus
        
        # Boost if in main content
        if link_info.get('is_main_content'):
            heuristic_score += 1
        if link_info.get('is_prominent'):
            heuristic_score += 1
        
        # Check against seek patterns
        seek_patterns = self.crawl_objective_analysis.get('url_patterns_to_seek', [])
        if any(pattern.lower() in url.lower() for pattern in seek_patterns):
            heuristic_score += 2
        
        return {
            'url': url,
            'relevance_score': heuristic_score,
            'historical_avg': sum(historical_scores) / len(historical_scores) if historical_scores else 5,
            'should_crawl': heuristic_score >= 5,
            'priority': 'high' if heuristic_score >= 8 else 'medium' if heuristic_score >= 6 else 'low'
        }
    
    async def _ask_ollama_for_navigation_advanced(
        self, 
        current_url: str, 
        available_links: List[Dict],
        page_extraction: Dict
    ) -> List[str]:
        """
        Advanced AI navigation with full context and learning.
        """
        if not available_links:
            return []
        
        # Score all links first
        scored_links = []
        for link_info in available_links[:30]:
            score_info = await self._score_url_relevance(link_info)
            scored_links.append({**link_info, **score_info})
        
        # Sort by relevance
        scored_links.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Take top candidates
        top_candidates = scored_links[:12]
        
        # Format for AI
        links_summary = []
        for i, link in enumerate(top_candidates, 1):
            links_summary.append(
                f"{i}. [{link['relevance_score']:.1f}] {link['anchor_text'][:50]} → {link['url_path']}"
            )
        
        prompt = f"""You are guiding a web crawler. Review these pre-scored URLs and select the best ones to crawl next.

CRAWL OBJECTIVE: {self.crawl_objective}

PROGRESS:
- Pages crawled: {len(self.visited_urls)}/{self.max_pages}
- High-value pages: {len(self.high_value_pages)}
- Current phase: {self.current_phase}

CURRENT PAGE: {current_url}
Page type: {page_extraction.get('page_type', 'unknown')}
Relevance: {page_extraction.get('relevance_score', '?')}/10
Summary: {page_extraction.get('content_summary', 'N/A')}

LEARNED PATTERNS:
High-value URL patterns: {self.site_understanding['high_value_url_patterns'][:5]}

TOP CANDIDATE URLS (with pre-scored relevance [score]):
{chr(10).join(links_summary)}

Select 3-5 URLs that best match the objective. Consider:
1. URLs matching learned high-value patterns
2. URLs with high relevance scores
3. URLs that explore new areas vs going deeper
4. Current progress toward objective

Respond with ONLY the numbers (comma-separated, e.g., "1,3,5,8").
If no links are worth crawling, respond "NONE"."""
        
        try:
            response = ollama.generate(
                model=self.decision_model,
                prompt=prompt
            )
            
            answer = response['response'].strip()
            
            if 'NONE' in answer.upper():
                print("  → AI: No valuable links found")
                return []
            
            # Extract numbers
            numbers = re.findall(r'\d+', answer)
            selected_urls = []
            
            for num in numbers[:5]:
                idx = int(num) - 1
                if 0 <= idx < len(top_candidates):
                    selected_urls.append(top_candidates[idx]['url'])
            
            return selected_urls
            
        except Exception as e:
            print(f"  ⚠ Navigation AI error: {str(e)[:100]}")
            # Fallback: return top 3 by score
            return [link['url'] for link in scored_links[:3]]
    
    async def _crawl_page(self, url: str, crawler: AsyncWebCrawler) -> Optional[Dict[str, Any]]:
        """
        Crawl a single page and extract content using AI.
        
        Args:
            url: The URL to crawl
            crawler: The AsyncWebCrawler instance
            
        Returns:
            Dictionary containing page data or None if failed
        """
        try:
            print(f"📄 Crawling: {url}")
            
            result = await crawler.arun(
                url=url,
                extraction_strategy=NoExtractionStrategy(),
                bypass_cache=True
            )
            
            if not result.success:
                print(f"  ✗ Failed to crawl")
                return None
            
            # Use AI to extract content (schema-less)
            ai_extraction = await self._extract_content_with_ai(
                result.html, 
                url,
                result.markdown if result.markdown else ""
            )
            
            page_data = {
                "url": url,
                "title": result.metadata.get("title", "No title"),
                "description": result.metadata.get("description", ""),
                "timestamp": datetime.now().isoformat(),
                "metadata": result.metadata,
                "ai_extraction": ai_extraction,  # AI-extracted structured data
                "relevance_score": ai_extraction.get('relevance_score', 0),
                "page_type": ai_extraction.get('page_type', 'unknown')
            }
            
            # Print extraction summary
            relevance = ai_extraction.get('relevance_score', 0)
            page_type = ai_extraction.get('page_type', 'unknown')
            print(f"  ✓ Type: {page_type} | Relevance: {relevance}/10")
            
            # Show key content extracted
            key_content = ai_extraction.get('key_content', {})
            if key_content:
                content_types = list(key_content.keys())
                print(f"  → Extracted: {', '.join(content_types[:3])}")
            
            return page_data
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:80]}")
            return None
    
    async def _analyze_site_structure(self) -> Dict:
        """
        Analyze crawled pages from reconnaissance to understand site structure.
        """
        print("\n🔍 Analyzing site structure...")
        
        # Collect page types and relevance scores
        page_types = {}
        for page in self.scraped_data:
            page_type = page.get('page_type', 'unknown')
            relevance = page.get('relevance_score', 0)
            if page_type not in page_types:
                page_types[page_type] = []
            page_types[page_type].append(relevance)
        
        # Build summary for AI
        pages_summary = []
        for page in self.scraped_data[:10]:
            pages_summary.append(f"- {page['url']}: {page['page_type']} (relevance: {page.get('relevance_score', 0)}/10)")
        
        prompt = f"""Analyze the reconnaissance crawl results and provide strategic guidance.

CRAWL OBJECTIVE: {self.crawl_objective}

PAGES CRAWLED IN RECONNAISSANCE ({len(self.scraped_data)} pages):
{chr(10).join(pages_summary)}

PAGE TYPE DISTRIBUTION:
{json.dumps({pt: {'count': len(scores), 'avg_relevance': sum(scores)/len(scores)} for pt, scores in page_types.items()}, indent=2)}

HIGH-VALUE URL PATTERNS DISCOVERED:
{self.site_understanding['high_value_url_patterns']}

Provide strategic analysis:
1. What TYPE of website is this?
2. Which sections/page types are most valuable for the objective?
3. What URL patterns should we prioritize in deep crawl?
4. What's the recommended crawl strategy going forward?

Respond in JSON:
{{
  "site_type": "...",
  "most_valuable_page_types": ["type1", "type2"],
  "recommended_focus": "Description of where to focus",
  "high_priority_patterns": ["pattern1", "pattern2"],
  "strategy": "continue_deep | adjust_objective | site_not_suitable"
}}"""

        try:
            response = ollama.generate(
                model=self.decision_model,
                prompt=prompt
            )
            
            response_text = response['response'].strip()
            if '```json' in response_text:
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            analysis = json.loads(response_text)
            
            print(f"  ✓ Site Type: {analysis.get('site_type', 'Unknown')}")
            print(f"  ✓ Focus: {analysis.get('recommended_focus', 'General crawl')}")
            
            return analysis
            
        except Exception as e:
            print(f"  ⚠ Analysis error: {e}")
            return {
                "site_type": "unknown",
                "most_valuable_page_types": list(page_types.keys())[:2],
                "recommended_focus": "Continue crawling all page types",
                "high_priority_patterns": self.site_understanding['high_value_url_patterns'],
                "strategy": "continue_deep"
            }
    
    async def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Two-phase intelligent crawling:
        Phase 1: Reconnaissance - understand site structure
        Phase 2: Targeted deep crawl - focus on valuable content
        
        Args:
            start_url: The starting URL for crawling
            
        Returns:
            List of scraped page data
        """
        # Set base domain
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        
        print(f"\n{'='*80}")
        print(f"🚀 STARTING INTELLIGENT WEB CRAWL")
        print(f"{'='*80}")
        print(f"Target: {start_url}")
        print(f"Objective: {self.crawl_objective}")
        print(f"Max pages: {self.max_pages}")
        print(f"{'='*80}\n")
        
        # PHASE 1: RECONNAISSANCE
        recon_budget = max(5, self.max_pages // 10)
        self.current_phase = "reconnaissance"
        
        print(f"📡 PHASE 1: RECONNAISSANCE ({recon_budget} pages)")
        print(f"{'─'*80}")
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            url_queue = [start_url]
            
            while url_queue and len(self.visited_urls) < recon_budget:
                current_url = url_queue.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(current_url)
                
                # Crawl page
                page_data = await self._crawl_page(current_url, crawler)
                
                if page_data:
                    self.scraped_data.append(page_data)
                    
                    # Get page HTML for link extraction
                    result = await crawler.arun(url=current_url, bypass_cache=True)
                    if result.success:
                        # Extract links with context
                        links = await self._extract_links_with_context(result.html, current_url)
                        
                        if links:
                            # Simple selection in recon phase - just take diverse links
                            selected = links[:8]  # Take more links in recon
                            for link in selected:
                                if link['url'] not in self.visited_urls and link['url'] not in url_queue:
                                    url_queue.append(link['url'])
                
                print(f"  Progress: {len(self.visited_urls)}/{recon_budget} recon pages\n")
        
        # Analyze site structure
        site_analysis = await self._analyze_site_structure()
        self.site_understanding.update(site_analysis)
        
        # PHASE 2: TARGETED DEEP CRAWL
        deep_budget = self.max_pages - len(self.visited_urls)
        self.current_phase = "deep_crawl"
        
        print(f"\n{'─'*80}")
        print(f"🎯 PHASE 2: TARGETED DEEP CRAWL ({deep_budget} pages)")
        print(f"{'─'*80}\n")
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Build priority queue from high-value pages discovered in recon
            url_queue = []
            
            # Re-extract links from high-value pages
            for page in self.scraped_data:
                if page.get('relevance_score', 0) >= 6:
                    result = await crawler.arun(url=page['url'], bypass_cache=True)
                    if result.success:
                        links = await self._extract_links_with_context(result.html, page['url'])
                        for link in links[:5]:
                            if link['url'] not in self.visited_urls:
                                url_queue.append(link['url'])
            
            # Remove duplicates
            url_queue = list(dict.fromkeys(url_queue))
            
            while url_queue and len(self.visited_urls) < self.max_pages:
                current_url = url_queue.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(current_url)
                
                # Crawl page
                page_data = await self._crawl_page(current_url, crawler)
                
                if page_data:
                    self.scraped_data.append(page_data)
                    
                    # Extract links with context
                    result = await crawler.arun(url=current_url, bypass_cache=True)
                    if result.success:
                        links = await self._extract_links_with_context(result.html, current_url)
                    
                    if links:
                            # Use advanced AI navigation
                            selected_urls = await self._ask_ollama_for_navigation_advanced(
                            current_url, 
                            links, 
                                page_data.get('ai_extraction', {})
                            )
                            
                            print(f"  → AI selected {len(selected_urls)} links")
                            
                            for url in selected_urls:
                                if url not in self.visited_urls and url not in url_queue:
                                    url_queue.append(url)
                
                print(f"  Progress: {len(self.visited_urls)}/{self.max_pages} | Queue: {len(url_queue)} | High-value: {len(self.high_value_pages)}\n")
        
        print(f"\n{'='*80}")
        print(f"✅ CRAWL COMPLETE")
        print(f"{'='*80}")
        print(f"Total pages: {len(self.scraped_data)}")
        print(f"High-value pages: {len(self.high_value_pages)}")
        print(f"Avg relevance: {sum(self.page_relevance_scores.values())/len(self.page_relevance_scores) if self.page_relevance_scores else 0:.1f}/10")
        print(f"{'='*80}\n")
        
        return self.scraped_data
    
    def save_to_json(self, filename: str = "scraped_data.json"):
        """Save only the extracted relevant data without crawl metadata."""
        output_path = os.path.join(os.getcwd(), filename)
        
        # Extract only the relevant content based on objective
        extracted_data = []
        for page in self.scraped_data:
            if page.get('relevance_score', 0) >= 5:  # Only include somewhat relevant pages
                page_data = {
                    "url": page['url'],
                    "extracted_content": page.get('ai_extraction', {}).get('key_content', {}),
                    "relevance": page.get('relevance_score', 0)
                }
                extracted_data.append(page_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "objective": self.crawl_objective,
                "extracted_data": extracted_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Data saved to: {output_path}")
        return output_path


async def main():
    """Main execution function with user objective input."""
    print("=" * 80)
    print("🤖 IMPROVED AGENTIC WEB CRAWLER")
    print("Schema-less AI-Powered Intelligent Crawling")
    print("=" * 80)
    print()
    
    # Model info
    print("ℹ️  This crawler uses deepseek-r1:14b (requires ~8.7GB RAM)")
    print("   For lower memory: edit decision_model parameter to use qwen2.5:7b or tinyllama")
    print()
    
    # Get user inputs
    start_url = input("🌐 Enter the website URL to crawl: ").strip()
    
    if not start_url.startswith(('http://', 'https://')):
        start_url = 'https://' + start_url
    
    print()
    print("📝 What information are you looking for?")
    print("   Examples:")
    print("   - 'Product names, prices, and availability'")
    print("   - 'Blog articles with titles and publication dates'")
    print("   - 'Documentation pages with code examples'")
    print("   - 'Contact information and team member details'")
    print()
    crawl_objective = input("Your objective: ").strip()
    
    if not crawl_objective:
        crawl_objective = "Extract all relevant content and structured data"
    
    print()
    max_pages_input = input("🔢 Maximum pages to crawl (default: 50): ").strip()
    max_pages = int(max_pages_input) if max_pages_input.isdigit() else 50
    
    # Initialize crawler
    crawler = ImprovedAgenticWebCrawler(
        decision_model="deepseek-r1:14b",
        extraction_model="deepseek-r1:14b",
        max_pages=max_pages
    )
    
    # Set objective
    crawler.crawl_objective = crawl_objective
    
    # Analyze objective with AI
    await crawler.analyze_user_objective(crawl_objective)
    
    # Start crawling
    scraped_data = await crawler.crawl_website(start_url)
    
    # Save data
    json_file = crawler.save_to_json()
    
    print(f"\n✅ Successfully crawled {len(scraped_data)} pages")
    print(f"   High-value pages: {len(crawler.high_value_pages)}")
    print(f"   Average relevance: {sum(crawler.page_relevance_scores.values())/len(crawler.page_relevance_scores):.1f}/10")
    
    # Generate human-readable report
    generate_report = input("\n📊 Generate human-readable analysis report? (y/n): ").strip().lower()
    
    if generate_report == 'y':
        analysis_file = json_file.replace('.json', '_analysis.md')
        json_to_markdown_complete(json_file, analysis_file)
        print(f"\n✓ Report saved to: {analysis_file}")
    
    print("\n" + "=" * 80)
    print("🎉 CRAWLING COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
