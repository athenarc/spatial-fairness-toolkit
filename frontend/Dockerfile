# Dockerfile for dev mode (Vite dev server)
FROM node:20-alpine

# Install pnpm globally
RUN npm install -g pnpm

WORKDIR /app

# Copy package files and install dependencies
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install

# Copy all source code
COPY . .

# Start Vite dev server
CMD ["pnpm", "dev", "--host"]
