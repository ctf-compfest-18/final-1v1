const crypto = require('crypto');
const http = require('http');

const port = Number(process.env.PORT || 3000);
const flag = process.env.FLAG || 'COMPFEST18{aurora_manifest_local_placeholder_not_for_submission}';
const approvals = new Map();
const jobs = new Map();
const exportsByToken = new Map();

function id(prefix) {
  return `${prefix}_${crypto.randomBytes(12).toString('hex')}`;
}

function send(res, status, body, type = 'application/json; charset=utf-8') {
  const value = typeof body === 'string' ? body : JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(value);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.setEncoding('utf8');
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 16384) reject(new Error('body too large'));
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function firstStringValues(raw) {
  const first = Object.create(null);
  const pairs = /"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"/g;
  for (const match of raw.matchAll(pairs)) {
    const key = JSON.parse(`"${match[1]}"`);
    const value = JSON.parse(`"${match[2]}"`);
    if (!(key in first)) first[key] = value;
  }
  return first;
}

function parseJson(raw) {
  const data = JSON.parse(raw);
  if (!data || Array.isArray(data) || typeof data !== 'object') throw new Error('manifest must be an object');
  if (Object.values(data).some(value => typeof value !== 'string')) throw new Error('only string manifest fields are accepted');
  return data;
}

const app = require('fs').readFileSync(`${__dirname}/views/index.html`, 'utf8');

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const readOnly = req.method === 'GET' || req.method === 'HEAD';
  try {
    if (readOnly && url.pathname === '/') return send(res, 200, app, 'text/html; charset=utf-8');
    if (readOnly && url.pathname === '/app.css') return send(res, 200, require('fs').readFileSync(`${__dirname}/public/app.css`, 'utf8'), 'text/css; charset=utf-8');
    if (readOnly && url.pathname === '/health') return send(res, 200, 'ok', 'text/plain; charset=utf-8');

    if (req.method === 'POST' && url.pathname === '/api/manifests/preview') {
      const raw = await readBody(req);
      parseJson(raw);
      const first = firstStringValues(raw);
      if (!/^[A-Z]{3}-\d{4}$/.test(first.shipment || '')) return send(res, 422, { error: 'shipment reference is invalid' });
      if (first.scope !== 'partner' || first.artifact !== 'dispatch-note') return send(res, 422, { error: 'partner validation only accepts dispatch-note manifests' });
      const approvalId = id('apr');
      approvals.set(approvalId, { raw, used: false, createdAt: Date.now() });
      return send(res, 201, { approvalId, state: 'approved', expiresInSeconds: 90 });
    }

    if (req.method === 'POST' && url.pathname === '/api/manifests/commit') {
      const body = parseJson(await readBody(req));
      const approval = approvals.get(body.approvalId);
      if (!approval || approval.used || Date.now() - approval.createdAt > 90000) return send(res, 404, { error: 'approval is unavailable' });
      approval.used = true;
      const manifest = parseJson(approval.raw);
      if (manifest.scope !== 'control-room' || manifest.artifact !== 'sealed-export') return send(res, 202, { state: 'released', detail: 'standard partner dispatch created' });
      const jobId = id('job');
      jobs.set(jobId, { state: 'queued' });
      setTimeout(() => {
        const handoff = id('xpt');
        exportsByToken.set(handoff, { used: false });
        jobs.set(jobId, { state: 'ready', handoff });
      }, 180);
      return send(res, 202, { jobId, state: 'queued' });
    }

    if (readOnly && url.pathname.startsWith('/api/jobs/')) {
      const job = jobs.get(url.pathname.slice('/api/jobs/'.length));
      return job ? send(res, 200, job) : send(res, 404, { error: 'job not found' });
    }

    if (readOnly && url.pathname.startsWith('/api/exports/')) {
      const handoff = url.pathname.slice('/api/exports/'.length);
      const record = exportsByToken.get(handoff);
      if (!record || record.used) return send(res, 404, { error: 'export unavailable' });
      record.used = true;
      return send(res, 200, { label: flag });
    }

    return send(res, 404, { error: 'not found' });
  } catch (error) {
    return send(res, 400, { error: error.message === 'body too large' ? error.message : 'invalid request body' });
  }
});

server.listen(port, '0.0.0.0', () => console.log(`Aurora Manifest Exchange listening on ${port}`));
