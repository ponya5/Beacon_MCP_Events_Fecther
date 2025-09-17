# Beacon MCP Events Fetcher

A clean, consolidated event scraper that fetches event information from 20 different websites and creates a single timestamped JSON file with all events.

## 🚀 Features

- **Consolidated Output**: Single timestamped JSON file with all events from all websites
- **Clean Architecture**: Modular, maintainable code following best practices
- **OpenAI Integration**: Uses OpenAI API key from .env for future AI enhancements
- **Comprehensive Coverage**: Scrapes 20 different event websites
- **Event Summaries**: Generates brief summaries by visiting individual event URLs
- **Error Handling**: Robust error handling with detailed logging
- **UTF-8 Support**: Properly handles international characters

## 📊 Latest Results

**Last Successful Scrape:** September 17, 2025
- **99 total events** scraped from **15/20 websites** (75% success rate)
- **Average 6.6 events** per successful website
- **Top performers:** LaStartup (30 events), International Conference Alerts (15 events)

## 🛠️ Requirements

- Python 3.8+
- aiohttp
- BeautifulSoup4
- python-dotenv

## ⚙️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Beacon_MCP_Events_Fecther
```

2. Install dependencies:
```bash
pip install aiohttp beautifulsoup4 python-dotenv
```

3. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

## 🎯 Usage

Run the consolidated event scraper:

```bash
python consolidated_event_scraper.py
```

The scraper will:
1. Visit all 20 configured websites
2. Extract event information using intelligent selectors
3. Generate summaries for the first 5 events per site
4. Create a single consolidated JSON file: `scraped_events/consolidated_events_YYYY-MM-DD_HH-MM-SS.json`

## 📋 Output Format

The consolidated JSON file contains:

```json
{
  "scraping_metadata": {
    "scraping_timestamp": "2025-09-17T22:56:03.743243",
    "total_websites_targeted": 20,
    "successful_scrapes": 15,
    "total_events_found": 99,
    "average_events_per_successful_site": 6.6,
    "openai_key_configured": true
  },
  "website_scraping_results": [...],
  "consolidated_events": [
    {
      "title": "Event Title",
      "date_time": "Event Date and Time",
      "location": "Event Location",
      "event_url": "https://event-link.com",
      "source_website": "website_name",
      "source_url": "https://source-website.com",
      "summary": "Brief event description"
    }
  ]
}
```

## 🌐 Target Websites

The scraper covers 20 event websites:

1. **GeekTime Israel** - Tech events and conferences
2. **Excel London** - Exhibition and event venue
3. **TechUK** - UK technology events
4. **TestSmarter** - Testing and QA events
5. **International Conference Alerts** - Academic conferences
6. **LaStartup Israel** - Startup and tech events
7. **10times.com** - Global event listings (Japan, Argentina, Spain)
8. **AI Tinkerers** - AI/ML meetups (8 cities: Barcelona, SF, NYC, Miami, Tokyo, London, Madrid, Buenos Aires, Tel Aviv)
9. **Microsoft Reactor** - Developer events

## 🏗️ Architecture

- **ConsolidatedEventScraper**: Main scraper class with clean separation of concerns
- **Async HTTP**: Efficient concurrent requests using aiohttp
- **Intelligent Selectors**: Multiple fallback strategies for finding events
- **Summary Generation**: Visits individual event URLs to create descriptions
- **Error Recovery**: Graceful handling of failed requests and missing data

## 🔧 Configuration

All target URLs are defined in `ConsolidatedEventScraper.TARGET_URLS`. The scraper automatically:
- Extracts website names for organization
- Handles relative and absolute URLs
- Applies respectful delays between requests
- Limits events per site to avoid overwhelming

## 📈 Performance

- **Processing Time**: ~2 minutes for all 20 websites
- **Success Rate**: 75% (15/20 websites successfully scraped)
- **Event Yield**: 99 events in latest run
- **Respectful Scraping**: 1-2 second delays between requests

## 🎯 Clean Code Principles

- **Single Responsibility**: Each method has one clear purpose
- **Error Handling**: Comprehensive exception handling throughout
- **Logging**: Detailed progress tracking and debugging info
- **Type Hints**: Clear parameter and return types
- **Documentation**: Comprehensive docstrings and comments
- **No Spaghetti Code**: Clean, modular architecture

## 📁 Project Structure

```
Beacon_MCP_Events_Fecther/
├── consolidated_event_scraper.py    # Main scraper (clean, production-ready)
├── scraped_events/                  # Output directory
│   └── consolidated_events_YYYY-MM-DD_HH-MM-SS.json
├── .env                            # OpenAI API key configuration
└── README.md                       # This file
```

## 🔄 Future Enhancements

- **AI-powered event categorization** using OpenAI API
- **Duplicate event detection** across different websites  
- **Event recommendation system** based on user preferences
- **Real-time event updates** with change detection
- **Calendar integration** for easy event management