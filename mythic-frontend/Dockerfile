# ---------- build ----------
    FROM node:18-alpine AS build

    ARG VITE_API_BASE_URL
    ARG VITE_CLERK_PUBLISHABLE_KEY
    
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci
    COPY . .
    
    ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
    ENV VITE_CLERK_PUBLISHABLE_KEY=${VITE_CLERK_PUBLISHABLE_KEY}
    
    RUN npm run build
    
    # ---------- runtime ----------
    FROM nginx:alpine
    COPY --from=build /app/dist /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    