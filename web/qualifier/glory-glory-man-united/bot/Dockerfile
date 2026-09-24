FROM mcr.microsoft.com/playwright:v1.45.4-jammy
ENV NODE_ENV=production
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY bot.js .
EXPOSE 3000
CMD ["node", "bot.js"]
