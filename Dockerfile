# ==== Stage 1: Build Frontend (Vite) ====
FROM node:20-alpine as builder

WORKDIR /app

# Copy dependency definition
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the react application
# Define ENV variables if needed for Vite during build
RUN npm run build

# ==== Stage 2: Serve with Nginx ====
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy build files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Expose port (80 is the default in our Nginx config)
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
