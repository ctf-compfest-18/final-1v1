const crypto = require('crypto');
const fs = require('fs');
const http = require('http');

const port = Number(process.env.PORT || 3000);
const flag = process.env.FLAG || 'COMPFEST18{queue_zero_local_placeholder_not_for_submission}';
const claims = new Map();
const exportsByToken = new Map();
const lanes = ['north', 'east', 'west'];
const signingKey = crypto.randomBytes(32);

function id(prefix) { return `${prefix}_${crypto.randomBytes(12).toString('hex')}`; }
function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function send(res, status, body, type = 'application/json; charset=utf-8') {
  const value = typeof body === 'string' ? body : JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(value);
}
function readJson(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.setEncoding('utf8');
    req.on('data', chunk => { raw += chunk; if (raw.length > 8192) reject(new Error('body too large')); });
    req.on('end', () => { try { resolve(JSON.parse(raw)); } catch { reject(new Error('invalid json')); } });
    req.on('error', reject);
  });
}
function fragmentFor(claim, lane) {
  return `${lane}.${crypto.createHmac('sha256', signingKey).update(`${claim.id}:${claim.token}:${lane}`).digest('hex').slice(0, 30)}`;
}

const app = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Queue Zero</title><link rel="stylesheet" href="/app.css"></head>
<body><main><div class="tag">Northline Claims / Settlement Desk</div><h1>Queue Zero</h1><p>Open a delayed-shipment claim, then redeem its receipt through a settlement lane. Each receipt is expected to settle once.</p><div class="grid"><section class="panel"><h2>Claim receipt</h2><button id="open">Open compensation claim</button><button class="lane" data-lane="north">Redeem through North lane</button><button class="lane" data-lane="east">Redeem through East lane</button><button class="lane" data-lane="west">Redeem through West lane</button><button id="assemble">Assemble release package</button></section><section class="panel"><h2>Activity</h2><pre id="out">No active claim.</pre></section></div></main><script>
let claim = null, fragments = [];
const out = document.querySelector('#out'); const show = value => out.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
async function request(path, options) { const r = await fetch(path, options); const body = await r.json(); if (!r.ok) throw new Error(body.error || 'request failed'); return body; }
document.querySelector('#open').onclick = async () => { try { claim = await request('/api/claims/start', {method:'POST'}); fragments = []; show(claim); } catch(e) { show(e.message); } };
document.querySelectorAll('[data-lane]').forEach(button => button.onclick = async () => { try { if (!claim) throw new Error('Open a claim first.'); const body = await request('/api/claims/redeem', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({claimId:claim.claimId,token:claim.claimToken,lane:button.dataset.lane})}); fragments.push(body.fragment); show({response:body, fragments}); } catch(e) { show(e.message); } });
document.querySelector('#assemble').onclick = async () => { try { if (!claim) throw new Error('Open a claim first.'); const body = await request('/api/claims/assemble', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({claimId:claim.claimId,fragments})}); show(body); } catch(e) { show(e.message); } };
</script></body></html>`;

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const readOnly = req.method === 'GET' || req.method === 'HEAD';
  try {
    if (readOnly && url.pathname === '/') return send(res, 200, app, 'text/html; charset=utf-8');
    if (readOnly && url.pathname === '/app.css') return send(res, 200, fs.readFileSync(`${__dirname}/public/app.css`, 'utf8'), 'text/css; charset=utf-8');
    if (readOnly && url.pathname === '/health') return send(res, 200, 'ok', 'text/plain; charset=utf-8');

    if (req.method === 'POST' && url.pathname === '/api/claims/start') {
      const claim = { id: id('clm'), token: id('rcpt'), redeemed: false, fragments: new Map(), createdAt: Date.now() };
      claims.set(claim.id, claim);
      return send(res, 201, { claimId: claim.id, claimToken: claim.token, settlementLanes: lanes });
    }

    if (req.method === 'POST' && url.pathname === '/api/claims/redeem') {
      const body = await readJson(req);
      const claim = claims.get(body.claimId);
      if (!claim || claim.token !== body.token || !lanes.includes(body.lane)) return send(res, 404, { error: 'claim receipt not found' });
      if (claim.redeemed) return send(res, 409, { error: 'claim receipt already settled' });
      await delay(180);
      const fragment = fragmentFor(claim, body.lane);
      claim.fragments.set(body.lane, fragment);
      claim.redeemed = true;
      return send(res, 200, { lane: body.lane, fragment, settlement: 'accepted' });
    }

    if (req.method === 'POST' && url.pathname === '/api/claims/assemble') {
      const body = await readJson(req);
      const claim = claims.get(body.claimId);
      if (!claim || !Array.isArray(body.fragments)) return send(res, 404, { error: 'claim not found' });
      const expected = lanes.map(lane => claim.fragments.get(lane));
      if (expected.some(value => !value) || new Set(body.fragments).size !== 3 || !expected.every(value => body.fragments.includes(value))) return send(res, 422, { error: 'three distinct settlement fragments are required' });
      const handoff = id('rel');
      exportsByToken.set(handoff, { used: false });
      return send(res, 200, { release: 'assembled', handoff });
    }

    if (readOnly && url.pathname.startsWith('/api/releases/')) {
      const handoff = url.pathname.slice('/api/releases/'.length);
      const release = exportsByToken.get(handoff);
      if (!release || release.used) return send(res, 404, { error: 'release unavailable' });
      release.used = true;
      return send(res, 200, { label: flag });
    }

    return send(res, 404, { error: 'not found' });
  } catch (error) {
    return send(res, 400, { error: error.message === 'body too large' ? error.message : 'invalid request body' });
  }
});

server.listen(port, '0.0.0.0', () => console.log(`Queue Zero listening on ${port}`));
