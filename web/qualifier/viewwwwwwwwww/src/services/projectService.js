class ProjectService {
  constructor({ repository, namePolicy, previewUrlFactory, previewClient, clock }) {
    this.repository = repository;
    this.namePolicy = namePolicy;
    this.previewUrlFactory = previewUrlFactory;
    this.previewClient = previewClient;
    this.clock = clock;
  }

  listProjects(ownerId) {
    return this.repository.allForOwner(ownerId);
  }

  createProject(ownerId, rawName) {
    const name = String(rawName || "").trim();

    if (!this.namePolicy.allows(name)) {
      return {
        ok: false,
        error: "Project names may contain lowercase letters, numbers, and hyphens."
      };
    }

    return {
      ok: true,
      project: this.repository.create(ownerId, name)
    };
  }

  async checkProject(ownerId, id) {
    const project = this.repository.findForOwner(ownerId, id);
    if (!project) return null;

    const target = this.previewUrlFactory.build(project);
    const baseResult = {
      lastChecked: this.clock.timeLabel()
    };

    try {
      const response = await this.previewClient.fetchText(target);

      return this.repository.updateCheckResult(ownerId, id, {
        ...baseResult,
        status: response.ok ? "Online" : `HTTP ${response.status}`,
        lastResponse: response.body.slice(0, 900) || "(empty response)"
      });
    } catch (error) {
      return this.repository.updateCheckResult(ownerId, id, {
        ...baseResult,
        status: "Unreachable",
        lastResponse: `Could not reach ${target}`
      });
    }
  }
}

module.exports = { ProjectService };
