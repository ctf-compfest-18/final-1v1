const crypto = require('crypto');
const fs = require('fs');
const http = require('http');

const port = Number(process.env.PORT || 3000);
const flag = process.env.FLAG || 'COMPFEST18{snowblind_relay_local_placeholder_not_for_submission}';
const signingSecret = process.env.JWT_SECRET || 'icefield-borealis-semaphore';
const exportsByToken = new Map();

function b64(value) { return Buffer.from(value).toString('base64url'); }
function unb64(value) { return Buffer.from(value, 'base64url').toString('utf8'); }
function signPart(value) { return crypto.createHmac('sha256', signingSecret).update(value).digest('base64url'); }
function makeToken(payload) {
  const unsigned = `${b64(JSON.stringify({ alg: 'HS256', typ: 'JWT', kid: 'snowblind-2026-q3' }))}.${b64(JSON.stringify(payload))}`;
  return `${unsigned}.${signPart(unsigned)}`;
}
function verifyToken(token) {
  const parts = token.split('.');
  if (parts.length !== 3) throw new Error('malformed session token');
  const expected = Buffer.from(signPart(`${parts[0]}.${parts[1]}`));
  const supplied = Buffer.from(parts[2]);
  if (expected.length !== supplied.length || !crypto.timingSafeEqual(expected, supplied)) throw new Error('session signature rejected');
  const header = JSON.parse(unb64(parts[0]));
  const payload = JSON.parse(unb64(parts[1]));
  if (header.alg !== 'HS256' || header.kid !== 'snowblind-2026-q3') throw new Error('unsupported session profile');
  return payload;
}
function id(prefix) { return `${prefix}_${crypto.randomBytes(12).toString('hex')}`; }
function send(res, status, body, type = 'application/json; charset=utf-8') {
  const value = typeof body === 'string' ? body : JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(value);
}

const app = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Snowblind Relay</title><link rel="stylesheet" href="/app.css"></head>
<body><main><div class="eyebrow">Polar Relay / Incident Continuity</div><h1>Snowblind Relay</h1><p>Provision a public relay session to inspect the current handoff channel. Reviewer releases remain restricted to the incident relay.</p><section class="panel"><button id="session">Provision public relay session</button><pre id="out">No relay session issued.</pre></section></main><script>
const out = document.querySelector('#out');
document.querySelector('#session').onclick = async () => { const response = await fetch('/api/session'); out.textContent = JSON.stringify(await response.json(), null, 2); };
</script></body></html>`;

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const readOnly = req.method === 'GET' || req.method === 'HEAD';
  try {
    if (readOnly && url.pathname === '/') return send(res, 200, app, 'text/html; charset=utf-8');
    if (readOnly && url.pathname === '/app.css') return send(res, 200, fs.readFileSync(`${__dirname}/public/app.css`, 'utf8'), 'text/css; charset=utf-8');
    if (readOnly && url.pathname === '/assets/relay-terms.txt') return send(res, 200, fs.readFileSync(`${__dirname}/public/assets/relay-terms.txt`, 'utf8'), 'text/plain; charset=utf-8');
    if (readOnly && url.pathname === '/robots.txt') return send(res, 200, 'User-agent: *\nDisallow: /assets/relay-terms.txt\n', 'text/plain; charset=utf-8');
    if (readOnly && url.pathname === '/health') return send(res, 200, 'ok', 'text/plain; charset=utf-8');

    if (readOnly && url.pathname === '/api/session') {
      const token = makeToken({ sub: 'public-console', role: 'viewer', aud: 'public-relay', channel: 'snowblind', iat: Math.floor(Date.now() / 1000) });
      return send(res, 200, { session: token, profile: 'public-relay' });
    }

    if (readOnly && url.pathname === '/api/relay/handoff') {
      const authorization = req.headers.authorization || '';
      if (!authorization.startsWith('Bearer ')) return send(res, 401, { error: 'relay session required' });
      const payload = verifyToken(authorization.slice(7));
      if (payload.role !== 'reviewer') return send(res, 403, { error: 'reviewer role required' });
      if (payload.aud !== 'incident-relay') return send(res, 403, { error: 'incident-relay audience required' });
      if (payload.channel !== 'snowblind') return send(res, 403, { error: 'snowblind channel required' });
      const handoff = id('case');
      exportsByToken.set(handoff, { used: false });
      return send(res, 200, { handoff, status: 'reviewer release approved' });
    }

    if (readOnly && url.pathname.startsWith('/api/exports/')) {
      const handoff = url.pathname.slice('/api/exports/'.length);
      const record = exportsByToken.get(handoff);
      if (!record || record.used) return send(res, 404, { error: 'incident export unavailable' });
      record.used = true;
      return send(res, 200, { label: flag });
    }

    return send(res, 404, { error: 'not found' });
  } catch (error) {
    return send(res, 401, { error: error.message || 'relay session rejected' });
  }
});

server.listen(port, '0.0.0.0', () => console.log(`Snowblind Relay listening on ${port}`));
