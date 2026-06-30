# -------------------------
# Stage 1: Build the application
# -------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the source code and build the production assets
COPY . .
RUN npm run build

# -------------------------
# Stage 2: Serve with Nginx
# -------------------------
FROM nginx:alpine

# Copy the static assets from the build stage to Nginx's default public directory
COPY --from=build /app/dist /usr/share/nginx/html

# Cloud Run injects the $PORT environment variable dynamically (usually 8080).
# This command forces Nginx to listen on that specific port instead of the default 80.
CMD sed -i -e "s/listen       80;/listen       ${PORT:-8080};/g" /etc/nginx/conf.d/default.conf && nginx -g "daemon off;"