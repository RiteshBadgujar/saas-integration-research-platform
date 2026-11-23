const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const FILE = 'file:///d:/SaaS%20Integration%20Intelligence%20%26%20Research%20Automation/index.html';
const OUT = 'd:/SaaS Integration Intelligence & Research Automation/screenshots';

if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

(async () => {
  console.log('Launching Puppeteer...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--allow-file-access-from-files']
  });

  // ── Desktop screenshots ────────────────────────────────────────────────────
  const desktop = await browser.newPage();
  await desktop.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1.5 });
  console.log('Loading file...');
  await desktop.goto(FILE, { waitUntil: 'networkidle0', timeout: 30000 });
  // Wait for charts to render
  await new Promise(r => setTimeout(r, 3000));

  console.log('Screenshot 1: Hero + KPI cards');
  await desktop.screenshot({ path: `${OUT}/01_desktop_hero.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 2: Auth charts');
  await desktop.evaluate(() => document.querySelector('#auth').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/02_desktop_auth_charts.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 3: Buildability + Composio');
  await desktop.evaluate(() => document.querySelector('#buildability').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/03_desktop_buildability.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 4: MCP + Category cards');
  await desktop.evaluate(() => document.querySelector('#mcp').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/04_desktop_mcp.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 5: Category cards');
  await desktop.evaluate(() => document.querySelector('#categories').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/05_desktop_categories.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 6: 100-App dataset table');
  await desktop.evaluate(() => document.querySelector('#dataset').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/06_desktop_table.png`, clip: { x:0, y:0, width:1440, height:900 } });

  // Test search filter
  await desktop.type('#appSearch', 'HubSpot');
  await new Promise(r => setTimeout(r, 600));
  await desktop.screenshot({ path: `${OUT}/07_desktop_table_search.png`, clip: { x:0, y:0, width:1440, height:900 } });
  await desktop.evaluate(() => document.querySelector('#appSearch').value = '');
  await desktop.evaluate(() => document.querySelector('#appSearch').dispatchEvent(new Event('input')));

  console.log('Screenshot 8: Audit table');
  await desktop.evaluate(() => document.querySelector('#audit').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/08_desktop_audit.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 9: Accuracy + confusion matrix');
  await desktop.evaluate(() => document.querySelector('#accuracy').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/09_desktop_accuracy.png`, clip: { x:0, y:0, width:1440, height:900 } });

  console.log('Screenshot 10: Recommendations');
  await desktop.evaluate(() => document.querySelector('#recommendations').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await desktop.screenshot({ path: `${OUT}/10_desktop_recommendations.png`, clip: { x:0, y:0, width:1440, height:900 } });

  // ── Mobile screenshots ─────────────────────────────────────────────────────
  const mobile = await browser.newPage();
  await mobile.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
  console.log('Loading mobile view...');
  await mobile.goto(FILE, { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));

  console.log('Screenshot 11: Mobile hero');
  await mobile.screenshot({ path: `${OUT}/11_mobile_hero.png`, clip: { x:0, y:0, width:390, height:844 } });

  await mobile.evaluate(() => document.querySelector('#auth').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await mobile.screenshot({ path: `${OUT}/12_mobile_auth.png`, clip: { x:0, y:0, width:390, height:844 } });

  await mobile.evaluate(() => document.querySelector('#dataset').scrollIntoView());
  await new Promise(r => setTimeout(r, 500));
  await mobile.screenshot({ path: `${OUT}/13_mobile_table.png`, clip: { x:0, y:0, width:390, height:844 } });

  await browser.close();
  console.log('Done! Screenshots saved to:', OUT);

  // List files
  const files = fs.readdirSync(OUT).filter(f => f.endsWith('.png'));
  files.forEach(f => {
    const size = fs.statSync(`${OUT}/${f}`).size;
    console.log(`  ${f}: ${(size/1024).toFixed(1)} KB`);
  });
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
