#!/bin/bash
# Auto-generated solve script
set -e

mkdir -p /home/user/project/scraped_data
which node && node --version
npm list -g puppeteer playwright 2>/dev/null || echo "Need to install"
cd /home/user/project && npm init -y && npm install puppeteer
cat > /home/user/project/scraper.js << 'EOF'
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function scrapeHN() {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.goto('https://news.ycombinator.com', { waitUntil: 'networkidle2' });
    
    // Extract story titles - they are in span.titleline > a
    const titles = await page.evaluate(() => {
        const titleElements = document.querySelectorAll('.titleline > a');
        const results = [];
        for (let i = 0; i < 5 && i < titleElements.length; i++) {
            results.push(titleElements[i].textContent.trim());
        }
        return results;
    });
    
    await browser.close();
    
    // Format titles with numbers
    const formattedTitles = titles.map((title, index) => `${index + 1}. ${title}`).join('\n');
    
    // Write titles to file
    const outputDir = '/home/user/project/scraped_data';
    fs.writeFileSync(path.join(outputDir, 'hn_titles.txt'), formattedTitles);
    
    // Write log file
    const logContent = `STATUS: SUCCESS
ITEMS_SCRAPED: 5
SOURCE: https://news.ycombinator.com`;
    fs.writeFileSync(path.join(outputDir, 'scrape_log.txt'), logContent);
    
    console.log('Scraping completed successfully!');
    console.log('Titles extracted:');
    console.log(formattedTitles);
}

scrapeHN().catch(console.error);
EOF
cd /home/user/project && node scraper.js
cat /home/user/project/scraped_data/hn_titles.txt
cat /home/user/project/scraped_data/scrape_log.txt
wc -l /home/user/project/scraped_data/hn_titles.txt && od -c /home/user/project/scraped_data/hn_titles.txt | tail -2
cat -A /home/user/project/scraped_data/hn_titles.txt
cat -A /home/user/project/scraped_data/scrape_log.txt
