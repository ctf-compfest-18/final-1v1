const express = require("express");

function createProjectRouter(projectService) {
  const router = express.Router();

  function renderDashboard(res, viewModel = {}) {
    res.render("dashboard", {
      user: res.locals.user,
      projects: projectService.listProjects(res.locals.user.id),
      error: null,
      created: null,
      ...viewModel
    });
  }

  router.get("/", (req, res) => {
    renderDashboard(res);
  });

  router.post("/projects", (req, res) => {
    const result = projectService.createProject(req.user.id, req.body.name);

    if (!result.ok) {
      return res.status(400).render("dashboard", {
        user: req.user,
        projects: projectService.listProjects(req.user.id),
        error: result.error,
        created: null
      });
    }

    return renderDashboard(res, {
      created: result.project
    });
  });

  router.post("/projects/:id/check", async (req, res) => {
    const project = await projectService.checkProject(req.user.id, req.params.id);

    if (!project) {
      return res.status(404).send("project not found");
    }

    return res.redirect(`/#project-${project.id}`);
  });

  return router;
}

module.exports = { createProjectRouter };
