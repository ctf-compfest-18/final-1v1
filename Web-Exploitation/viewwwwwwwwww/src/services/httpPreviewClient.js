const http = require("http");
const https = require("https");

class HttpPreviewClient {
  constructor({ timeoutMs = 2500, maxBodyLength = 1200 } = {}) {
    this.timeoutMs = timeoutMs;
    this.maxBodyLength = maxBodyLength;
  }

  fetchText(target) {
    return new Promise((resolve, reject) => {
      const url = new URL(target);
      const client = url.protocol === "https:" ? https : http;

      const request = client.get(url, { timeout: this.timeoutMs }, (response) => {
        let body = "";

        response.setEncoding("utf8");
        response.on("data", (chunk) => {
          body += chunk;
          if (body.length > this.maxBodyLength) request.destroy();
        });
        response.on("end", () => {
          resolve({
            ok: response.statusCode >= 200 && response.statusCode < 300,
            status: response.statusCode,
            body
          });
        });
      });

      request.on("timeout", () => {
        request.destroy(new Error("request timed out"));
      });
      request.on("error", reject);
    });
  }
}

module.exports = { HttpPreviewClient };
