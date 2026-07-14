const { Camoufox } = require('camoufox');
const fs = require('fs');

const COOKIE_PATH = '/home/ubuntu/.hermes/secrets/upwork_cookies.json';

process.on('uncaughtException', (e) => {
  if (e.message?.includes('Cannot read properties of undefined')) return;
  process.exit(1);
});

(async () => {
  const oldCookies = fs.existsSync(COOKIE_PATH) ? JSON.parse(fs.readFileSync(COOKIE_PATH, 'utf8')) : [];

  const browser = await Camoufox({
    headless: true, os: 'windows', humanize: 1.5,
    locale: ['en-US'],
    screen: { min_width: 1280, min_height: 720 }
  });

  const ctx = await browser.newContext({ noDefaultViewport: true });
  const page = await ctx.newPage();
  await page.evaluate(() => { window.resizeTo(1366, 768); });

  if (oldCookies.length > 0) {
    const pwCookies = oldCookies.map(c => ({
      name: c.name, value: c.value,
      domain: c.domain.startsWith('.') ? c.domain : '.' + c.domain,
      path: c.path || '/',
      httpOnly: c.httpOnly || false,
      secure: c.secure || true,
      sameSite: c.sameSite || 'Lax'
    }));
    try { await ctx.addCookies(pwCookies); } catch(e) {}
    console.log('Loaded', oldCookies.length, 'cookies');
  }

  await page.goto('https://www.upwork.com/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);

  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  
  // Extract all text from page
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log('=== BODY TEXT (first 3000) ===');
  console.log(bodyText.substring(0, 3000));
  
  // Try to get the HTML meta info  
  const metaInfo = await page.evaluate(() => {
    // Get all script tags content that might have user data
    const scripts = document.querySelectorAll('script');
    const results = [];
    scripts.forEach(s => {
      const text = s.textContent || '';
      if (text.includes('user') || text.includes('profile') || text.includes('identity')) {
        results.push(text.substring(0, 500));
      }
    });
    return results;
  });
  
  console.log('=== SCRIPTS WITH USER/PROFILE DATA ===');
  metaInfo.forEach((s, i) => {
    console.log(`--- Script ${i+1} ---`);
    console.log(s);
  });
  
  // Also search for common patterns in HTML
  const html = await page.content();
  const searches = ['isimgorulsunn', 'Edel', 'Reister', 'Vanilla', 'displayName', 'fullName', 'userName'];
  for (const s of searches) {
    if (html.includes(s)) {
      // Find context around the match
      const idx = html.indexOf(s);
      console.log(`Found "${s}" at position ${idx}, context:`, html.substring(Math.max(0,idx-80), idx+80));
    }
  }
  
  await page.screenshot({ path: '/tmp/upwork_homepage.png' });
  
  await browser.close();
  console.log('--- DONE ---');
})().catch(e => {
  console.log('ERROR:', e.message);
  process.exit(1);
});
