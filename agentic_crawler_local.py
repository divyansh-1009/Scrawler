"""
🤖 Agentic AI Web Crawler 

Schema-less AI-Powered Intelligent Web Crawling

This script uses:
- Ollama with deepseek-r1:14b for AI-powered decisions
- Crawl4AI for intelligent web crawling
- AI Navigation - LLM figures out which links are relevant
- Schema-less Extraction - LLM determines what's important to scrape
- Two-phase crawling - Reconnaissance + Targeted Deep Dive

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
import ollama
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import NoExtractionStrategy
from bs4 import BeautifulSoup


class ImprovedAgenticWebCrawler:
    """An intelligent web crawler that uses AI to make navigation decisions and extract content schema-lessly."""
    
    def __init__(self, decision_model: str = "deepseek-r1:14b", extraction_model: str = "deepseek-r1:14b", max_pages: int = 50):
        self.decision_model = decision_model
        self.extraction_model = extraction_model
        self.max_pages = max_pages
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
            response = ollama.generate(model=self.decision_model, prompt=prompt)
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
    
    async def _extract_content_with_ai(self, html: str, url: str, markdown: str = "") -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'lxml')
        for tag in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
            tag.decompose()
        page_text = soup.get_text(separator='\n', strip=True)
        content_to_analyze = markdown[:4000] if markdown else page_text[:4000]
        headers = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)][:15]
        main_links = []
        for a in soup.find_all('a', href=True)[:30]:
            text = a.get_text(strip=True)
            if text and len(text) > 2:
                main_links.append(text)
        
        prompt = f"""You are an expert content analyst evaluating a web page for relevance and extracting information.

USER'S OBJECTIVE: {self.crawl_objective}

TARGET DATA TYPES: {', '.join(self.desired_data_types)}
KEY FIELDS TO EXTRACT: {', '.join(self.crawl_objective_analysis.get('key_fields', []))}

PAGE URL: {url}

PAGE HEADERS:
{chr(10).join(headers[:10])}

PAGE CONTENT (excerpt):
{content_to_analyze}

MAIN LINKS:
{', '.join(main_links[:15])}

YOUR TASK - ANALYZE CAREFULLY:

1. **Understand the Objective**: Read the user's objective carefully and understand what they're really asking for

2. **Evaluate Page Relevance** (0-10 scale):
   - 9-10: Directly answers the objective with specific, detailed information
   - 7-8: Contains significant relevant information, clearly related to objective
   - 5-6: Moderately relevant, has some useful information related to objective
   - 3-4: Tangentially related, minor relevance or background information
   - 1-2: Barely related, mostly irrelevant with tiny connection
   - 0: Completely irrelevant (navigation, footer, unrelated content)

3. **Extract Strategically**:
   - For HIGH relevance (7+): Extract EVERYTHING in detail - full text, all items, complete data
   - For MODERATE relevance (4-6): Extract key points and important details
   - For LOW relevance (1-3): Extract only the specifically relevant parts
   - Be thorough but focused on what actually relates to the objective

4. **Quality Over Quantity**: 
   - Don't inflate relevance scores - be honest and accurate
   - Extract complete information, but stay focused on the objective
   - If a page is mostly navigation/footer/ads, score it low

Respond in JSON format:
{{
  "page_type": "...",
  "relevance_score": 0-10,
  "key_content": {{
    // Extract based on relevance level
    // High relevance: comprehensive extraction
    // Moderate: key points and details
    // Low: only specifically relevant parts
  }},
  "reasoning": "Clear explanation of WHY this page got this score and how it relates to the objective",
  "content_summary": "Accurate summary of what useful information is on this page"
}}

CRITICAL: Be accurate with relevance scores. Don't give high scores to barely related content."""

        try:
            response = ollama.generate(model=self.extraction_model, prompt=prompt)
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
            response = ollama.generate(model=self.decision_model, prompt=prompt)
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
            print(f"  ✓ Type: {page_type} | Relevance: {relevance}/10")
            key_content = ai_extraction.get('key_content', {})
            if key_content:
                content_types = list(key_content.keys())
                print(f"  → Extracted: {', '.join(content_types[:3])}")
            return page_data
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:80]}")
            return None
    
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
            response = ollama.generate(model=self.decision_model, prompt=prompt)
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
            while url_queue and len(self.visited_urls) < recon_budget:
                current_url = url_queue.pop(0)
                if current_url in self.visited_urls:
                    continue
                self.visited_urls.add(current_url)
                page_data = await self._crawl_page(current_url, crawler)
                if page_data:
                    self.scraped_data.append(page_data)
                    result = await crawler.arun(url=current_url, bypass_cache=True)
                    if result.success:
                        links = await self._extract_links_with_context(result.html, current_url)
                        if links:
                            selected = links[:8]
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
            for page in self.scraped_data:
                if page.get('relevance_score', 0) >= 5:  # Include moderately relevant pages and above
                    result = await crawler.arun(url=page['url'], bypass_cache=True)
                    if result.success:
                        links = await self._extract_links_with_context(result.html, page['url'])
                        for link in links[:7]:  # Good balance of links to follow
                            if link['url'] not in self.visited_urls:
                                url_queue.append(link['url'])
            url_queue = list(dict.fromkeys(url_queue))
            
            while url_queue and len(self.visited_urls) < self.max_pages:
                current_url = url_queue.pop(0)
                if current_url in self.visited_urls:
                    continue
                self.visited_urls.add(current_url)
                page_data = await self._crawl_page(current_url, crawler)
                if page_data:
                    self.scraped_data.append(page_data)
                    result = await crawler.arun(url=current_url, bypass_cache=True)
                    if result.success:
                        links = await self._extract_links_with_context(result.html, current_url)
                        if links:
                            selected_urls = await self._ask_ollama_for_navigation_advanced(current_url, links, page_data.get('ai_extraction', {}))
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
        
        response = ollama.generate(
            model="deepseek-r1:14b",
            prompt=summary_prompt
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

