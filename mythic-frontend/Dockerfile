# ---------- build ----------
    FROM node:18-alpine AS build

    # 1) Объявляем build‑аргументы
    ARG VITE_CLERK_PUBLISHABLE_KEY
    ARG VITE_PUBLIC_CLERK_FRONTEND_API
    
    # 2) Пробрасываем их в ENV перед сборкой
    ENV VITE_CLERK_PUBLISHABLE_KEY=${VITE_CLERK_PUBLISHABLE_KEY}
    ENV VITE_PUBLIC_CLERK_FRONTEND_API=${VITE_PUBLIC_CLERK_FRONTEND_API}
    
    WORKDIR /app
    
    # 3) Копируем только .env.production (в нём уже наши VITE_*)
    COPY .env.production .
    
    # 4) Устанавливаем зависимости и копируем весь код
    COPY package*.json ./
    RUN npm ci
    COPY . .
    
    # 5) Собираем фронт
    RUN npm run build
    
    # ---------- runtime ----------
    FROM nginx:alpine
    COPY --from=build /app/dist /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    