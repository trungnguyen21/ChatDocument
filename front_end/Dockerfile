# Build stage
FROM node:20 AS build

ARG PUBLIC_API_URL
ENV PUBLIC_API_URL=http://backend:8000/api

WORKDIR /front_end

COPY package*.json ./
RUN npm install
COPY . .

# Force legacy OpenSSL for Node
ENV NODE_OPTIONS=--openssl-legacy-provider

RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /front_end

RUN npm install -g serve

COPY --from=build /front_end/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
