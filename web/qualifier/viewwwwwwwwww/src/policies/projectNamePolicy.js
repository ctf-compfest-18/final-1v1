class ProjectNamePolicy {
  constructor(previewUrlFactory) {
    this.previewUrlFactory = previewUrlFactory;
    this.blockedTokens = [
      "localhost",
      "127.",
      "127.0.0.1",
      "0.0.0.0",
      "::1",
      "[::1]",
      "169.254.",
      "metadata",
      "localtest"
    ];
  }

  allows(name) {
    if (typeof name !== "string") return false;

    const preview = name.slice(0, 32);
    if (!/^[a-z0-9-]{3,32}$/.test(preview)) return false;

    const lowered = name.toLowerCase();
    if (this.blockedTokens.some((token) => lowered.includes(token))) return false;

    const target = this.previewUrlFactory.build({ name });
    return this.previewUrlFactory.hasManagedShape(target);
  }
}

module.exports = { ProjectNamePolicy };
