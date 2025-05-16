# Use official Node.js image as the base
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies (including devDependencies for build)
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the app
COPY . .

# Build the Next.js app
RUN npm run build

# Optionally prune devDependencies for a smaller final image
RUN npm prune --production

# Expose the port Next.js runs on
EXPOSE 3000

# Start the Next.js production server
CMD ["npm", "start"]
