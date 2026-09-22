class ProjectRepository {
  constructor(seedProjects = []) {
    this.projects = seedProjects.map((project) => ({ ...project }));
    this.nextId = this.projects.reduce((max, project) => Math.max(max, project.id), 0) + 1;
  }

  allForOwner(ownerId) {
    return this.projects.filter((project) => project.ownerId === ownerId);
  }

  create(ownerId, name) {
    const project = {
      id: this.nextId,
      ownerId,
      name,
      status: "Queued",
      lastChecked: "Never",
      lastResponse: "Waiting for the first service check."
    };

    this.nextId += 1;
    this.projects.unshift(project);
    return project;
  }

  findForOwner(ownerId, id) {
    return this.projects.find((project) => project.ownerId === ownerId && project.id === Number(id));
  }

  updateCheckResult(ownerId, id, result) {
    const project = this.findForOwner(ownerId, id);
    if (!project) return null;

    Object.assign(project, result);
    return project;
  }
}

module.exports = { ProjectRepository };
