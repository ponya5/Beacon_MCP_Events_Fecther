"""
Consolidated Event Scraper
Scrapes events from all URLs and creates a single consolidated JSON file with timestamp
Uses OpenAI API key from .env file
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConsolidatedEventScraper:
    """Consolidated Event Scraper that creates a single JSON file with all events"""
    
    # All target URLs as specified in requirements
    TARGET_URLS = [
        "https://www.geektime.co.il/event/",
        "https://www.excel.london/",
        "https://www.techuk.org/what-we-deliver/events.html?location=London",
        "https://testsmarter.com/events/",
        "https://internationalconferencealerts.com/argentina/artificial-intelligence",
        "https://www.lastartup.co.il/events/",
        "https://10times.com/japan/technology",
        "https://barcelona.aitinkerers.org/",
        "https://sf.aitinkerers.org/",
        "https://nyc.aitinkerers.org/",
        "https://miami.aitinkerers.org/",
        "https://tokyo.aitinkerers.org/",
        "https://london.aitinkerers.org/",
        "https://madrid.aitinkerers.org/",
        "https://buenos-aires.aitinkerers.org/",
        "https://tlv.aitinkerers.org/",
        "https://10times.com/argentina/technology",
        "https://10times.com/spain/technology/workshops",
        "https://www.geektime.co.il/events/",
        "https://developer.microsoft.com/reactor/"
    ]
    
    def __init__(self):
        self.session = None
        self.all_events = []  # Consolidated list of all events
        self.scraping_stats = {
            "total_websites": len(self.TARGET_URLS),
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "total_events": 0,
            "scraping_start_time": None,
            "scraping_end_time": None,
            "website_results": []
        }
        
        # Check OpenAI API key
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_key or self.openai_key == 'your_openai_api_key_here':
            logger.warning("⚠️ OpenAI API key not properly configured in .env file")
        else:
            logger.info("✅ OpenAI API key loaded from .env")
        
    async def __aenter__(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=aiohttp.ClientTimeout(total=20)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    def get_website_name(self, url: str) -> str:
        """Extract clean website name from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        domain = domain.replace('www.', '')
        return domain.replace('.', '_').replace('-', '_')
    
    def get_timestamp(self) -> str:
        """Get formatted timestamp for filename"""
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL with error handling"""
        try:
            logger.info(f"🔗 Fetching: {url}")
            async with self.session.get(url, ssl=False) as response:
                if response.status == 200:
                    html = await response.text()
                    logger.info(f"✅ Fetched {len(html)} characters from {url}")
                    return html
                else:
                    logger.warning(f"⚠️ HTTP {response.status} for {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching {url}: {str(e)[:100]}")
            return None
    
    def extract_events_from_html(self, html: str, base_url: str, website_name: str) -> List[Dict]:
        """Extract events from HTML using comprehensive selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        # Comprehensive event selectors
        event_selectors = [
            '.event', '.event-item', '.event-card', '.event-listing',
            '.upcoming-event', '.conference-item', '.meetup-item',
            'article', '.post', '.card', '.listing',
            '[class*="event"]', '[class*="conference"]', '[class*="meetup"]',
            '.item', '.entry', 'li'
        ]
        
        event_elements = []
        
        # Try each selector until we find events
        for selector in event_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # Filter out navigation, header, footer elements
                    filtered_elements = [
                        el for el in elements 
                        if not any(parent.name in ['nav', 'header', 'footer'] for parent in el.parents)
                        and len(el.get_text(strip=True)) > 10
                    ]
                    
                    if filtered_elements:
                        event_elements = filtered_elements[:30]  # Limit to 30 events per site
                        logger.info(f"Found {len(event_elements)} events with selector '{selector}'")
                        break
            except Exception:
                continue
        
        # Extract event data
        for i, element in enumerate(event_elements):
            try:
                event_data = self.extract_event_data(element, base_url, website_name)
                if event_data and event_data.get('title'):
                    events.append(event_data)
            except Exception as e:
                logger.debug(f"Error processing event element {i}: {e}")
                continue
        
        logger.info(f"✅ Extracted {len(events)} events from {website_name}")
        return events
    
    def extract_event_data(self, element, base_url: str, website_name: str) -> Optional[Dict]:
        """Extract individual event data from HTML element"""
        # Extract title
        title = self.extract_title(element)
        if not title or len(title.strip()) < 3:
            return None
        
        # Extract other fields
        date_time = self.extract_date_time(element) or 'TBD'
        location = self.extract_location(element) or 'TBD'
        event_url = self.extract_event_url(element, base_url)
        
        return {
            'title': title.strip()[:200],
            'date_time': date_time,
            'location': location,
            'event_url': event_url,
            'source_website': website_name,
            'source_url': base_url,
            'summary': ''  # Will be filled later
        }
    
    def extract_title(self, element) -> Optional[str]:
        """Extract event title using multiple strategies"""
        # Try heading tags first
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading = element.find(tag)
            if heading and heading.get_text(strip=True):
                return heading.get_text(strip=True)
        
        # Try title classes
        title_selectors = [
            '.title', '.event-title', '.name', '.event-name',
            '[class*="title"]', '[class*="name"]', '.heading'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                return title_elem.get_text(strip=True)
        
        # Try link text as fallback
        link = element.find('a')
        if link and link.get_text(strip=True):
            return link.get_text(strip=True)
        
        return None
    
    def extract_date_time(self, element) -> Optional[str]:
        """Extract event date/time"""
        date_selectors = [
            '.date', '.time', '.datetime', '.when',
            '[class*="date"]', '[class*="time"]', '[class*="when"]',
            '.event-date', '.event-time'
        ]
        
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem and date_elem.get_text(strip=True):
                return date_elem.get_text(strip=True).replace('\n', ' ').strip()
        
        return None
    
    def extract_location(self, element) -> Optional[str]:
        """Extract event location"""
        location_selectors = [
            '.location', '.venue', '.place', '.where',
            '[class*="location"]', '[class*="venue"]', '[class*="place"]',
            '.event-location', '.event-venue'
        ]
        
        for selector in location_selectors:
            loc_elem = element.select_one(selector)
            if loc_elem and loc_elem.get_text(strip=True):
                return loc_elem.get_text(strip=True).replace('\n', ' ').strip()
        
        return None
    
    def extract_event_url(self, element, base_url: str) -> str:
        """Extract event URL"""
        link = element.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith('/'):
                return urljoin(base_url, href)
            elif href.startswith('http'):
                return href
        return base_url
    
    async def generate_summary(self, event: Dict) -> str:
        """Generate event summary by visiting the event URL"""
        if not event.get('event_url') or event['event_url'] == 'TBD':
            return "Event details available on the website"
        
        try:
            html = await self.fetch_html(event['event_url'])
            if not html:
                return "Summary not available"
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try meta description first
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                return meta_desc['content'][:200].strip()
            
            # Try og:description
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                return og_desc['content'][:200].strip()
            
            # Try first meaningful paragraph
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30:
                    return text[:200].strip()
            
            return "Event details available on the website"
            
        except Exception as e:
            logger.debug(f"Error generating summary for {event.get('title', 'Unknown')}: {e}")
            return "Summary not available"
    
    async def scrape_website(self, url: str) -> List[Dict]:
        """Scrape events from a single website"""
        website_name = self.get_website_name(url)
        logger.info(f"🔍 Scraping: {website_name}")
        
        try:
            # Fetch HTML content
            html = await self.fetch_html(url)
            if not html:
                self.scraping_stats["failed_scrapes"] += 1
                self.scraping_stats["website_results"].append({
                    "website": website_name,
                    "url": url,
                    "status": "failed_to_fetch",
                    "events_count": 0
                })
                return []
            
            # Extract events from HTML
            events = self.extract_events_from_html(html, url, website_name)
            
            if not events:
                self.scraping_stats["failed_scrapes"] += 1
                self.scraping_stats["website_results"].append({
                    "website": website_name,
                    "url": url,
                    "status": "no_events_found",
                    "events_count": 0
                })
                return []
            
            # Generate summaries for first few events (to be respectful)
            logger.info(f"📝 Generating summaries for {min(len(events), 5)} events from {website_name}")
            for i, event in enumerate(events[:5]):
                summary = await self.generate_summary(event)
                event['summary'] = summary
                await asyncio.sleep(0.5)  # Small delay between summary requests
            
            # Set default summary for remaining events
            for event in events[5:]:
                event['summary'] = "Event details available on the website"
            
            self.scraping_stats["successful_scrapes"] += 1
            self.scraping_stats["website_results"].append({
                "website": website_name,
                "url": url,
                "status": "success",
                "events_count": len(events)
            })
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping {website_name}: {e}")
            self.scraping_stats["failed_scrapes"] += 1
            self.scraping_stats["website_results"].append({
                "website": website_name,
                "url": url,
                "status": f"error: {str(e)[:100]}",
                "events_count": 0
            })
            return []
    
    async def scrape_all_websites(self):
        """Main method to scrape all websites and consolidate results"""
        logger.info(f"🚀 Starting consolidated event scraping for {len(self.TARGET_URLS)} websites")
        self.scraping_stats["scraping_start_time"] = datetime.now().isoformat()
        
        for i, url in enumerate(self.TARGET_URLS, 1):
            logger.info(f"📍 Processing website {i}/{len(self.TARGET_URLS)}")
            
            events = await self.scrape_website(url)
            if events:
                self.all_events.extend(events)
            
            # Respectful delay between websites
            await asyncio.sleep(1)
        
        self.scraping_stats["scraping_end_time"] = datetime.now().isoformat()
        self.scraping_stats["total_events"] = len(self.all_events)
        
        # Save consolidated results
        self.save_consolidated_results()
    
    def save_consolidated_results(self):
        """Save all events to a single consolidated JSON file with timestamp"""
        timestamp = self.get_timestamp()
        filename = f"scraped_events/consolidated_events_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs("scraped_events", exist_ok=True)
        
        # Create consolidated data structure
        consolidated_data = {
            "scraping_metadata": {
                "scraping_timestamp": self.scraping_stats["scraping_start_time"],
                "completion_timestamp": self.scraping_stats["scraping_end_time"],
                "total_websites_targeted": self.scraping_stats["total_websites"],
                "successful_scrapes": self.scraping_stats["successful_scrapes"],
                "failed_scrapes": self.scraping_stats["failed_scrapes"],
                "total_events_found": self.scraping_stats["total_events"],
                "average_events_per_successful_site": round(
                    self.scraping_stats["total_events"] / max(self.scraping_stats["successful_scrapes"], 1), 2
                ),
                "openai_key_configured": bool(self.openai_key and self.openai_key != 'your_openai_api_key_here')
            },
            "website_scraping_results": self.scraping_stats["website_results"],
            "consolidated_events": self.all_events
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎉 Scraping completed successfully!")
            logger.info(f"📊 Final Results:")
            logger.info(f"   • Total websites processed: {self.scraping_stats['total_websites']}")
            logger.info(f"   • Successful scrapes: {self.scraping_stats['successful_scrapes']}")
            logger.info(f"   • Total events found: {self.scraping_stats['total_events']}")
            logger.info(f"   • Average events per site: {consolidated_data['scraping_metadata']['average_events_per_successful_site']}")
            logger.info(f"✅ Consolidated results saved to: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving consolidated results: {e}")
            return None


async def main():
    """Main function to run the consolidated scraper"""
    async with ConsolidatedEventScraper() as scraper:
        await scraper.scrape_all_websites()


if __name__ == "__main__":
    asyncio.run(main())
