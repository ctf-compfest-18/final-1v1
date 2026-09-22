"use strict";

const crypto = require("crypto");
const express = require("express");
const session = require("express-session");
const puppeteer = require("puppeteer-core");


const app = express();
const port = Number(process.env.PORT || 3000);
const flag =
  process.env.FLAG ||
  "COMPFEST18{http_only_does_not_stop_same_origin_xss_92d4b7e6ac}";
const botToken = process.env.BOT_TOKEN || crypto.randomBytes(24).toString("hex");
const browserExecutable =
  process.env.PUPPETEER_EXECUTABLE_PATH || "/usr/bin/chromium";

app.disable("x-powered-by");
app.use(express.urlencoded({extended: false, limit: "32kb"}));
app.use(express.json({limit: "32kb"}));
app.use("/static", express.static("static", {fallthrough: false}));
app.use(
  session({
    secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString("hex"),
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      sameSite: "lax",
      secure: false,
      maxAge: 30 * 60 * 1000,
    },
  }),
);

const users = new Map([
  [
    "player",
    {
      password: "training123",
      displayName: "Hacker Class Participant",
      role: "participant",
    },
  ],
  [
    "admin",
    {
      password: crypto.randomBytes(32).toString("hex"),
      displayName: "Feedback Reviewer",
      role: "admin",
    },
  ],
]);

const posts = new Map();
const messages = new Map([["player", []], ["admin", []]]);
const reportStatus = new Map();
let nextPostId = 100;
let reportQueue = Promise.resolve();


function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function sanitizePost(value) {
  return String(value)
    .replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, "")
    .replace(/<script\b[^>]*\/?\s*>/gi, "");
}


function page(title, body) {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${escapeHtml(title)}</title>
    <link rel="stylesheet" href="/static/app.css">
  </head>
  <body>${body}</body>
</html>`;
}


function requireLogin(req, res, next) {
  if (!req.session.username) {
    return res.redirect("/login");
  }
  next();
}


function requireAdmin(req, res, next) {
  const user = users.get(req.session.username);
  if (!user || user.role !== "admin") {
    return res.status(403).send("Administrator access is required.");
  }
  next();
}


function isLoopback(address) {
  return (
    address === "127.0.0.1" ||
    address === "::1" ||
    address === "::ffff:127.0.0.1"
  );
}


async function visitPost(postId) {
  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: browserExecutable,
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-breakpad",
        "--disable-crash-reporter",
        "--user-data-dir=/tmp/chromium-profile",
        "--js-flags=--jitless",
      ],
    });

    const browserPage = await browser.newPage();
    await browserPage.setRequestInterception(true);
    browserPage.on("request", (interceptedRequest) => {
      const target = new URL(interceptedRequest.url());
      if (target.hostname === "127.0.0.1") {
        interceptedRequest.continue();
      } else {
        interceptedRequest.abort();
      }
    });

    const loginUrl =
      `http://127.0.0.1:${port}/internal/bot-login` +
      `?token=${encodeURIComponent(botToken)}&post=${postId}`;
    await browserPage.goto(loginUrl, {
      waitUntil: "domcontentloaded",
      timeout: 8000,
    });
    await new Promise((resolve) => setTimeout(resolve, 2500));
    reportStatus.set(postId, "visited");
  } catch (error) {
    console.error(`Browser review failed for post ${postId}:`, error.message);
    reportStatus.set(postId, "failed");
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}


app.get("/health", (_req, res) => {
  res.json({status: "ok"});
});


app.get("/", (req, res) => {
  if (req.session.username) {
    return res.redirect("/dashboard");
  }
  res.redirect("/login");
});


app.get("/login", (_req, res) => {
  res.send(
    page(
      "Feedback Board",
      `<main class="narrow">
        <section class="card">
          <h1>Feedback Board</h1>
          <p class="muted">Sign in to publish a report for the review team.</p>
          <form method="post" action="/login">
            <label for="username">Username</label>
            <input id="username" name="username" autocomplete="username" required>
            <label for="password">Password</label>
            <input id="password" name="password" type="password" autocomplete="current-password" required>
            <button type="submit">Sign in</button>
          </form>
        </section>
      </main>`,
    ),
  );
});


app.post("/login", (req, res) => {
  const username = String(req.body.username || "");
  const password = String(req.body.password || "");
  const user = users.get(username);
  if (!user || user.password !== password) {
    return res.status(401).send(
      page(
        "Sign-in failed",
        `<main class="narrow">
          <section class="card">
            <h1>Sign-in failed</h1>
            <p class="error">Invalid username or password.</p>
            <a class="button" href="/login">Try again</a>
          </section>
        </main>`,
      ),
    );
  }

  req.session.regenerate((error) => {
    if (error) {
      return res.status(500).send("Unable to create a session.");
    }
    req.session.username = username;
    res.redirect("/dashboard");
  });
});


app.post("/logout", requireLogin, (req, res) => {
  req.session.destroy(() => res.redirect("/login"));
});


