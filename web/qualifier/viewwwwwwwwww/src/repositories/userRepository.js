class UserRepository {
  constructor() {
    this.users = [];
    this.nextId = 1;
  }

  create({ username, passwordHash }) {
    const user = {
      id: this.nextId,
      username,
      passwordHash
    };

    this.nextId += 1;
    this.users.push(user);
    return user;
  }

  findById(id) {
    return this.users.find((user) => user.id === Number(id));
  }

  findByUsername(username) {
    return this.users.find((user) => user.username === username);
  }
}

module.exports = { UserRepository };
