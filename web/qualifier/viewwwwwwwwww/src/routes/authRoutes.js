const express = require("express");

function createAuthRouter(authService) {
  const router = express.Router();

  function renderAuth(res, viewModel = {}) {
    res.render("auth", {
      mode: "login",
      error: null,
      username: "",
      ...viewModel
    });
  }

  router.get("/login", (req, res) => {
    if (req.session.userId) return res.redirect("/");
    return renderAuth(res);
  });

  router.post("/login", (req, res) => {
    const result = authService.login(req.body.username, req.body.password);

    if (!result.ok) {
      return res.status(401).render("auth", {
        mode: "login",
        error: result.error,
        username: String(req.body.username || "")
      });
    }

    req.session.userId = result.user.id;
    return res.redirect("/");
  });

  router.get("/register", (req, res) => {
    if (req.session.userId) return res.redirect("/");
    return renderAuth(res, { mode: "register" });
  });

  router.post("/register", (req, res) => {
    const result = authService.register(req.body.username, req.body.password);

    if (!result.ok) {
      return res.status(400).render("auth", {
        mode: "register",
        error: result.error,
        username: String(req.body.username || "")
      });
    }

    req.session.userId = result.user.id;
    return res.redirect("/");
  });

  router.post("/logout", (req, res) => {
    req.session.destroy(() => {
      res.redirect("/login");
    });
  });

  return router;
}

module.exports = { createAuthRouter };
