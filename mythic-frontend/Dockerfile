# ---------- build ----------
    FROM node:18-alpine AS build

    # оставляем ТОЛЬКО ключ Clerk
    ARG  VITE_CLERK_PUBLISHABLE_KEY
    WORKDIR /app
    
    COPY package*.json ./
    COPY .env.production . 
    RUN npm ci
    
    COPY . .
    
    # пробрасываем внутрь процесса Viteтолько Clerk-ключ
    ENV  VITE_CLERK_PUBLISHABLE_KEY=${VITE_CLERK_PUBLISHABLE_KEY}
    
    RUN npm run build        # vite build
    
    # ---------- runtime ----------
    FROM nginx:alpine
    COPY --from=build /app/dist /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    