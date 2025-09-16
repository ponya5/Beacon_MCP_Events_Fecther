import asyncio
from browser_use import Agent, Browser
from browser_use.llm import ChatOpenAI  # or Gemini, Ollama, etc.
import json

async def main():
    # 1. Start the browser
    browser = Browser(headless=False)
    
    # 2. Choose the LLM backend (here: OpenAI GPT-4o, but you can swap)
    llm = ChatOpenAI(model="gpt-4o", api_key="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")
    
    # 3. Create an agent that ties LLM + browser together
    agent = Agent(
        task="navigate to URL - @https://www.geektime.co.il/event/ then find list of events and return a json array of those events. for each event: title, datetime, location, url to event",
        llm=llm,
        browser=browser,
    )

    # 4. Run the task
    result = await agent.run()
    
    # 5. Save result
    with open("scrape.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(main())