class PreviewUrlFactory {
  constructor(domain) {
    this.domain = domain;
  }

  build(project) {
    return `http://${project.name}.${this.domain}/status`;
  }

  hasManagedShape(target) {
    return target.startsWith("http://") && target.endsWith(`.${this.domain}/status`);
  }
}

module.exports = { PreviewUrlFactory };