app.get("/dashboard", requireLogin, (req, res) => {
  const username = req.session.username;
  const user = users.get(username);
  const ownPosts = [...posts.values()].filter((post) => post.owner === username);
  const inbox = messages.get(username) || [];

  const postRows =
    ownPosts.length === 0
      ? `<p class="muted">No reports have been published yet.</p>`
      : ownPosts
          .map(
            (post) =>
              `<li>
                <a href="/posts/${post.id}">#${post.id} — ${escapeHtml(post.title)}</a>
                <span class="muted">Review status: ${escapeHtml(reportStatus.get(post.id) || "not submitted")}</span>
              </li>`,
          )
          .join("");

  const messageRows =
    inbox.length === 0
      ? `<p class="muted">Your inbox is empty.</p>`
      : inbox
          .map(
            (message) =>
              `<article class="message">
                <strong>From ${escapeHtml(message.from)}</strong>
                <p>${escapeHtml(message.content)}</p>
              </article>`,
          )
          .join("");

  res.send(
    page(
      "Feedback Dashboard",
      `<main>
        <header>
          <div>
            <h1>Feedback Dashboard</h1>
            <p class="muted">Signed in as ${escapeHtml(user.displayName)}</p>
          </div>
          <form method="post" action="/logout">
            <button class="secondary" type="submit">Sign out</button>
          </form>
        </header>

        <section class="grid">
          <article class="card">
            <h2>New report</h2>
            <p class="muted">Basic formatting is supported in the report body.</p>
            <form method="post" action="/posts">
              <label for="title">Title</label>
              <input id="title" name="title" maxlength="80" required>
              <label for="body">Report body</label>
              <textarea id="body" name="body" maxlength="4000" required></textarea>
              <button type="submit">Publish report</button>
            </form>
          </article>

          <article class="card">
            <h2>Your reports</h2>
            <ul class="post-list">${postRows}</ul>
          </article>
        </section>

        <section class="card">
          <h2>Inbox</h2>
          <div id="inbox">${messageRows}</div>
        </section>
      </main>`,
    ),
  );
});


app.post("/posts", requireLogin, (req, res) => {
  const title = String(req.body.title || "").trim();
  const body = String(req.body.body || "");
  if (!title || !body || title.length > 80 || body.length > 4000) {
    return res.status(400).send("Invalid report.");
  }

  const post = {
    id: nextPostId,
    owner: req.session.username,
    title,
    body: sanitizePost(body),
  };
  nextPostId += 1;
  posts.set(post.id, post);
  reportStatus.set(post.id, "not submitted");
  res.redirect(`/posts/${post.id}`);
});


app.get("/posts/:postId", requireLogin, (req, res) => {
  const postId = Number(req.params.postId);
  const post = posts.get(postId);
  if (!post) {
    return res.status(404).send("Report not found.");
  }

  const isOwner = post.owner === req.session.username;
  const reportForm = isOwner
    ? `<form method="post" action="/posts/${post.id}/report">
        <button type="submit">Submit to review team</button>
      </form>`
    : "";

  res.send(
    page(
      post.title,
      `<main>
        <article class="card">
          <p><a href="/dashboard">Back to dashboard</a></p>
          <h1>${escapeHtml(post.title)}</h1>
          <p class="muted">Published by ${escapeHtml(post.owner)}</p>
          <section class="report-body">${post.body}</section>
          ${reportForm}
        </article>
      </main>`,
    ),
  );
});


app.post("/posts/:postId/report", requireLogin, (req, res) => {
  const postId = Number(req.params.postId);
  const post = posts.get(postId);
  if (!post || post.owner !== req.session.username) {
    return res.status(404).send("Report not found.");
  }
  if (reportStatus.get(postId) === "queued") {
    return res.status(409).send("This report is already queued.");
  }

  reportStatus.set(postId, "queued");
  reportQueue = reportQueue.then(() => visitPost(postId));
  res.redirect("/dashboard");
});


app.get("/api/reports/:postId", requireLogin, (req, res) => {
  const postId = Number(req.params.postId);
  const post = posts.get(postId);
  if (!post || post.owner !== req.session.username) {
    return res.status(404).json({error: "Report not found."});
  }
  res.json({post_id: postId, status: reportStatus.get(postId)});
});


app.get("/api/messages", requireLogin, (req, res) => {
  res.json(messages.get(req.session.username) || []);
});


app.post("/api/messages", requireLogin, (req, res) => {
  const recipient = String(req.body.recipient || "");
  const content = String(req.body.message || "");
  if (!users.has(recipient) || !content || content.length > 1000) {
    return res.status(400).json({error: "Invalid message."});
  }

  messages.get(recipient).push({
    from: req.session.username,
    content,
  });
  res.status(201).json({status: "delivered"});
});


app.get("/admin/flag", requireLogin, requireAdmin, (_req, res) => {
  res.type("text/plain").send(flag);
});


app.get("/internal/bot-login", (req, res) => {
  if (!isLoopback(req.socket.remoteAddress) || req.query.token !== botToken) {
    return res.status(404).send("Not found.");
  }

  const postId = Number(req.query.post);
  if (!posts.has(postId)) {
    return res.status(404).send("Report not found.");
  }

  req.session.regenerate((error) => {
    if (error) {
      return res.status(500).send("Unable to create a reviewer session.");
    }
    req.session.username = "admin";
    res.redirect(`/posts/${postId}`);
  });
});


app.listen(port, "0.0.0.0", () => {
  console.log(`Feedback Board is listening on port ${port}.`);
});
