const { chromium } = require('playwright');
const TARGETS = [5, 10, 25, 60, 100, 200];
const median = a => { const b=[...a].sort((x,y)=>x-y); const m=b.length>>1;
  return b.length%2 ? b[m] : (b[m-1]+b[m])/2; };

(async () => {
  const browser = await chromium.launch();
  console.log('  true |  reported | ratio |  err  | conf high/fair/low | streams | data/hr');
  console.log('-------+-----------+-------+-------+--------------------+---------+--------');
  const ratios = [];
  for (const mbps of TARGETS) {
    const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
    const errs = [];
    page.on('pageerror', e => errs.push(e.message));
    await page.goto('http://127.0.0.1:8099/index.html', { waitUntil: 'load' });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', {
      offline: false, latency: 20,
      downloadThroughput: mbps*1e6/8, uploadThroughput: mbps*1e6/8 });
    await page.selectOption('#interval', '2000');
    await page.click('#toggle');
    await page.waitForTimeout(26000);

    const s = await page.evaluate(() => window.__wsc.speeds().map(
      x => ({ mbps: x.mbps, conf: x.conf, conc: x.conc })));
    const perHour = await page.textContent('#vPerHour');
    const warm = s.slice(2);
    const rep = warm.length ? median(warm.map(x=>x.mbps)) : NaN;
    const c = ['high','fair','low','capped'].map(k => warm.filter(x=>x.conf===k).length);
    ratios.push(rep/mbps);
    console.log(
      String(mbps).padStart(6) + ' | ' + rep.toFixed(1).padStart(9) + ' | ' +
      (rep/mbps).toFixed(3).padStart(5) + ' | ' +
      (((rep/mbps)-1)*100).toFixed(1).padStart(5) + '%' + ' | ' +
      (c[0]+'/'+c[1]+'/'+(c[2]+c[3])).padStart(18) + ' | ' +
      String(median(warm.map(x=>x.conc))||0).padStart(7) + ' | ' + perHour);
    if (errs.length) console.log('   PAGE ERRORS: ' + errs.join('; '));
    await page.close();
  }
  const worst = Math.max(...ratios.map(r=>Math.abs(r-1)));
  console.log('\nall readings within ' + (worst*100).toFixed(1) + '% of the true link speed');
  await browser.close();
})();
