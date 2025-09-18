"""
Consolidated Event Scraper
Scrapes events from all URLs and creates a single consolidated JSON file with timestamp
Uses OpenAI API key from .env file
"""

import asyncio
import aiohttp
import json
import os
import re
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
        location = self.extract_location(element)
        event_url = self.extract_event_url(element, base_url)
        
        # If no location found, try URL-based inference
        if not location:
            location = self._infer_location_from_url(base_url, website_name)
        
        # If still no location, try extracting from title
        if not location:
            location = self._extract_location_from_title(title)
        
        # Default fallback
        if not location:
            location = 'TBD'
        
        return {
            'title': title.strip()[:200],
            'date_time': date_time,
            'location': location,
            'event_url': event_url,
            'source_website': website_name,
            'source_url': base_url,
            'summary': ''  # Will be filled later
        }
    
    def _infer_location_from_url(self, url: str, website_name: str) -> Optional[str]:
        """Infer location from URL patterns and website context"""
        url_lower = url.lower()
        
        # City-specific AI Tinkerers domains
        city_domains = {
            'barcelona.aitinkerers.org': 'Barcelona, Spain',
            'sf.aitinkerers.org': 'San Francisco, CA',
            'nyc.aitinkerers.org': 'New York City, NY',
            'miami.aitinkerers.org': 'Miami, FL',
            'tokyo.aitinkerers.org': 'Tokyo, Japan',
            'london.aitinkerers.org': 'London, UK',
            'madrid.aitinkerers.org': 'Madrid, Spain',
            'buenos-aires.aitinkerers.org': 'Buenos Aires, Argentina',
            'tlv.aitinkerers.org': 'Tel Aviv, Israel'
        }
        
        # Check for exact domain matches
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain in city_domains:
            return city_domains[domain]
        
        # Country/region specific sites
        country_patterns = {
            r'\.co\.il|israel': 'Israel',
            r'\.london|london': 'London, UK',
            r'\.co\.uk|techuk': 'United Kingdom',
            r'argentina|\.ar': 'Argentina',
            r'spain|\.es': 'Spain',
            r'japan|\.jp': 'Japan',
            r'excel\.london': 'London, UK'
        }
        
        for pattern, location in country_patterns.items():
            if re.search(pattern, url_lower):
                return location
        
        # URL path-based inference
        path_patterns = [
            (r'/london|location=london', 'London, UK'),
            (r'/argentina', 'Argentina'),
            (r'/spain', 'Spain'),
            (r'/japan', 'Japan'),
            (r'/tel-?aviv|/tlv', 'Tel Aviv, Israel'),
            (r'/new-?york|/nyc', 'New York, NY'),
            (r'/san-?francisco|/sf', 'San Francisco, CA'),
            (r'/miami', 'Miami, FL'),
            (r'/madrid', 'Madrid, Spain'),
            (r'/barcelona', 'Barcelona, Spain'),
            (r'/buenos-?aires', 'Buenos Aires, Argentina'),
            (r'/tokyo', 'Tokyo, Japan')
        ]
        
        for pattern, location in path_patterns:
            if re.search(pattern, url_lower):
                return location
        
        return None
    
    def _extract_location_from_title(self, title: str) -> Optional[str]:
        """Extract location information from event title"""
        if not title:
            return None
        
        # Common location patterns in titles
        title_location_patterns = [
            r'\b(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "in London", "at New York"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Event|Conference|Meetup|Summit)\b',  # "London Event"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d{4}\b',  # "London 2025"
            r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-–—]\s*',  # "London - Event"
            r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*:\s*',  # "London: Event"
        ]
        
        for pattern in title_location_patterns:
            matches = re.findall(pattern, title)
            for match in matches:
                if self._is_likely_city_name(match):
                    return self._clean_location(match)
        
        return None
    
    def _is_likely_city_name(self, text: str) -> bool:
        """Check if text is likely a city name"""
        if not text or len(text) < 3:
            return False
        
        # Known cities and countries
        known_locations = {
            'london', 'paris', 'berlin', 'madrid', 'barcelona', 'rome', 'amsterdam',
            'new york', 'san francisco', 'los angeles', 'chicago', 'boston', 'miami',
            'toronto', 'vancouver', 'montreal', 'sydney', 'melbourne', 'tokyo',
            'tel aviv', 'jerusalem', 'haifa', 'buenos aires', 'sao paulo', 'mexico city',
            'singapore', 'hong kong', 'seoul', 'mumbai', 'delhi', 'bangalore',
            'dubai', 'abu dhabi', 'cairo', 'johannesburg', 'cape town',
            'israel', 'uk', 'usa', 'canada', 'australia', 'japan', 'spain',
            'france', 'germany', 'italy', 'argentina', 'brazil', 'india'
        }
        
        text_lower = text.lower()
        if text_lower in known_locations:
            return True
        
        # Check if it looks like a city name (capitalized, reasonable length)
        if (text[0].isupper() and
                len(text) >= 3 and
                len(text) <= 30 and
                text.replace(' ', '').isalpha()):
            return True
        
        return False
    
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
        """Extract event location using enhanced multi-strategy approach"""
        # Strategy 1: Enhanced CSS selectors
        location_selectors = [
            # Primary location selectors
            '.location', '.venue', '.place', '.where', '.address',
            '.event-location', '.event-venue', '.event-place', '.event-address',
            '.venue-name', '.venue-address', '.location-name',
            
            # Semantic selectors
            '[class*="location"]', '[class*="venue"]', '[class*="place"]', 
            '[class*="address"]', '[class*="city"]', '[class*="country"]',
            '[data-location]', '[data-venue]', '[data-address]',
            
            # Common patterns
            '.info .location', '.details .location', '.meta .location',
            '.event-info .location', '.event-details .venue',
            '.card-location', '.item-location', '.post-location',
            
            # Icon-based selectors (often location info follows location icons)
            '.fa-map-marker + *', '.fa-location + *', '.icon-location + *',
            '.location-icon + *', '.map-icon + *',
            
            # Alternative text patterns
            '.where-text', '.venue-text', '.location-text', '.address-text'
        ]
        
        for selector in location_selectors:
            try:
                loc_elem = element.select_one(selector)
                if loc_elem and loc_elem.get_text(strip=True):
                    location = loc_elem.get_text(strip=True).replace('\n', ' ').strip()
                    if self._is_valid_location(location):
                        return self._clean_location(location)
            except Exception:
                continue
        
        # Strategy 2: Structured data extraction (JSON-LD, microdata)
        location = self._extract_structured_location(element)
        if location:
            return location
        
        # Strategy 3: Text pattern matching
        location = self._extract_location_from_text(element)
        if location:
            return location
        
        # Strategy 4: Attribute-based extraction
        location = self._extract_location_from_attributes(element)
        if location:
            return location
        
        return None
    
    def _is_valid_location(self, location: str) -> bool:
        """Validate if extracted text is likely a location"""
        if not location or len(location.strip()) < 2:
            return False
        
        # Filter out common non-location texts
        invalid_patterns = [
            r'^(more|details|info|read more|click here|register|book now)$',
            r'^(yes|no|true|false|null|undefined)$',
            r'^[\d\s\-\+\(\)]+$',  # Only numbers/symbols
            r'^[^\w\s]+$',  # Only special characters
            r'^(am|pm|est|pst|cet|utc|gmt)$',  # Time zones only
            r'^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$',  # Month names only
        ]
        
        location_lower = location.lower().strip()
        for pattern in invalid_patterns:
            if re.match(pattern, location_lower):
                return False
        
        return True
    
    def _clean_location(self, location: str) -> str:
        """Clean and standardize location text"""
        # Remove extra whitespace and normalize
        location = ' '.join(location.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['location:', 'venue:', 'where:', 'at:', 'in:', '@']
        for prefix in prefixes_to_remove:
            if location.lower().startswith(prefix):
                location = location[len(prefix):].strip()
        
        # Remove trailing punctuation except important ones
        location = re.sub(r'[,;]+$', '', location)
        
        # Capitalize properly
        if location.islower() or location.isupper():
            location = location.title()
        
        return location[:100]  # Reasonable length limit
    
    def _extract_structured_location(self, element) -> Optional[str]:
        """Extract location from structured data (JSON-LD, microdata)"""
        # Look for JSON-LD structured data
        json_ld_scripts = element.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                location = self._extract_location_from_json_ld(data)
                if location:
                    return location
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Look for microdata
        location_microdata = element.find(attrs={'itemprop': ['location', 'address', 'venue']})
        if location_microdata:
            text = location_microdata.get_text(strip=True)
            if self._is_valid_location(text):
                return self._clean_location(text)
        
        return None
    
    def _extract_location_from_json_ld(self, data) -> Optional[str]:
        """Extract location from JSON-LD structured data"""
        if isinstance(data, list):
            for item in data:
                location = self._extract_location_from_json_ld(item)
                if location:
                    return location
        elif isinstance(data, dict):
            # Check for location field
            if 'location' in data:
                location_data = data['location']
                if isinstance(location_data, str):
                    return self._clean_location(location_data)
                elif isinstance(location_data, dict):
                    # Try common location sub-fields
                    for field in ['name', 'address', 'addressLocality', 'addressRegion']:
                        if field in location_data and isinstance(location_data[field], str):
                            return self._clean_location(location_data[field])
            
            # Check for address field
            if 'address' in data:
                address_data = data['address']
                if isinstance(address_data, str):
                    return self._clean_location(address_data)
                elif isinstance(address_data, dict):
                    # Build address from components
                    address_parts = []
                    for field in ['streetAddress', 'addressLocality', 'addressRegion', 'addressCountry']:
                        if field in address_data and isinstance(address_data[field], str):
                            address_parts.append(address_data[field])
                    if address_parts:
                        return self._clean_location(', '.join(address_parts))
        
        return None
    
    def _extract_location_from_text(self, element) -> Optional[str]:
        """Extract location using text pattern matching"""
        text = element.get_text()
        
        # Common location patterns
        location_patterns = [
            r'(?:location|venue|where|at|in):\s*([^,\n\r]+)',
            r'(?:held at|taking place at|hosted at)\s+([^,\n\r]+)',
            r'(?:📍|🏢|🌍|📌)\s*([^,\n\r]+)',  # Location emojis
            r'(?:Address|Venue|Location):\s*([^\n\r]+)',
            r'(?:City|Country):\s*([^,\n\r]+)',
            r'\b(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+)*)\b',  # "in London" or "at New York"
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if self._is_valid_location(match):
                    return self._clean_location(match)
        
        return None
    
    def _extract_location_from_attributes(self, element) -> Optional[str]:
        """Extract location from HTML attributes"""
        # Check data attributes
        data_attrs = ['data-location', 'data-venue', 'data-address', 'data-city', 'data-country']
        for attr in data_attrs:
            value = element.get(attr)
            if value and self._is_valid_location(value):
                return self._clean_location(value)
        
        # Check title attributes that might contain location
        title = element.get('title', '')
        if title and ('location' in title.lower() or 'venue' in title.lower()):
            # Extract location from title like "Event at Location: Details"
            location_match = re.search(r'(?:at|in)\s+([^:,\n]+)', title, re.IGNORECASE)
            if location_match and self._is_valid_location(location_match.group(1)):
                return self._clean_location(location_match.group(1))
        
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
        """Generate event summary and enhance location by visiting the event URL"""
        if not event.get('event_url') or event['event_url'] == 'TBD':
            return "Event details available on the website"
        
        try:
            html = await self.fetch_html(event['event_url'])
            if not html:
                return "Summary not available"
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to enhance location from event page if current location is TBD
            if event.get('location') == 'TBD':
                enhanced_location = self._extract_location_from_event_page(soup)
                if enhanced_location:
                    event['location'] = enhanced_location
                    logger.debug(f"Enhanced location for '{event.get('title', 'Unknown')}': {enhanced_location}")
            
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
    
    def _extract_location_from_event_page(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract location from individual event page using comprehensive strategies"""
        # Strategy 1: Try the same enhanced location extraction on the full page
        page_body = soup.find('body') or soup
        location = self.extract_location(page_body)
        if location and location != 'TBD':
            return location
        
        # Strategy 2: Look for specific event page patterns
        event_page_selectors = [
            # Event-specific location selectors
            '.event-venue', '.event-location', '.event-address',
            '.venue-info', '.location-info', '.address-info',
            '.event-details .venue', '.event-details .location',
            '.event-meta .venue', '.event-meta .location',
            
            # Common event page structures
            '.sidebar .venue', '.sidebar .location',
            '.event-sidebar .venue', '.event-sidebar .location',
            '.event-content .venue', '.event-content .location',
            
            # Schema.org and structured data
            '[itemtype*="Event"] [itemprop="location"]',
            '[itemtype*="Place"] [itemprop="name"]',
            '[itemtype*="PostalAddress"]',
            
            # Map and address containers
            '.map-container', '.address-container', '.venue-container',
            '.google-map', '.location-map'
        ]
        
        for selector in event_page_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and self._is_valid_location(text) and len(text) > 2:
                        return self._clean_location(text)
            except Exception:
                continue
        
        # Strategy 3: Look for location in page title or headings
        page_title = soup.find('title')
        if page_title:
            title_text = page_title.get_text()
            location = self._extract_location_from_title(title_text)
            if location:
                return location
        
        # Strategy 4: Search for location patterns in all text content
        page_text = soup.get_text()
        location_patterns = [
            r'(?:venue|location|address|where):\s*([^\n\r,]+)',
            r'(?:held at|taking place at|hosted at|located at)\s+([^\n\r,]+)',
            r'(?:📍|🏢|🌍|📌)\s*([^\n\r,]+)',
            r'(?:Address|Venue|Location):\s*([^\n\r]+)',
            r'(?:Join us at|Meet us at|Visit us at)\s+([^\n\r,]+)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if self._is_valid_location(match) and len(match) > 5:
                    return self._clean_location(match)
        
        # Strategy 5: Look for structured data in JSON-LD
        json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    location = self._extract_location_from_json_ld(data)
                    if location:
                        return location
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return None
    
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
            
            logger.info("🎉 Scraping completed successfully!")
            logger.info("📊 Final Results:")
            logger.info(f"   • Total websites processed: {self.scraping_stats['total_websites']}")
            logger.info(f"   • Successful scrapes: {self.scraping_stats['successful_scrapes']}")
            logger.info(f"   • Total events found: {self.scraping_stats['total_events']}")
            avg_events = consolidated_data['scraping_metadata']['average_events_per_successful_site']
            logger.info(f"   • Average events per site: {avg_events}")
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
