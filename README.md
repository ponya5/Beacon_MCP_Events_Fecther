# 🗓️ Beacon MCP Events Fetcher

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![CI](https://img.shields.io/badge/CI-Passing-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**A powerful, intelligent event scraper that aggregates tech events from 20+ websites into a single, clean JSON file.**

[📖 Features](#-features) • [🚀 Quick Start](#-quick-start) • [📊 Latest Results](#-latest-results) • [🌐 Target Websites](#-target-websites) • [📁 Output](#-output-format)

</div>

---

## 🌟 Overview

**Beacon MCP Events Fetcher** is a sophisticated web scraper designed to collect and consolidate technology events from multiple sources. It intelligently scrapes 20 different event websites, extracts relevant information, and creates a single timestamped JSON file with all discovered events.

### 🎯 Key Highlights
- **Intelligent Scraping**: Uses multiple fallback strategies to extract events reliably
- **Respectful Automation**: Includes delays between requests to avoid overwhelming servers
- **Global Coverage**: Targets tech events across multiple countries and cities
- **Clean Architecture**: Modular, maintainable code with comprehensive error handling
- **Rich Output**: Detailed event information including summaries and metadata

---

## 🚀 Features

- **🌐 Multi-Source Aggregation**: Scrapes 20+ event websites simultaneously
- **🧠 Intelligent Extraction**: Multiple CSS selectors and fallback strategies
- **📝 Event Summaries**: Generates descriptions by visiting individual event pages
- **⚡ Async Processing**: Concurrent requests for maximum efficiency
- **🛡️ Error Recovery**: Robust handling of failed requests and missing data
- **🌍 International Support**: Handles UTF-8 and international characters
- **📊 Rich Metadata**: Comprehensive scraping statistics and website performance
- **🔮 AI Integration Ready**: Built-in support for OpenAI API enhancements
- **📅 Timestamped Output**: Organized JSON files with precise timing

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/beacon-mcp-events-fetcher.git
   cd beacon-mcp-events-fetcher
   ```

2. **Install dependencies**
   ```bash
   pip install aiohttp beautifulsoup4 python-dotenv
   ```

3. **Set up environment (Optional - for AI features)**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_actual_openai_api_key_here" > .env
   ```

4. **Run the scraper**
   ```bash
   python consolidated_event_scraper.py
   ```

### 📋 What Happens Next

The scraper will automatically:
1. Visit all 20 configured event websites
2. Extract event information using intelligent selectors
3. Generate summaries for up to 5 events per site
4. Create a consolidated JSON file in `scraped_events/` directory

**Expected runtime:** ~2-3 minutes for full scrape

---

## 📊 Latest Results

<div align="center">

**🕐 Last Successful Scrape:** September 18, 2025
**📈 Performance Metrics:**
- ✅ **83 total events** scraped successfully
- 🌐 **15/20 websites** scraped (75% success rate)
- 📊 **Average 5.53 events** per successful website
- 🏆 **Top performers:**
  - GeekTime Israel: 17 events
  - Excel London: 7 events
  - TechUK: 8 events
  - International Conference Alerts: 15 events

</div>

---

## 📁 Output Format

Each scrape generates a timestamped JSON file with the following structure:

```json
{
  "scraping_metadata": {
    "scraping_timestamp": "2025-09-18T23:12:06.414822",
    "completion_timestamp": "2025-09-18T23:14:00.225123",
    "total_websites_targeted": 20,
    "successful_scrapes": 15,
    "failed_scrapes": 5,
    "total_events_found": 83,
    "average_events_per_successful_site": 5.53,
    "openai_key_configured": false
  },
  "website_scraping_results": [
    {
      "website": "geektime_co_il",
      "url": "https://www.geektime.co.il/event/",
      "status": "success",
      "events_count": 17
    }
  ],
  "consolidated_events": [
    {
      "title": "Tech Conference 2025",
      "date_time": "November 15, 2025",
      "location": "Tel Aviv, Israel",
      "event_url": "https://example.com/event",
      "source_website": "geektime_co_il",
      "source_url": "https://www.geektime.co.il/event/",
      "summary": "A comprehensive technology conference featuring..."
    }
  ]
}
```

**Sample output location:** `scraped_events/consolidated_events_2025-09-18_23-14-00.json`

---

## 🌐 Target Websites

The scraper covers **20 diverse event sources** across multiple countries:

### 🇮🇱 Israel & Middle East
- **GeekTime Israel** - Premier tech events and conferences
- **LaStartup Israel** - Startup and entrepreneurship events

### 🇬🇧 United Kingdom
- **Excel London** - Major exhibition and event venue
- **TechUK** - UK technology industry events

### 🌍 Global & Academic
- **International Conference Alerts** - Academic and research conferences
- **TestSmarter** - Testing and QA events
- **10times.com** - Global event listings (Japan, Argentina, Spain)

### 🤖 AI & Developer Communities
- **AI Tinkerers** - AI/ML meetups (8 cities):
  - Barcelona, Spain
  - San Francisco, CA
  - New York City, NY
  - Miami, FL
  - Tokyo, Japan
  - London, UK
  - Madrid, Spain
  - Buenos Aires, Argentina
  - Tel Aviv, Israel

### 🏢 Corporate & Tech
- **Microsoft Reactor** - Developer events and workshops

---

## 🏗️ Architecture & Technology

### Core Components
- **ConsolidatedEventScraper**: Main orchestration class
- **Async HTTP Client**: Efficient concurrent web requests
- **Intelligent Parsers**: Multiple extraction strategies
- **Summary Generator**: Individual event page analysis
- **Error Handler**: Comprehensive failure recovery

### Technical Stack
- **Python 3.8+** - Core language
- **aiohttp** - Asynchronous HTTP client
- **BeautifulSoup4** - HTML parsing and extraction
- **python-dotenv** - Environment variable management
- **asyncio** - Concurrent processing
- **logging** - Comprehensive activity tracking

### Key Features
- **Multi-strategy parsing** with CSS selectors, XPath, and regex
- **Rate limiting** with respectful delays between requests
- **Content validation** and cleaning
- **Location inference** from URLs and titles
- **Structured data extraction** (JSON-LD, microdata)

---

## 📈 Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Processing Time** | ~2-3 minutes | Full scrape of all websites |
| **Success Rate** | 75% | Websites successfully scraped |
| **Event Yield** | 83+ events | Latest successful run |
| **Request Rate** | ~1-2 seconds | Delay between requests |
| **Concurrent Limit** | 20 | Maximum simultaneous connections |

---

## 🛠️ Configuration

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here  # Optional, for AI features
```

### Target URLs
All scraping targets are configured in `ConsolidatedEventScraper.TARGET_URLS`:
- 20 carefully selected event websites
- Global geographic coverage
- Mix of corporate, academic, and community events

### Scraping Parameters
- **Max events per site:** 30 (configurable)
- **Summary generation:** First 5 events per site
- **Request timeout:** 20 seconds
- **Retry attempts:** Built-in error recovery

---

## 🎯 Usage Examples

### Basic Usage
```bash
python consolidated_event_scraper.py
```

### With Environment Monitoring
```bash
# In one terminal
python consolidated_event_scraper.py

# In another terminal (monitor progress)
tail -f scraped_events/*.json | jq '.scraping_metadata'
```

### Processing Results
```python
import json

# Load latest results
with open('scraped_events/consolidated_events_2025-09-18_23-14-00.json') as f:
    data = json.load(f)

print(f"Found {data['scraping_metadata']['total_events_found']} events!")
```

---

## 🔧 Development

### Code Quality
- **Type Hints**: Full type annotations
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Try-catch blocks throughout
- **Logging**: Detailed progress tracking
- **Modular Design**: Single responsibility principle

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## 📈 Roadmap & Future Enhancements

### 🚀 Planned Features
- **AI-Powered Categorization**: Automatic event topic classification
- **Duplicate Detection**: Identify events listed on multiple sites
- **Real-time Updates**: Continuous monitoring for new events
- **Event Recommendations**: Personalized event suggestions
- **Calendar Integration**: iCal, Google Calendar export
- **API Endpoints**: REST API for programmatic access

### 🤝 Community Contributions Welcome!
- Website selector improvements
- New event source additions
- Performance optimizations
- Mobile app development
- Browser extension

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♂️ Support & Contributing

### Questions?
- Open an issue for bug reports or feature requests
- Check existing issues for similar requests

### Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Acknowledgments
- Built with ❤️ for the tech community
- Thanks to all event organizers sharing their events online
- Inspired by the need for consolidated event discovery

---

<div align="center">

**Made with ❤️ for the global tech community**

[⭐ Star this repo](#) • [🐛 Report Issues](#) • [📧 Contact](#)

</div>