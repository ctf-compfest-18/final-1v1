FROM node:22-bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV NODE_ENV=production \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    HOME=/tmp \
    XDG_CONFIG_HOME=/tmp/.config \
    XDG_CACHE_HOME=/tmp/.cache

WORKDIR /app

COPY src/package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY src/ .
RUN chown -R root:root /app && chmod -R 755 /app

USER node

EXPOSE 3000

CMD ["node", "app.js"]
