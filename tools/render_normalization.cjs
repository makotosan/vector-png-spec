/* Optional independent SVG2 rendering adapter; requires Playwright and Chrome. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const manifest = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.NORMALIZATION_CHROME ? { executablePath: process.env.NORMALIZATION_CHROME } : {})
  });
  try {
    const results = [];
    for (const item of manifest) {
      if (!Number.isInteger(item.width) || !Number.isInteger(item.height) ||
          Math.min(item.width,item.height)<1 || Math.max(item.width,item.height)>4096 ||
          item.width*item.height>4000000) throw new Error('Viewport limit');
      const context = await browser.newContext({
        viewport: { width: item.width, height: item.height }, deviceScaleFactor: 1,
        javaScriptEnabled: false, offline: true, colorScheme: 'light'
      });
      await context.route('**/*', route => route.abort());
      try {
        const page = await context.newPage();
        page.setDefaultTimeout(20000);
        for (const kind of ['before','after']) {
          const bytes = fs.readFileSync(item[kind]);
          if (bytes.length > 1000000) throw new Error('Source limit');
          // Inputs have already passed the fixture input policy. An image document
          // adds isolation; the tool never inserts SVG markup into a live DOM.
          await page.setContent('<html><body style="margin:0;background:transparent"><img width="'+item.width+'" height="'+item.height+'" src="data:image/svg+xml;base64,'+bytes.toString('base64')+'"></body></html>', { waitUntil:'load' });
          await page.locator('img').screenshot({ path: item[kind]+'.png', omitBackground:true, timeout:20000 });
        }
        results.push({ id:item.id, renderer: 'Chromium', version:browser.version(),
          platform:process.platform, fonts:'system fonts of this test host; SVG font-family preserved',
          viewport:[item.width,item.height], background:'transparent', color_alpha:'Chromium sRGB screenshot, decoded RGBA',
          resource_policy:'offline context, abort all network routes, script-disabled SVG image document', mode:'exact', tolerances:0 });
      } finally { await context.close(); }
    }
    fs.writeFileSync(process.argv[2]+'.results.json', JSON.stringify(results,null,2)+'\n');
  } finally { await browser.close(); }
})().catch(err=>{process.stderr.write(String(err)+'\n');process.exitCode=1;});
