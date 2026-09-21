FROM node:22-bookworm-slim

WORKDIR /app

COPY src/package.json ./
COPY src ./src

USER node
EXPOSE 3000

CMD ["node", "src/server.js"]
