FROM node:20-slim

WORKDIR /app

# Copia arquivos de pacotes para otimização de cache
COPY package.json package-lock.json ./

# Instalação completa (incluindo devDependencies para testes se necessário)
RUN npm install

# O código será montado via Volume para Hot Reload
EXPOSE 5173

# Vite precisa de --host para aceitar conexões externas ao contêiner
# [HOTFIX]: Usar o binário do Vite diretamente para evitar "npm error signal SIGTERM" quando o Docker para o container.
CMD ["./node_modules/.bin/vite", "--host"]
