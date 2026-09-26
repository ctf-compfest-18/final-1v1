FROM mcr.microsoft.com/playwright:v1.45.3-jammy
ENV NODE_ENV=production
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY bot.js .
EXPOSE 3000
CMD ["node", "bot.js"]
