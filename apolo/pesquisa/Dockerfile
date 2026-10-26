# A imagem oficial já traz o Chromium e as bibliotecas do sistema; a versão tem de ser a mesma do pacote playwright.
FROM mcr.microsoft.com/playwright:v1.64.1-noble
WORKDIR /pesquisa
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
EXPOSE 4000
CMD ["node", "servidor.js"]
