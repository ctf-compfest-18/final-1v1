const crypto = require("crypto");

class AuthService {
  constructor(userRepository) {
    this.userRepository = userRepository;
  }

  register(rawUsername, rawPassword) {
    const username = String(rawUsername || "").trim().toLowerCase();
    const password = String(rawPassword || "");

    if (!/^[a-z0-9_-]{3,24}$/.test(username)) {
      return {
        ok: false,
        error: "Username must be 3-24 characters using lowercase letters, numbers, underscores, or hyphens."
      };
    }

    if (password.length < 6 || password.length > 72) {
      return {
        ok: false,
        error: "Password must be 6-72 characters."
      };
    }

    if (this.userRepository.findByUsername(username)) {
      return {
        ok: false,
        error: "That username is already taken."
      };
    }

    return {
      ok: true,
      user: this.userRepository.create({
        username,
        passwordHash: this.hashPassword(password)
      })
    };
  }

  login(rawUsername, rawPassword) {
    const username = String(rawUsername || "").trim().toLowerCase();
    const password = String(rawPassword || "");
    const user = this.userRepository.findByUsername(username);

    if (!user || !this.verifyPassword(password, user.passwordHash)) {
      return {
        ok: false,
        error: "Invalid username or password."
      };
    }

    return {
      ok: true,
      user
    };
  }

  findUser(id) {
    return this.userRepository.findById(id);
  }

  hashPassword(password) {
    const salt = crypto.randomBytes(16).toString("hex");
    const hash = crypto.scryptSync(password, salt, 32).toString("hex");
    return `${salt}:${hash}`;
  }

  verifyPassword(password, passwordHash) {
    const [salt, storedHash] = passwordHash.split(":");
    if (!salt || !storedHash) return false;

    const hash = crypto.scryptSync(password, salt, 32);
    const stored = Buffer.from(storedHash, "hex");

    return stored.length === hash.length && crypto.timingSafeEqual(stored, hash);
  }
}

module.exports = { AuthService };
