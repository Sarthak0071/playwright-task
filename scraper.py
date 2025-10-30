import sys
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# Fix for Windows - Playwright needs this to run properly
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class CareerPageScraper:
    def __init__(self):
        # Keywords to look for in URLs (like /careers, /jobs, etc.)
        self.url_keywords = [
            'career', 'careers', 'job', 'jobs', 'hiring', 'join', 
            'employment', 'opening', 'openings', 'opportunities', 
            'vacancy', 'vacancies', 'recruitment', 'apply', 'position'
        ]
        
        # Keywords to look for in link text (like "We're hiring", "Join us", etc.)
        self.link_text_keywords = [
            'careers', 'jobs', 'hiring', "we're hiring", 'join us',
            'job openings', 'work with us', 'open positions', 
            'apply now', 'join our team', 'work here'
        ]
    
    def is_same_domain(self, main_url, link_url):
        """Check if a link belongs to the same website"""
        main_domain = urlparse(main_url).netloc
        link_domain = urlparse(link_url).netloc
        return main_domain == link_domain or link_domain == ''
    
    def looks_like_career_page(self, url, text=''):
        """Check if URL or link text matches career-related keywords"""
        url = url.lower()
        text = text.lower()
        
        # Check if URL contains any career keywords
        for keyword in self.url_keywords:
            if keyword in url:
                return True
        
        # Check if link text contains any career keywords
        for keyword in self.link_text_keywords:
            if keyword in text:
                return True
        
        return False
    
    async def scrape_website(self, website_url):
        """Main function that does all the scraping work"""
        career_pages = []
        checked_urls = set()  # To avoid checking same URL twice
        
        try:
            # Start Playwright and launch browser
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                page.set_default_timeout(60000)
                
                print(f"Loading website: {website_url}")
                
                # Try to load the main page
                try:
                    await page.goto(website_url, wait_until='networkidle')
                    await asyncio.sleep(3)  # Give it time to fully load
                except Exception as e:
                    await browser.close()
                    return {'error': f'Could not load website: {str(e)}'}
                
                # Scroll down to load any lazy-loaded content
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
                
                # Extract all links from the page
                all_links = await page.evaluate('''() => {
                    const links = [];
                    document.querySelectorAll('a').forEach(a => {
                        if (a.href) {
                            links.push({
                                url: a.href,
                                text: (a.textContent || a.innerText || '').trim()
                            });
                        }
                    });
                    return links;
                }''')
                
                print(f"Found {len(all_links)} links on the page")
                
                # Filter links that might be career pages
                potential_career_links = []
                for link in all_links:
                    url = link['url']
                    text = link['text']
                    
                    # Skip if we already checked this URL
                    if url in checked_urls:
                        continue
                    
                    # Only check links from the same website
                    if not self.is_same_domain(website_url, url):
                        continue
                    
                    # Does this look like a career page?
                    if self.looks_like_career_page(url, text):
                        potential_career_links.append({'url': url, 'text': text})
                        checked_urls.add(url)
                
                print(f"Found {len(potential_career_links)} potential career links")
                
                # If we didn't find any career links, try common career page URLs
                if len(potential_career_links) == 0:
                    print("No career links found, trying common paths...")
                    common_paths = ['/careers', '/jobs', '/career', '/hiring', '/join-us']
                    
                    base = website_url.rstrip('/')
                    for path in common_paths:
                        test_url = base + path
                        try:
                            response = await page.goto(test_url, wait_until='domcontentloaded', timeout=10000)
                            if response and response.status == 200:
                                print(f"✓ Found: {test_url}")
                                potential_career_links.append({
                                    'url': test_url,
                                    'text': f'Common path: {path}'
                                })
                        except:
                            pass  # Page doesn't exist, that's okay
                
                # Now visit each potential career page and verify it
                for link in potential_career_links:
                    try:
                        print(f"Verifying: {link['url']}")
                        await page.goto(link['url'], wait_until='domcontentloaded')
                        await asyncio.sleep(2)
                        
                        # Get page title and content
                        title = await page.title()
                        content = (await page.evaluate('() => document.body.innerText')).lower()
                        
                        # Look for job-related words in the content
                        job_words = ['position', 'role', 'apply', 'responsibilities', 
                                    'requirements', 'opening', 'vacancy', 'full time']
                        has_job_content = any(word in content for word in job_words)
                        
                        # Add to results if it's a real career page
                        if has_job_content or self.looks_like_career_page(link['url']):
                            career_pages.append({
                                'url': link['url'],
                                'title': title,
                                'link_text': link['text'],
                                'verified': has_job_content
                            })
                    
                    except Exception as e:
                        # Couldn't load this page, but add it anyway
                        print(f"Error checking {link['url']}: {str(e)}")
                        career_pages.append({
                            'url': link['url'],
                            'title': 'Could not load page',
                            'link_text': link['text'],
                            'verified': False
                        })
                
                await browser.close()
                
                # Return the results
                return {
                    'success': True,
                    'total_links_found': len(all_links),
                    'career_pages': career_pages,
                    'count': len(career_pages)
                }
        
        except Exception as e:
            return {'error': f'Something went wrong: {str(e)}'}
    
    def scrape_career_pages(self, website_url):
        """Public method to start scraping (handles async internally)"""
        # Create a fresh event loop for this scraping task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async scraping function
            result = loop.run_until_complete(self.scrape_website(website_url))
            return result
        except Exception as e:
            return {'error': f'Error: {str(e)}'}
        finally:
            loop.close()