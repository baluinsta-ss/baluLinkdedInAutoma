import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Callable
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
import re
from urllib.parse import quote_plus, urlparse
import hashlib
from googlesearch import search as google_search  # pip install googlesearch-python


class CurationService:
    """PDF search and download service with multiple methods"""
    
    def __init__(self):
        # PDF download directory
        self.pdf_dir = "curated_pdfs"
        if not os.path.exists(self.pdf_dir):
            os.makedirs(self.pdf_dir)
        
        # Initialize Google Sheets client
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        self.client = gspread.authorize(creds)
        
        # Predefined educational PDF sources
        self.pdf_sources = [
            "https://www.tutorialspoint.com/python/python_tutorial.pdf",
            "https://www.py4e.com/lectures3/Pythonlearn-01-Intro.pdf",
            "https://github.com/PacktPublishing/",
            "https://archive.org/",
        ]
    
    def search_google_pdfs_method1(self, search_query: str, max_results: int = 10) -> List[Dict]:
        """Method 1: Use googlesearch-python library"""
        
        pdfs = []
        
        try:
            query = f"{search_query} filetype:pdf"
            print(f"🔍 Method 1: Searching with googlesearch library: {query}")
            
            # Use googlesearch library
            search_results = google_search(query, num_results=max_results, lang='en', sleep_interval=2)
            
            for idx, url in enumerate(search_results):
                if idx >= max_results:
                    break
                    
                try:
                    # Extract title from URL
                    title = urlparse(url).path.split('/')[-1]
                    title = title.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
                    title = re.sub(r'\s+', ' ', title).strip()
                    
                    if len(title) < 5:
                        title = f"PDF about {search_query} - {idx+1}"
                    
                    pdfs.append({
                        'title': title[:200],
                        'url': url,
                        'resource_type': 'PDF',
                        'source': 'Google Search',
                        'search_query': search_query,
                        'summary': f"Educational PDF about {search_query}"
                    })
                    print(f"✅ Found: {title[:60]}")
                    
                except Exception as e:
                    print(f"⚠️ Error processing URL: {e}")
                    continue
            
            print(f"📚 Method 1 found {len(pdfs)} PDFs")
            return pdfs
            
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            return []
    
    def search_google_pdfs_method2(self, search_query: str, max_results: int = 10) -> List[Dict]:
        """Method 2: Use SerpAPI or similar service (requires API key)"""
        
        pdfs = []
        
        try:
            # Alternative: Use DuckDuckGo search (doesn't require API key)
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(search_query + ' filetype:pdf')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            print(f"🔍 Method 2: Searching DuckDuckGo: {search_query}")
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all result links
                links = soup.find_all('a', class_='result__a')
                
                for link in links[:max_results]:
                    try:
                        url = link.get('href', '')
                        if url and '.pdf' in url.lower():
                            title = link.get_text(strip=True)
                            
                            pdfs.append({
                                'title': title[:200] if title else f"PDF about {search_query}",
                                'url': url,
                                'resource_type': 'PDF',
                                'source': 'DuckDuckGo Search',
                                'search_query': search_query,
                                'summary': f"Educational PDF about {search_query}"
                            })
                            print(f"✅ Found: {title[:60]}")
                    except:
                        continue
            
            print(f"📚 Method 2 found {len(pdfs)} PDFs")
            return pdfs
            
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
            return []
    
    def search_github_pdfs(self, search_query: str, max_results: int = 5) -> List[Dict]:
        """Method 3: Search GitHub for educational PDFs"""
        
        pdfs = []
        
        try:
            # GitHub search
            search_url = f"https://github.com/search?q={quote_plus(search_query + ' extension:pdf')}&type=code"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            print(f"🔍 Method 3: Searching GitHub: {search_query}")
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find PDF file results
                results = soup.find_all('div', class_='f4')
                
                for result in results[:max_results]:
                    try:
                        link = result.find('a')
                        if link:
                            github_url = "https://github.com" + link.get('href', '')
                            
                            # Convert to raw content URL
                            raw_url = github_url.replace('/blob/', '/raw/')
                            
                            title = link.get_text(strip=True)
                            
                            pdfs.append({
                                'title': title[:200] if title else f"GitHub PDF about {search_query}",
                                'url': raw_url,
                                'resource_type': 'PDF',
                                'source': 'GitHub',
                                'search_query': search_query,
                                'summary': f"Open-source PDF about {search_query}"
                            })
                            print(f"✅ Found on GitHub: {title[:60]}")
                    except:
                        continue
            
            print(f"📚 Method 3 found {len(pdfs)} PDFs")
            return pdfs
            
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            return []
    
    def get_curated_pdfs(self, search_query: str) -> List[Dict]:
        """Method 4: Use curated list of known educational PDFs"""
        
        pdfs = []
        
        # Curated educational PDF sources based on topic
        curated_sources = {
            'python': [
                {
                    'title': 'Python Tutorial - Tutorialspoint',
                    'url': 'https://www.tutorialspoint.com/python/python_tutorial.pdf',
                    'summary': 'Complete Python programming tutorial'
                },
                {
                    'title': 'Python for Everybody',
                    'url': 'https://www.py4e.com/lectures3/Pythonlearn-01-Intro.pdf',
                    'summary': 'Python basics for beginners'
                },
                {
                    'title': 'Automate the Boring Stuff with Python',
                    'url': 'https://automatetheboringstuff.com/2e/chapter0/automate_the_boring_stuff_with_python.pdf',
                    'summary': 'Practical Python automation'
                }
            ],
            'java': [
                {
                    'title': 'Java Programming Tutorial',
                    'url': 'https://www.tutorialspoint.com/java/java_tutorial.pdf',
                    'summary': 'Complete Java programming guide'
                }
            ],
            'data structures': [
                {
                    'title': 'Data Structures and Algorithms',
                    'url': 'https://www.tutorialspoint.com/data_structures_algorithms/data_structures_algorithms_tutorial.pdf',
                    'summary': 'DSA fundamentals'
                }
            ],
            'machine learning': [
                {
                    'title': 'Introduction to Machine Learning',
                    'url': 'https://www.tutorialspoint.com/machine_learning/machine_learning_tutorial.pdf',
                    'summary': 'ML basics and algorithms'
                }
            ],
            'web development': [
                {
                    'title': 'HTML Tutorial',
                    'url': 'https://www.tutorialspoint.com/html/html_tutorial.pdf',
                    'summary': 'HTML web development guide'
                },
                {
                    'title': 'JavaScript Tutorial',
                    'url': 'https://www.tutorialspoint.com/javascript/javascript_tutorial.pdf',
                    'summary': 'JavaScript programming guide'
                }
            ],
            'react': [
                {
                    'title': 'React Tutorial',
                    'url': 'https://www.tutorialspoint.com/reactjs/reactjs_tutorial.pdf',
                    'summary': 'React JS framework guide'
                }
            ]
        }
        
        # Match query to curated sources
        query_lower = search_query.lower()
        
        for keyword, sources in curated_sources.items():
            if keyword in query_lower:
                for source in sources:
                    pdfs.append({
                        'title': source['title'],
                        'url': source['url'],
                        'resource_type': 'PDF',
                        'source': 'Curated Educational Resources',
                        'search_query': search_query,
                        'summary': source['summary']
                    })
                    print(f"✅ Curated PDF: {source['title']}")
        
        print(f"📚 Method 4 found {len(pdfs)} curated PDFs")
        return pdfs
    
    def curate_resources_from_topics(
        self,
        topics: List[str],
        max_per_topic: int = 5,
        progress_callback: Callable[[int, str], None] = None
    ) -> List[Dict]:
        """Search for PDFs using multiple methods"""
        
        all_resources = []
        total_topics = len(topics)
        
        for i, topic in enumerate(topics):
            if progress_callback:
                progress = int((i / total_topics) * 30)
                progress_callback(progress, f"🔍 Searching for: {topic}...")
            
            # Try all methods and combine results
            methods = [
                self.get_curated_pdfs(topic),  # Start with curated (most reliable)
                self.search_google_pdfs_method1(topic, max_per_topic),
                self.search_github_pdfs(topic, 3),
                self.search_google_pdfs_method2(topic, max_per_topic)
            ]
            
            topic_pdfs = []
            for method_results in methods:
                topic_pdfs.extend(method_results)
                if len(topic_pdfs) >= max_per_topic:
                    break
            
            all_resources.extend(topic_pdfs[:max_per_topic])
            time.sleep(2)
        
        if not all_resources:
            if progress_callback:
                progress_callback(100, "❌ No PDFs found")
            return []
        
        print(f"📚 Total PDFs found: {len(all_resources)}")
        
        if progress_callback:
            progress_callback(40, "🤖 Scoring with AI...")
        
        # Score resources
        from services.ai_service import AIService
        ai_service = AIService()
        
        for resource in all_resources:
            try:
                resource['relevance_score'] = ai_service.score_slideshare_relevance(resource, topics)
            except:
                resource['relevance_score'] = 7.0
        
        # Sort by relevance
        all_resources.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        if progress_callback:
            progress_callback(50, "📥 Downloading PDFs...")
        
        # Download top 10
        downloaded = []
        for idx, resource in enumerate(all_resources[:10]):
            if progress_callback:
                progress_callback(50 + idx * 4, f"📥 {resource['title'][:40]}...")
            
            try:
                local_path = self._download_pdf(resource['url'], resource['title'])
                resource['local_pdf_path'] = local_path if local_path else ''
                resource['download_status'] = 'success' if local_path else 'failed'
                downloaded.append(resource)
                time.sleep(1)
            except Exception as e:
                print(f"❌ Download error: {e}")
                resource['local_pdf_path'] = ''
                resource['download_status'] = 'failed'
                downloaded.append(resource)
        
        if progress_callback:
            progress_callback(90, "✍️ Generating LinkedIn posts...")
        
        # Generate drafts
        for resource in downloaded:
            try:
                resource['draft_post'] = ai_service.generate_pdf_post_draft(resource)
            except:
                resource['draft_post'] = self._create_simple_draft(resource)
        
        if progress_callback:
            progress_callback(95, "💾 Saving...")
        
        # Save to sheets
        if downloaded:
            self._save_to_sheets(downloaded)
        
        success = len([r for r in downloaded if r['download_status'] == 'success'])
        if progress_callback:
            progress_callback(100, f"✅ Downloaded {success}/{len(downloaded)} PDFs")
        
        return downloaded
    
    def _download_pdf(self, url: str, title: str) -> str:
        """Download PDF from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/pdf,*/*'
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                safe_title = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title])
                safe_title = safe_title[:80]
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"{safe_title}_{url_hash}.pdf"
                filepath = os.path.join(self.pdf_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                
                if os.path.getsize(filepath) > 1000:
                    with open(filepath, 'rb') as f:
                        if f.read(5) == b'%PDF-':
                            print(f"✅ Downloaded: {filename}")
                            return filepath
                    os.remove(filepath)
            return None
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def _create_simple_draft(self, resource: dict) -> str:
        return f"""📚 Free Resource Alert!

