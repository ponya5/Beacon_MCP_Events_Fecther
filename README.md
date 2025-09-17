# Beacon MCP Events Fetcher

A Python script that uses Playwright MCP to scrape events from GeekTime (https://www.geektime.co.il/event/).

## Features

- Scrapes events from GeekTime events page
- Extracts title, datetime, location, and URL for each event
- Saves results to JSON format
- Uses Playwright for headless browser automation
- Environment-based configuration

## Setup

1. Ensure Playwright is installed on your system
2. Install required Python dependencies:
   ```bash
   pip install python-dotenv
   ```

3. Configure your OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

## Usage

Run the script:
```bash
python script.py
```

The script will:
1. Launch a headless Chrome browser
2. Navigate to https://www.geektime.co.il/event/
3. Extract event information using JavaScript evaluation
4. Save the results to `scrape.json`
5. Close the browser

## Live Scraping Features

- **Direct Website Access**: Connects directly to GeekTime website
- **Headless Operation**: Runs invisibly without browser windows
- **Robust Extraction**: Uses multiple CSS selectors for event detection
- **Real-time Data**: Fetches current events from the live website
- **Error Recovery**: Handles network issues and parsing errors gracefully

## Output Format

The script generates a JSON array of events with this structure:

```json
[
  {
    "title": "Event Title",
    "datetime": "Event Date and Time",
    "location": "Event Location",
    "url": "https://www.geektime.co.il/event/event-slug"
  }
]
```

## Notes

- The script connects directly to the live GeekTime website
- Uses multiple CSS selectors to handle various page layouts
- Includes comprehensive error handling for robust operation
- Runs in headless mode for server deployment
- Supports Hebrew text extraction and UTF-8 encoding
