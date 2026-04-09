I need to scrape some basic information from a webpage using a headless browser. Can you help me extract data from the Hacker News homepage?

Please use a headless browser (like Puppeteer with Node.js or Playwright) to visit https://news.ycombinator.com and extract the titles of the top 5 stories displayed on the front page.

Save the extracted titles to a file at /home/user/project/scraped_data/hn_titles.txt with the following format:
- Each title should be on its own line
- Lines should be numbered starting from 1
- Format: "NUMBER. TITLE" (e.g., "1. Some Story Title Here")
- There should be exactly 5 lines in the file
- No empty lines or extra whitespace at the end of the file

Before running the scraper, create the necessary project directory structure at /home/user/project/scraped_data/ if it doesn't exist.

After completing the scrape, create a simple log file at /home/user/project/scraped_data/scrape_log.txt that contains:
- Line 1: The exact text "STATUS: SUCCESS"
- Line 2: The exact text "ITEMS_SCRAPED: 5"
- Line 3: The exact text "SOURCE: https://news.ycombinator.com"
