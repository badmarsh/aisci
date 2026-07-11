const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3001');

  // Wait for React to hydrate
  await page.waitForTimeout(2000);

  const getBg = () => page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  const getHtmlClass = () => page.evaluate(() => document.documentElement.className);

  console.log('Before click:');
  console.log('HTML class:', await getHtmlClass());
  console.log('Body bg:', await getBg());

  // Click the switch (role="switch")
  await page.click('button[role="switch"]');
  await page.waitForTimeout(1000);

  console.log('After click:');
  console.log('HTML class:', await getHtmlClass());
  console.log('Body bg:', await getBg());

  await browser.close();
})();
