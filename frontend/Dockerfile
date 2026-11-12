# syntax=docker/dockerfile:1

# ---------- Stage 1: build the React app ----------
FROM node:24-alpine AS build
WORKDIR /app

# Dependencies first (cached until package*.json change)
COPY package.json package-lock.json ./
RUN npm ci

# Then the source code
COPY . .

# Vite bakes VITE_* variables into the JS at BUILD time (not at run time).
ARG VITE_API_BASE_URL=/api
ARG VITE_AGENT_API_BASE_URL=http://localhost:8001
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_AGENT_API_BASE_URL=$VITE_AGENT_API_BASE_URL

RUN npm run build

# ---------- Stage 2: serve static files with nginx ----------
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80