/**
 * Meet diagnostic: screenshot + dump all buttons + body text
 * Usage: cd /home/ubuntu/meet-bot && DISPLAY=:99 node diag.js
 * 
 * Run this BEFORE guessing why the bot can't join.
 * It reveals what the page ACTUALLY shows vs your assumptions.
 */
const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
chromium.use(StealthPlugin());

const MEET_URL = process.argv[2] || 'https://meet.google.com/ake-fqyg-mfw';

(async () => {
  const profileDir = require('os').homedir() + '/.meet-chrome';
  
  const context = await chromium.launchPersistentContext(profileDir, {
    headless: false,
    args: ['--no-sandbox', '--disable-blink-features=AutomationControlled'],
    viewport: { width: 1366, height: 768 },
  });
  
  const page = await context.newPage();
  
  await page.goto(MEET_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  console.log('URL:', page.url());
  
  await page.waitForTimeout(5000);
  
  // Screenshot
  await page.screenshot({ path: '/tmp/meet-page.png', fullPage: false });
  console.log('Screenshot saved to /tmp/meet-page.png');
  
  // Full body text
  const body = await page.evaluate(() => document.body?.innerText || '');
  console.log('BODY TEXT:\n' + body.substring(0, 1000));
  
  // All interactive elements
  const buttons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button, [role="button"], a[href]'))
      .slice(0, 20)
      .map(b => ({
        tag: b.tagName,
        text: (b.textContent || '').trim().substring(0, 80),
        aria: b.getAttribute('aria-label') || '',
        role: b.getAttribute('role') || '',
      }));
  });
  console.log('BUTTONS:', JSON.stringify(buttons, null, 2));
  
  await context.close();
  console.log('Done');
})();
