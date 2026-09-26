FROM node:22-alpine

WORKDIR /app

COPY src/package*.json ./
RUN npm ci --omit=dev

COPY src/ .

ENV NODE_ENV=production
ENV PORT=8080

RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 8080
CMD ["npm", "start"]
