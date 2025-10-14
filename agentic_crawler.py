"""
🤖 Agentic AI Web Crawler 

Schema-less AI-Powered Intelligent Web Crawling

This script uses:
- Ollama with deepseek-r1:14b for AI-powered decisions
- Crawl4AI for intelligent web crawling
- AI Navigation - LLM figures out which links are relevant
- Schema-less Extraction - LLM determines what's important to scrape
- Two-phase crawling - Reconnaissance + Targeted Deep Dive
- Section-based Analysis - Each page section scored independently for relevance
- Smart Link Selection - Heuristic filtering of links based on objective keywords

Key Improvements:
- Reconnaissance phase uses intelligent link filtering (not blind first-N selection)
- Pages analyzed section-by-section with individual relevance scores
- Only relevant sections extracted, irrelevant sections skipped
- Link selection considers anchor text, context, and objective keywords

Performance Optimizations:
- Parallel page crawling: Multiple pages processed concurrently
- Async AI calls: LLM requests run in thread pool for parallelization
- Batch processing: Queue seeding and link extraction parallelized
- Configurable concurrency: Adjust speed vs resource usage (1-10 pages)
- Expected speedup: 2-3x faster with default concurrency=3

Requirements:
- Ollama must be running locally with deepseek-r1:14b model
- Python 3.8+
- See requirements.txt for package dependencies
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from functools import partial
import ollama
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import NoExtractionStrategy
from bs4 import BeautifulSoup


class ImprovedAgenticWebCrawler:
    """An intelligent web crawler that uses AI to make navigation decisions and extract content schema-lessly."""
    
    def __init__(self, decision_model: str = "deepseek-r1:14b", extraction_model: str = "deepseek-r1:14b", max_pages: int = 50, concurrency: int = 3):
        self.decision_model = decision_model
        self.extraction_model = extraction_model
        self.max_pages = max_pages
        self.concurrency = concurrency  # Number of pages to process concurrently
        self.visited_urls = set()
        self.scraped_data = []
        self.base_domain = None
        self.crawl_objective = ""
        self.crawl_objective_analysis = {}
        self.desired_data_types = []
        self.site_understanding = {"site_type": None, "main_sections": [], "content_patterns": defaultdict(list), "high_value_url_patterns": [], "recommended_focus": ""}
        self.page_relevance_scores = {}
        self.high_value_pages = []
        self.current_phase = "initialization"
    
    async def _async_ollama_generate(self, model: str, prompt: str) -> Dict:
        """Async wrapper for ollama.generate to enable parallelization."""
        loop = asyncio.get_event_loop()
        # Run the blocking ollama.generate in a thread pool
        response = await loop.run_in_executor(None, partial(ollama.generate, model=model, prompt=prompt))
        return response
        
    async def analyze_user_objective(self, objective: str) -> Dict[str, Any]:
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
            response = await self._async_ollama_generate(model=self.decision_model, prompt=prompt)
            response_text = response['response'].strip()
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
            return {"data_types": ["general content"], "key_fields": ["title", "content", "links"], "valuable_sections": ["main content"], "url_patterns_to_seek": [], "url_patterns_to_avoid": ["login", "signup", "cart"], "extraction_strategy": "Extract all available content", "success_criteria": "Crawl specified number of pages"}
        
    def _is_same_domain(self, url: str) -> bool:
        if not self.base_domain:
            return False
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain
    
    def _extract_url_pattern(self, url: str) -> str:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        pattern_parts = []
        for part in path_parts:
            if part.isdigit() or len(part) > 30:
                pattern_parts.append('*')
            else:
                pattern_parts.append(part)
        return '/' + '/'.join(pattern_parts) if pattern_parts else '/'
    
    def _find_similar_visited_urls(self, url: str, limit: int = 3) -> List[str]:
        pattern = self._extract_url_pattern(url)
        similar = []
        for visited in self.visited_urls:
            if self._extract_url_pattern(visited) == pattern:
                similar.append(visited)
                if len(similar) >= limit:
                    break
        return similar
    
    def _score_link_relevance_heuristic(self, link: Dict) -> float:
        """Score a link's relevance using heuristics during reconnaissance."""
        score = 5.0  # Base score
        
        # Extract text to analyze
        link_text = (link.get('anchor_text', '') + ' ' + link.get('context', '')).lower()
        url_path = link.get('url_path', '').lower()
        
        # Penalize obvious low-value pages
        low_value_keywords = ['privacy', 'policy', 'terms', 'cookie', 'login', 'signin', 'signup', 
                              'register', 'cart', 'checkout', 'account', 'subscribe', 'newsletter']
        for keyword in low_value_keywords:
            if keyword in link_text or keyword in url_path:
                score -= 3
        
        # Boost if link is in main content area
        if link.get('is_main_content'):
            score += 2
        
        # Boost if link is prominent (in headers)
        if link.get('is_prominent'):
            score += 1.5
        
        # Penalize navigation links
        if link.get('is_navigation'):
            score -= 1
        
        # Boost if objective keywords appear in link text
        if self.crawl_objective:
            objective_keywords = [word.lower() for word in self.crawl_objective.split() if len(word) > 3]
            for keyword in objective_keywords:
                if keyword in link_text:
                    score += 2
                if keyword in url_path:
                    score += 1.5
        
        # Boost if matches desired data types
        for data_type in self.desired_data_types:
            if data_type.lower() in link_text or data_type.lower() in url_path:
                score += 2
        
        # Check against objective analysis patterns
        seek_patterns = self.crawl_objective_analysis.get('url_patterns_to_seek', [])
        for pattern in seek_patterns:
            if pattern.lower() in url_path or pattern.lower() in link_text:
                score += 3
        
        return max(0, min(10, score))  # Clamp between 0-10
    
    def _select_best_links_for_recon(self, links: List[Dict], count: int = 8) -> List[Dict]:
        """Intelligently select the most promising links during reconnaissance."""
        if not links:
            return []
        
        # Score all links
        scored_links = []
        for link in links:
            score = self._score_link_relevance_heuristic(link)
            scored_links.append((score, link))
        
        # Sort by score (highest first)
        scored_links.sort(reverse=True, key=lambda x: x[0])
        
        # Take top N, but ensure diversity (don't take too many from same pattern)
        selected = []
        pattern_counts = defaultdict(int)
        
        for score, link in scored_links:
            if len(selected) >= count:
                break
            
            # Skip if score is too low (below 3)
            if score < 3:
                continue
            
            # Limit links from same URL pattern to maintain diversity
            pattern = self._extract_url_pattern(link['url'])
            if pattern_counts[pattern] >= 2:  # Max 2 links per pattern in recon
                continue
            
            selected.append(link)
            pattern_counts[pattern] += 1
        
        return selected
    
    def _identify_page_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Identify distinct content sections on a page."""
        sections = []
        section_id = 0
        
        # Try semantic HTML5 sections first
        for section_tag in soup.find_all(['section', 'article', 'main']):
            text = section_tag.get_text(separator=' ', strip=True)
            if len(text) < 50:  # Skip tiny sections
                continue
            
            # Get section identifier
            section_class = ' '.join(section_tag.get('class', []))
            section_name = section_tag.get('id', section_class or f'section_{section_id}')
            
            # Get headers in this section
            headers = [h.get_text(strip=True) for h in section_tag.find_all(['h1', 'h2', 'h3', 'h4']) if h.get_text(strip=True)]
            
            sections.append({
                'id': section_id,
                'name': section_name[:50],
                'text_preview': text[:400],
                'headers': headers[:3],
                'tag_type': section_tag.name,
                'word_count': len(text.split())
            })
            section_id += 1
        
        # If no semantic sections found, try divs with substantial content
        if len(sections) < 2:
            sections = []
            section_id = 0
            for div in soup.find_all('div', class_=True):
                text = div.get_text(separator=' ', strip=True)
                if len(text) < 100:  # Need more substantial content for divs
                    continue
                
                # Skip if this div is nested inside another we already captured
                if any(div in s.get('_element', []) for s in sections):
                    continue
                
                section_class = ' '.join(div.get('class', []))
                headers = [h.get_text(strip=True) for h in div.find_all(['h1', 'h2', 'h3', 'h4']) if h.get_text(strip=True)]
                
                sections.append({
                    'id': section_id,
                    'name': section_class[:50] or f'content_block_{section_id}',
                    'text_preview': text[:400],
                    'headers': headers[:3],
                    'tag_type': 'div',
                    'word_count': len(text.split()),
                    '_element': div  # Keep reference for nesting check
                })
                section_id += 1
                
                if len(sections) >= 8:  # Limit to avoid too many sections
                    break
        
        # Clean up internal references
        for section in sections:
            section.pop('_element', None)
        
        return sections[:8]  # Max 8 sections
    
    async def _extract_content_with_ai(self, html: str, url: str, markdown: str = "") -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove noise but keep main content
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Identify distinct sections
        sections = self._identify_page_sections(soup)
        
        # If we have multiple sections, analyze them individually
        if len(sections) >= 2:
            return await self._extract_content_by_sections(sections, url, soup)
        else:
            # Fall back to whole-page analysis for simple pages
            return await self._extract_content_whole_page(soup, url, markdown)
    
    async def _extract_content_by_sections(self, sections: List[Dict], url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze and extract content section by section."""
        
        # Build section summary for AI
        sections_summary = []
        for section in sections:
            sections_summary.append({
                'id': section['id'],
                'name': section['name'],
                'headers': section['headers'],
                'preview': section['text_preview'][:200],
                'size': f"{section['word_count']} words"
            })
        
        prompt = f"""You are analyzing a web page SECTION BY SECTION to find relevant content.

USER'S OBJECTIVE: {self.crawl_objective}

TARGET DATA TYPES: {', '.join(self.desired_data_types)}
KEY FIELDS TO EXTRACT: {', '.join(self.crawl_objective_analysis.get('key_fields', []))}

PAGE URL: {url}

PAGE SECTIONS (analyze each independently):
{json.dumps(sections_summary, indent=2)}

YOUR TASK:
1. Score EACH section individually (0-10) based on how well it matches the objective
2. For high-scoring sections (7+), extract ALL relevant data in detail
3. For medium sections (4-6), extract key points
4. For low sections (0-3), note why they're irrelevant and skip extraction

Respond in JSON:
{{
  "page_type": "overall page type",
  "sections_analysis": [
    {{
      "section_id": 0,
      "relevance_score": 0-10,
      "reason": "why this section is/isn't relevant",
      "extracted_content": {{
        // Only include if relevance >= 4
        // Extract based on relevance level
      }}
    }},
    ...
  ],
  "overall_relevance_score": 0-10,
  "content_summary": "Summary of what valuable information was found across all sections"
}}

CRITICAL: Different sections can have VERY different relevance scores. Be precise."""

        try:
            response = await self._async_ollama_generate(model=self.extraction_model, prompt=prompt)
            response_text = response['response'].strip()
            if '```json' in response_text:
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif '```' in response_text:
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            extracted = json.loads(response_text)
            
            # Compile extracted content from relevant sections
            key_content = {}
            section_scores = []
            for section_analysis in extracted.get('sections_analysis', []):
                section_id = section_analysis.get('section_id')
                relevance = section_analysis.get('relevance_score', 0)
                section_scores.append(relevance)
                
                if relevance >= 4 and 'extracted_content' in section_analysis:
                    section_name = sections[section_id]['name'] if section_id < len(sections) else f'section_{section_id}'
                    key_content[f"section_{section_id}_{section_name}"] = section_analysis['extracted_content']
            
            # Calculate overall relevance (max of section scores, not average)
            overall_relevance = max(section_scores) if section_scores else 0
            
            result = {
                "page_type": extracted.get('page_type', 'unknown'),
                "relevance_score": overall_relevance,
                "key_content": key_content,
                "sections_analysis": extracted.get('sections_analysis', []),
                "reasoning": f"Analyzed {len(sections)} sections. Best section scored {overall_relevance}/10.",
                "content_summary": extracted.get('content_summary', 'No summary available')
            }
            
            self._update_site_knowledge(url, result)
            return result
            
        except Exception as e:
            print(f"  ⚠ AI section extraction error: {str(e)[:100]}")
            # Fallback to whole page
            return await self._extract_content_whole_page(soup, url, "")
    
    async def _extract_content_whole_page(self, soup: BeautifulSoup, url: str, markdown: str = "") -> Dict[str, Any]:
        """Fallback: analyze entire page as one unit (for simple pages)."""
        page_text = soup.get_text(separator='\n', strip=True)
        content_to_analyze = markdown[:4000] if markdown else page_text[:4000]
        headers = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)][:15]
        
        prompt = f"""You are an expert content analyst evaluating a web page for relevance and extracting information.

USER'S OBJECTIVE: {self.crawl_objective}

TARGET DATA TYPES: {', '.join(self.desired_data_types)}
KEY FIELDS TO EXTRACT: {', '.join(self.crawl_objective_analysis.get('key_fields', []))}

PAGE URL: {url}

PAGE HEADERS:
{chr(10).join(headers[:10])}

PAGE CONTENT (excerpt):
{content_to_analyze}

YOUR TASK - ANALYZE CAREFULLY:

1. **Evaluate Page Relevance** (0-10 scale):
   - 9-10: Directly answers the objective with specific, detailed information
   - 7-8: Contains significant relevant information, clearly related to objective
   - 5-6: Moderately relevant, has some useful information related to objective
   - 3-4: Tangentially related, minor relevance or background information
   - 1-2: Barely related, mostly irrelevant with tiny connection
   - 0: Completely irrelevant (navigation, footer, unrelated content)

2. **Extract Strategically**:
   - For HIGH relevance (7+): Extract EVERYTHING in detail - full text, all items, complete data
   - For MODERATE relevance (4-6): Extract key points and important details
   - For LOW relevance (1-3): Extract only the specifically relevant parts

Respond in JSON format:
{{
  "page_type": "...",
  "relevance_score": 0-10,
  "key_content": {{
    // Extract based on relevance level
  }},
  "reasoning": "Clear explanation of WHY this page got this score",
  "content_summary": "Summary of what useful information is on this page"
}}

CRITICAL: Be accurate with relevance scores."""

        try:
            response = await self._async_ollama_generate(model=self.extraction_model, prompt=prompt)
            response_text = response['response'].strip()
            if '```json' in response_text:
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif '```' in response_text:
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            extracted = json.loads(response_text)
            self._update_site_knowledge(url, extracted)
            return extracted
        except Exception as e:
            print(f"  ⚠ AI extraction error: {str(e)[:100]}")
            return {"page_type": "unknown", "relevance_score": 5, "key_content": {"title": soup.find('title').get_text() if soup.find('title') else "No title", "headers": headers, "text_excerpt": page_text[:500]}, "reasoning": "Fallback extraction due to error", "content_summary": "Content extracted with fallback method"}
    
    def _update_site_knowledge(self, url: str, extraction_result: Dict):
        relevance = extraction_result.get('relevance_score', 0)
        self.page_relevance_scores[url] = relevance
        if relevance >= 6:  # Pages with moderate to high relevance
            self.high_value_pages.append(url)
            url_pattern = self._extract_url_pattern(url)
            if url_pattern not in self.site_understanding['high_value_url_patterns']:
                self.site_understanding['high_value_url_patterns'].append(url_pattern)
            page_type = extraction_result.get('page_type')
            if page_type:
                self.site_understanding['content_patterns'][page_type].append({'url': url, 'pattern': url_pattern, 'relevance': relevance})
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        url = urljoin(base_url, url)
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    async def _extract_links_with_context(self, html: str, base_url: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        links_with_context = []
        avoid_patterns = self.crawl_objective_analysis.get('url_patterns_to_avoid', [])
        avoid_patterns.extend(['javascript:', 'mailto:', 'tel:', '#', '.jpg', '.png', '.pdf', '.css', '.js'])
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if any(pattern.lower() in href.lower() for pattern in avoid_patterns):
                continue
            try:
                full_url = self._normalize_url(href, base_url)
            except:
                continue
            if not self._is_same_domain(full_url) or full_url in self.visited_urls:
                continue
            anchor_text = link.get_text(strip=True)
            if not anchor_text or len(anchor_text) < 2:
                continue
            parent = link.parent
            context_text = parent.get_text(strip=True)[:200] if parent else ""
            title = link.get('title', '')
            aria_label = link.get('aria-label', '')
            is_in_nav = bool(link.find_parent(['nav', 'header']))
            is_in_main = bool(link.find_parent('main'))
            is_prominent = bool(link.find_parent(['h1', 'h2', 'h3']))
            
            links_with_context.append({'url': full_url, 'anchor_text': anchor_text, 'context': context_text, 'title': title, 'aria_label': aria_label, 'is_navigation': is_in_nav, 'is_main_content': is_in_main, 'is_prominent': is_prominent, 'url_path': urlparse(full_url).path})
        return links_with_context
    
    async def _score_url_relevance(self, link_info: Dict) -> Dict:
        url = link_info['url']
        similar_urls = self._find_similar_visited_urls(url)
        historical_scores = [self.page_relevance_scores.get(u, 0) for u in similar_urls]
        url_pattern = self._extract_url_pattern(url)
        pattern_bonus = 2 if url_pattern in self.site_understanding['high_value_url_patterns'] else 0
        heuristic_score = 5 + pattern_bonus
        if link_info.get('is_main_content'):
            heuristic_score += 1
        if link_info.get('is_prominent'):
            heuristic_score += 1
        seek_patterns = self.crawl_objective_analysis.get('url_patterns_to_seek', [])
        if any(pattern.lower() in url.lower() for pattern in seek_patterns):
            heuristic_score += 2
        return {'url': url, 'relevance_score': heuristic_score, 'historical_avg': sum(historical_scores) / len(historical_scores) if historical_scores else 5, 'should_crawl': heuristic_score >= 5, 'priority': 'high' if heuristic_score >= 8 else 'medium' if heuristic_score >= 6 else 'low'}
    
    async def _ask_ollama_for_navigation_advanced(self, current_url: str, available_links: List[Dict], page_extraction: Dict) -> List[str]:
        if not available_links:
            return []
        scored_links = []
        for link_info in available_links[:30]:
            score_info = await self._score_url_relevance(link_info)
            scored_links.append({**link_info, **score_info})
        scored_links.sort(key=lambda x: x['relevance_score'], reverse=True)
        top_candidates = scored_links[:12]
        links_summary = []
        for i, link in enumerate(top_candidates, 1):
            links_summary.append(f"{i}. [{link['relevance_score']:.1f}] {link['anchor_text'][:50]} → {link['url_path']}")
        
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
            response = await self._async_ollama_generate(model=self.decision_model, prompt=prompt)
            answer = response['response'].strip()
            if 'NONE' in answer.upper():
                print("  → AI: No valuable links found")
                return []
            numbers = re.findall(r'\d+', answer)
            selected_urls = []
            for num in numbers[:5]:
                idx = int(num) - 1
                if 0 <= idx < len(top_candidates):
                    selected_urls.append(top_candidates[idx]['url'])
            return selected_urls
        except Exception as e:
            print(f"  ⚠ Navigation AI error: {str(e)[:100]}")
            return [link['url'] for link in scored_links[:3]]
    
    async def _crawl_page(self, url: str, crawler: AsyncWebCrawler) -> Optional[Dict[str, Any]]:
        try:
            print(f"📄 Crawling: {url}")
            result = await crawler.arun(url=url, extraction_strategy=NoExtractionStrategy(), bypass_cache=True)
            if not result.success:
                print(f"  ✗ Failed to crawl")
                return None
            ai_extraction = await self._extract_content_with_ai(result.html, url, result.markdown if result.markdown else "")
            page_data = {"url": url, "title": result.metadata.get("title", "No title"), "description": result.metadata.get("description", ""), "timestamp": datetime.now().isoformat(), "metadata": result.metadata, "ai_extraction": ai_extraction, "relevance_score": ai_extraction.get('relevance_score', 0), "page_type": ai_extraction.get('page_type', 'unknown')}
            relevance = ai_extraction.get('relevance_score', 0)
            page_type = ai_extraction.get('page_type', 'unknown')
            
            # Show if section-based analysis was used
            sections_analyzed = ai_extraction.get('sections_analysis', [])
            if sections_analyzed:
                print(f"  ✓ Type: {page_type} | Relevance: {relevance}/10 | Sections: {len(sections_analyzed)}")
                # Show section breakdown
                high_sections = sum(1 for s in sections_analyzed if s.get('relevance_score', 0) >= 7)
                if high_sections > 0:
                    print(f"  → {high_sections} high-value section(s) found")
            else:
                print(f"  ✓ Type: {page_type} | Relevance: {relevance}/10")
            
            key_content = ai_extraction.get('key_content', {})
            if key_content:
                content_types = list(key_content.keys())
                print(f"  → Extracted: {', '.join(content_types[:3])}")
            return page_data
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:80]}")
            return None
    
    async def _crawl_pages_batch(self, urls: List[str], crawler: AsyncWebCrawler, batch_size: int = 3) -> List[Optional[Dict[str, Any]]]:
        """Crawl multiple pages concurrently for better performance."""
        tasks = []
        for url in urls[:batch_size]:
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                tasks.append(self._crawl_page(url, crawler))
        
        if not tasks:
            return []
        
        # Crawl all pages in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"  ⚠ Batch crawl error: {str(result)[:80]}")
            elif result is not None:
                valid_results.append(result)
        
        return valid_results
    
    async def _analyze_site_structure(self) -> Dict:
        print("\n🔍 Analyzing site structure...")
        page_types = {}
        for page in self.scraped_data:
            page_type = page.get('page_type', 'unknown')
            relevance = page.get('relevance_score', 0)
            if page_type not in page_types:
                page_types[page_type] = []
            page_types[page_type].append(relevance)
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
            response = await self._async_ollama_generate(model=self.decision_model, prompt=prompt)
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
            return {"site_type": "unknown", "most_valuable_page_types": list(page_types.keys())[:2], "recommended_focus": "Continue crawling all page types", "high_priority_patterns": self.site_understanding['high_value_url_patterns'], "strategy": "continue_deep"}
    
    async def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        print(f"\n{'='*80}")
        print(f"🚀 STARTING INTELLIGENT WEB CRAWL")
        print(f"{'='*80}")
        print(f"Target: {start_url}")
        print(f"Objective: {self.crawl_objective}")
        print(f"Max pages: {self.max_pages}")
        print(f"{'='*80}\n")
        
        recon_budget = max(5, self.max_pages // 10)
        self.current_phase = "reconnaissance"
        print(f"📡 PHASE 1: RECONNAISSANCE ({recon_budget} pages)")
        print(f"{'─'*80}")
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            url_queue = [start_url]
            batch_size = self.concurrency  # Use configurable concurrency
            
            while url_queue and len(self.visited_urls) < recon_budget:
                # Get batch of URLs to process
                remaining_budget = recon_budget - len(self.visited_urls)
                current_batch_size = min(batch_size, remaining_budget, len(url_queue))
                
                batch_urls = []
                for _ in range(current_batch_size):
                    if url_queue:
                        url = url_queue.pop(0)
                        if url not in self.visited_urls:
                            batch_urls.append(url)
                
                if not batch_urls:
                    continue
                
                print(f"🔄 Processing batch of {len(batch_urls)} pages...")
                
                # Crawl batch in parallel
                batch_results = await self._crawl_pages_batch(batch_urls, crawler, batch_size=len(batch_urls))
                
                # Process results and extract links
                for page_data in batch_results:
                    if page_data:
                        self.scraped_data.append(page_data)
                        result = await crawler.arun(url=page_data['url'], bypass_cache=True)
                        if result.success:
                            links = await self._extract_links_with_context(result.html, page_data['url'])
                            if links:
                                # Use intelligent link selection
                                selected = self._select_best_links_for_recon(links, count=8)
                                print(f"  → Smart filter: {len(links)} links → {len(selected)} relevant")
                                for link in selected:
                                    if link['url'] not in self.visited_urls and link['url'] not in url_queue:
                                        url_queue.append(link['url'])
                
                print(f"  Progress: {len(self.visited_urls)}/{recon_budget} recon pages\n")
        
        site_analysis = await self._analyze_site_structure()
        self.site_understanding.update(site_analysis)
        
        deep_budget = self.max_pages - len(self.visited_urls)
        self.current_phase = "deep_crawl"
        print(f"\n{'─'*80}")
        print(f"🎯 PHASE 2: TARGETED DEEP CRAWL ({deep_budget} pages)")
        print(f"{'─'*80}\n")
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            url_queue = []
            print("🔗 Seeding deep crawl queue from high-value pages...")
            
            # Parallelize queue seeding - extract links from multiple pages concurrently
            high_value_pages = [page for page in self.scraped_data if page.get('relevance_score', 0) >= 5]
            
            async def extract_links_from_page(page_url):
                """Helper to extract links from a single page."""
                try:
                    result = await crawler.arun(url=page_url, bypass_cache=True)
                    if result.success:
                        links = await self._extract_links_with_context(result.html, page_url)
                        selected = self._select_best_links_for_recon(links, count=7)
                        return [link['url'] for link in selected if link['url'] not in self.visited_urls]
                except Exception as e:
                    print(f"  ⚠ Error extracting links from {page_url}: {str(e)[:50]}")
                return []
            
            # Process pages in batches for link extraction
            batch_size = min(self.concurrency * 2, 5)  # Slightly higher for I/O bound operations
            for i in range(0, len(high_value_pages), batch_size):
                batch = high_value_pages[i:i+batch_size]
                tasks = [extract_links_from_page(page['url']) for page in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, list):
                        url_queue.extend(result)
            
            url_queue = list(dict.fromkeys(url_queue))  # Remove duplicates
            print(f"  ✓ Queue seeded with {len(url_queue)} promising links\n")
            
            # Deep crawl with batching (smaller batches for better AI navigation)
            batch_size = max(2, self.concurrency // 2)  # Smaller batch for AI-guided navigation
            
            while url_queue and len(self.visited_urls) < self.max_pages:
                # Get batch of URLs to process
                remaining_budget = self.max_pages - len(self.visited_urls)
                current_batch_size = min(batch_size, remaining_budget, len(url_queue))
                
                batch_urls = []
                for _ in range(current_batch_size):
                    if url_queue:
                        url = url_queue.pop(0)
                        if url not in self.visited_urls:
                            batch_urls.append(url)
                
                if not batch_urls:
                    continue
                
                # Crawl batch in parallel
                batch_results = await self._crawl_pages_batch(batch_urls, crawler, batch_size=len(batch_urls))
                
                # Process results and get AI navigation for each
                for page_data in batch_results:
                    if page_data:
                        self.scraped_data.append(page_data)
                        result = await crawler.arun(url=page_data['url'], bypass_cache=True)
                        if result.success:
                            links = await self._extract_links_with_context(result.html, page_data['url'])
                            if links:
                                selected_urls = await self._ask_ollama_for_navigation_advanced(page_data['url'], links, page_data.get('ai_extraction', {}))
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


async def generate_ai_answer(scraped_data: List[Dict], crawl_objective: str) -> str:
    """Generate comprehensive AI-powered answer to the user's question."""
    print("\n" + "="*80)
    print("🤖 GENERATING AI-POWERED COMPREHENSIVE ANSWER")
    print("="*80 + "\n")
    
    # Prepare data for AI analysis - Include moderately relevant and above
    all_pages = [p for p in scraped_data if p.get('relevance_score', 0) >= 4]  # Balanced threshold
    
    if not all_pages:
        print("⚠ No relevant data found to summarize.")
        return "No relevant data was found that matches your objective."
    
    # Build comprehensive context from ALL extracted data
    context_parts = []
    for idx, page in enumerate(all_pages[:20], 1):  # Increased from 10 to 20 pages
        ai_extraction = page.get('ai_extraction', {})
        content = ai_extraction.get('key_content', {})
        summary = ai_extraction.get('content_summary', '')
        page_type = page.get('page_type', 'unknown')
        
        context_parts.append(f"=== SOURCE {idx} ({page_type}) ===")
        context_parts.append(f"URL: {page['url']}")
        context_parts.append(f"Summary: {summary}")
        context_parts.append(f"Extracted Data: {json.dumps(content, indent=2)}")
        context_parts.append("=" * 50)
    
    context = "\n".join(context_parts)
    
    # Generate comprehensive summary with AI
    summary_prompt = '''You are an expert analyst tasked with answering a user's specific question based on web-scraped data.

USER'S QUESTION/OBJECTIVE:
"''' + crawl_objective + '''"

IMPORTANT INSTRUCTIONS:
1. Read the user's question VERY CAREFULLY and understand what they are asking for
2. Analyze ALL the extracted data below, even if it seems only remotely related
3. Your PRIMARY GOAL is to DIRECTLY ANSWER the user's question as comprehensively as possible
4. Extract and present EVERY piece of information that could help answer their question
5. If the data is incomplete, mention what was found and what might be missing
6. Be thorough - include ALL relevant details, facts, numbers, names, descriptions, etc.

EXTRACTED DATA FROM ''' + str(len(all_pages)) + ''' WEB PAGES:

''' + context[:15000] + '''

YOUR TASK:
Provide a COMPREHENSIVE, DETAILED answer to the user's question. Structure your response as:

1. **DIRECT ANSWER**: Start with a clear, direct answer to their question
2. **COMPLETE FINDINGS**: Present ALL relevant information found, organized logically
   - Include specific details, numbers, names, descriptions
   - Don't summarize too much - be thorough and detailed
   - If there are lists or multiple items, present them ALL
3. **SUPPORTING DETAILS**: Additional context and related information
4. **DATA COMPLETENESS**: Assess if the scraped data fully answers the question
5. **CONCLUSION**: Final summary addressing the user's objective

CRITICAL: Your answer should be COMPREHENSIVE and DETAILED. The user wants ALL the information available, not just a summary. Include every relevant piece of data you found.'''
    
    try:
        print("🤖 Analyzing all scraped data to answer your question...\n")
        print(f"📊 Processing {len(all_pages)} pages of extracted content...")
        print("⏳ This may take 1-2 minutes for comprehensive analysis...\n")
        
        # Use asyncio to run in executor for async compatibility
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            partial(ollama.generate, model="deepseek-r1:14b", prompt=summary_prompt)
        )
        
        ai_summary = response['response'].strip()
        
        print("="*80)
        print("✨ COMPREHENSIVE ANSWER TO YOUR QUESTION")
        print("="*80 + "\n")
        print(ai_summary)
        print("\n" + "="*80)
        
        return ai_summary
        
    except Exception as e:
        print(f"⚠ Error generating AI summary: {e}")
        return f"Error generating summary: {e}"


def save_results(scraped_data: List[Dict], ai_summary: str, crawl_objective: str, output_dir: str = "."):
    """Save crawling results to files."""
    import os
    
    # Prepare output data
    output_data = {
        "objective": crawl_objective,
        "total_pages_crawled": len(scraped_data),
        "high_value_pages": len([p for p in scraped_data if p.get('relevance_score', 0) >= 6]),
        "extracted_data": [
            {
                "url": page['url'],
                "page_type": page.get('page_type', 'unknown'),
                "relevance": page.get('relevance_score', 0),
                "extracted_content": page.get('ai_extraction', {}).get('key_content', {})
            }
            for page in scraped_data
            if page.get('relevance_score', 0) >= 4
        ]
    }
    
    # Save JSON data
    json_path = os.path.join(output_dir, 'scraped_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {json_path}")
    
    # Save AI answer
    answer_path = os.path.join(output_dir, 'ai_answer.md')
    with open(answer_path, 'w', encoding='utf-8') as f:
        f.write(f"# AI-Generated Answer\n\n")
        f.write(f"**Question/Objective**: {crawl_objective}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
        f.write("---\n\n")
        f.write(ai_summary)
    print(f"✅ Saved: {answer_path}")
    
    print("\n" + "="*80)
    print("🎉 CRAWLING AND ANALYSIS COMPLETE!")
    print("="*80)


async def main():
    """Main execution function."""
    print("=" * 80)
    print("🤖 AGENTIC WEB CRAWLER - LOCAL EDITION")
    print("Schema-less AI-Powered Intelligent Crawling")
    print("=" * 80)
    print()
    
    # Check Ollama connection
    print("ℹ️  This crawler uses deepseek-r1:14b via Ollama")
    print("   Make sure Ollama is running and the model is downloaded")
    print("   (Run: ollama pull deepseek-r1:14b)")
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
    
    print()
    print("⚡ Concurrency settings:")
    print("   Higher = Faster but more resource intensive")
    print("   Recommended: 2-5 for most systems")
    concurrency_input = input("🔢 Concurrent pages to process (default: 3): ").strip()
    concurrency = int(concurrency_input) if concurrency_input.isdigit() else 3
    concurrency = max(1, min(concurrency, 10))  # Clamp between 1-10
    
    # Initialize crawler
    crawler = ImprovedAgenticWebCrawler(
        decision_model="deepseek-r1:14b",
        extraction_model="deepseek-r1:14b",
        max_pages=max_pages,
        concurrency=concurrency
    )
    
    # Set objective
    crawler.crawl_objective = crawl_objective
    
    # Analyze objective with AI
    await crawler.analyze_user_objective(crawl_objective)
    
    # Start crawling
    scraped_data = await crawler.crawl_website(start_url)
    
    print(f"\n✅ Successfully crawled {len(scraped_data)} pages")
    print(f"   High-value pages: {len(crawler.high_value_pages)}")
    if crawler.page_relevance_scores:
        avg_relevance = sum(crawler.page_relevance_scores.values()) / len(crawler.page_relevance_scores)
        print(f"   Average relevance: {avg_relevance:.1f}/10")
    
    # Display scraped data summary
    print("\n" + "="*80)
    print("📦 SCRAPED DATA SUMMARY")
    print("="*80 + "\n")
    output_data = {
        "objective": crawl_objective,
        "total_pages_crawled": len(scraped_data),
        "high_value_pages": len(crawler.high_value_pages),
        "pages_by_relevance": {
            "high (7-10)": len([p for p in scraped_data if p.get('relevance_score', 0) >= 7]),
            "moderate (4-6)": len([p for p in scraped_data if 4 <= p.get('relevance_score', 0) < 7]),
            "low (0-3)": len([p for p in scraped_data if p.get('relevance_score', 0) < 4]),
        }
    }
    print(json.dumps(output_data, indent=2))
    
    # Generate AI-powered answer
    ai_summary = await generate_ai_answer(scraped_data, crawl_objective)
    
    # Save results
    save_results(scraped_data, ai_summary, crawl_objective)


if __name__ == "__main__":
    asyncio.run(main())

