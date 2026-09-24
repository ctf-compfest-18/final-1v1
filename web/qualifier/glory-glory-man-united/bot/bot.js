const express = require("express");
const { chromium } = require("playwright");

const WEB_ORIGIN = (process.env.WEB_ORIGIN || "http://web:8000").replace(/\/+$/, "");
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || "dev-admin-token";
const WAIT_MS = parseInt(process.env.BOT_WAIT_MS || "45000", 10);
const PORT = parseInt(process.env.PORT || "3000", 10);
const GAP_MS = parseInt(process.env.BOT_GAP_MS || "2000", 10);
const MAX_QUEUE = parseInt(process.env.BOT_MAX_QUEUE || "50", 10);

const app = express();
app.use(express.json());

const queue = [];
let visited = 0;

app.post("/visit", (req, res) => {
  const path = String((req.body && req.body.path) || "");
  if (!/^\/preview\/[0-9a-f]{32}$/.test(path)) {
    return res.status(400).json({ ok: false, error: "bad path" });
  }
  if (queue.length >= MAX_QUEUE) {
    return res.status(429).json({ ok: false, error: "queue full" });
  }
  queue.push(path);
  res.status(202).json({ ok: true, position: queue.length, waitMs: WAIT_MS });
});

app.get("/healthz", (_req, res) => res.json({ ok: true, queue: queue.length, visited }));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function launch() {
  return chromium.launch({ args: ["--no-sandbox", "--disable-dev-shm-usage"] });
}

async function visit(browser, path) {
  const ctx = await browser.newContext();
  try {
    await ctx.addCookies([{ name: "admin-token", value: ADMIN_TOKEN, url: WEB_ORIGIN }]);
    const page = await ctx.newPage();
    await page.goto(`${WEB_ORIGIN}${path}`, { waitUntil: "load", timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(WAIT_MS);
  } finally {
    await ctx.close().catch(() => {});
  }
}

(async () => {
  let browser = await launch();
  for (;;) {
    const path = queue.shift();
    if (!path) {
      await sleep(400);
      continue;
    }
    try {
      await visit(browser, path);
      visited++;
    } catch (err) {
      console.error("visit failed:", err && err.message);
      try { await browser.close(); } catch (_) {}
      browser = await launch();
    }
    await sleep(GAP_MS);
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});

app.listen(PORT, () => console.log(`bot listening on :${PORT}`));
