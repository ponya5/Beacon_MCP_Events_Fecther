import asyncio
import json
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()


async def scrape_geektime_events_with_playwright():
    """
    Scrape events from GeekTime using Playwright
    """
    events = []

    async with async_playwright() as p:
        try:
            print("🔗 Launching browser and navigating to GeekTime events page...")

            # Launch browser with realistic user agent
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            # Navigate to the events page
            await page.goto("https://www.geektime.co.il/event/", wait_until="domcontentloaded", timeout=60000)

            print("📄 Waiting for page to load...")
            await asyncio.sleep(3)  # Wait for dynamic content to load

            print("🔍 Extracting events data...")

            # JavaScript code to extract events from the page
            extract_events_js = """
        () => {
            const events = [];

            // Look for event containers using various selectors
            const eventSelectors = [
                '.event-item',
                '.event-card',
                '.event',
                '[class*="event"]',
                '.post',
                'article',
                '.card',
                '.event-container',
                '.upcoming-event'
            ];

            let eventElements = [];
            for (const selector of eventSelectors) {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    console.log(`Found ${elements.length} elements with `
                        + `selector: ${selector}`);
                    eventElements = Array.from(elements);
                    break;
                }
            }

            // If no specific event selectors found, look for common event patterns
            if (eventElements.length === 0) {
                console.log('Trying fallback selectors.');
                const fallbackSelectors = [
                    'div[class*="event"]', 'article[class*="event"]',
                    'section[class*="event"]', 'div[class*="post"]',
                    'article[class*="post"]'
                ];

                for (const selector of fallbackSelectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        eventElements = Array.from(elements);
                        break;
                    }
                }
            }

            console.log(`Processing ${eventElements.length} `
                + `potential events...`);

            // Process each event element (limit to first 20)
            eventElements.slice(0, 20).forEach((element, index) => {
                try {
                    // Extract title
                    let title = null;
                    const titleSelectors = [
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title',
                        '[class*="title"]', '.event-title',
                        '[class*="event-title"]', '.name', '[class*="name"]',
                        'a'
                    ];

                    for (const sel of titleSelectors) {
                        const titleElem = element.querySelector(sel);
                        if (titleElem && titleElem.textContent.trim()) {
                            title = titleElem.textContent.trim();
                            break;
                        }
                    }

                    // Skip if no title found
                    if (!title) {
                        console.log(`Skipping event ${index + 1}: `
                            + `no title found`);
                        return;
                    }

                    // Extract URL
                    let url = null;
                    const linkElem = element.querySelector('a[href]');
                    if (linkElem) {
                        const href = linkElem.getAttribute('href');
                        if (href) {
                            if (href.startsWith('/')) {
                                url = 'https://www.geektime.co.il' + href;
                            } else if (href.startsWith('http')) {
                                url = href;
                            }
                        }
                    }

                    // Extract date/time
                    let datetime = null;
                    const dateSelectors = [
                        '.date', '.time', '.datetime', '[class*="date"]',
                        '[class*="time"]', '[class*="datetime"]',
                        '.event-date', '.event-time', '[data-date]',
                        '[data-time]'
                    ];

                    for (const sel of dateSelectors) {
                        const dateElem = element.querySelector(sel);
                        if (dateElem && dateElem.textContent.trim()) {
                            datetime = dateElem.textContent.trim();
                            break;
                        }
                    }

                    // Extract location/venue
                    let location = null;
                    const locationSelectors = [
                        '.location', '.venue', '.place',
                        '[class*="location"]', '[class*="venue"]',
                        '[class*="place"]', '.event-location',
                        '.event-venue', '[data-location]', '[data-venue]'
                    ];

                    for (const sel of locationSelectors) {
                        const locElem = element.querySelector(sel);
                        if (locElem && locElem.textContent.trim()) {
                            location = locElem.textContent.trim();
                            break;
                        }
                    }

                    // Create event object
                    const event = {
                        title: title,
                        datetime: datetime || 'TBD',
                        location: location || 'TBD',
                        url: url || 'https://www.geektime.co.il/event/'
                    };

                    events.push(event);
                    console.log(`✅ Extracted event ${index + 1}: `
                        + `${title.substring(0, 50)}...`);

                } catch (error) {
                    console.log(`⚠️ Error processing event ${index + 1}: `
                        + `${error.message}`);
                }
            });

            console.log(`🎯 Successfully extracted `
                + `${events.length} events`);
            return events;
        }
        """

            # Execute the JavaScript to extract events
            print("Executing JavaScript evaluation to extract events...")

            # Evaluate JavaScript on the page
            events_data = await page.evaluate(extract_events_js)

            # Convert the returned data to Python objects
            events = json.loads(events_data) if isinstance(events_data, str) else events_data

            print(f"🎯 Successfully extracted {len(events)} events")

            # Close browser
            await browser.close()

            return events

        except Exception as e:
            print(f"❌ Error scraping events: {e}")
            try:
                await browser.close()
            except:
                pass
            return []


def save_events_to_json(events, filename="scrape.json"):
    """
    Save events to JSON file with proper UTF-8 encoding
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(events)} events to {filename}")
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")


async def main():
    """
    Main function to scrape GeekTime events using Playwright MCP
    """
    print("🚀 Starting GeekTime events scraper with Playwright MCP...")

    # Check if OpenAI API key is configured
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("⚠️ Warning: OpenAI API key not configured in .env file")
        print("   Please update OPENAI_API_KEY in .env with "
              "your actual API key")
    else:
        print("✅ OpenAI API key configured")

    events = await scrape_geektime_events_with_playwright()
    save_events_to_json(events)

    print("✨ Scraping completed!")


if __name__ == "__main__":
    asyncio.run(main())
