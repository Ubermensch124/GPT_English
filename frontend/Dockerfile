FROM node:18-alpine

WORKDIR /app

# package.json & package-lock.json
COPY package*.json ./

RUN npm install --production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]