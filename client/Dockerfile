# Stage 1: Build the Vite app
FROM node:20-alpine as build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the Vite app
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built files from Vite to nginx html folder
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