Found this PDF: "{resource['title']}"

Perfect for learning {resource['search_query']}! 🚀

🔗 Download: {resource['url']}

#{resource['search_query'].replace(' ', '')} #Learning #FreePDF #TechEducation"""
    
    def _save_to_sheets(self, resources: List[Dict]):
        try:
            sheet = self.client.open("LinkedIn_Resources").worksheet("resources")
            existing = pd.DataFrame(sheet.get_all_records())
            
            for r in resources:
                if existing.empty or r['url'] not in existing.get('url', []).values:
                    r['id'] = len(existing) + 1 if not existing.empty else 1
                    r['created_at'] = datetime.now().isoformat()
                    
                    sheet.append_row([
                        str(r.get('id', '')),
                        str(r.get('title', ''))[:500],
                        str(r.get('url', '')),
                        str(r.get('resource_type', '')),
                        str(r.get('source', '')),
                        str(r.get('search_query', '')),
                        str(r.get('summary', ''))[:500],
                        str(r.get('relevance_score', '')),
                        str(r.get('local_pdf_path', '')),
                        str(r.get('draft_post', ''))[:1000],
                        str(r.get('download_status', '')),
                        str(r.get('created_at', ''))
                    ])
        except Exception as e:
            print(f"❌ Save error: {e}")
