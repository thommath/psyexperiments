## Build stage: compile the frontend static files
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build


## Runtime stage: serve with Nginx
FROM nginx:1.27-alpine AS runtime

# Copy built assets to Nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose default HTTP port
EXPOSE 80

# Use the default Nginx start command
CMD ["nginx", "-g", "daemon off;"]


