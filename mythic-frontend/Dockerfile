# Этап сборки
FROM node:18-alpine AS builder

WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package*.json ./

RUN npm ci && npm install --save-dev @types/node

COPY . .

# Убедимся, что есть файл типов
RUN if [ ! -f src/vite-env.d.ts ]; then \
    echo '/// <reference types="vite/client" />' > src/vite-env.d.ts && \
    echo 'interface ImportMetaEnv {' >> src/vite-env.d.ts && \
    echo '  readonly VITE_CLERK_PUBLISHABLE_KEY: string;' >> src/vite-env.d.ts && \
    echo '  readonly VITE_API_BASE_URL: string;' >> src/vite-env.d.ts && \
    echo '}' >> src/vite-env.d.ts && \
    echo 'interface ImportMeta {' >> src/vite-env.d.ts && \
    echo '  readonly env: ImportMetaEnv;' >> src/vite-env.d.ts && \
    echo '}' >> src/vite-env.d.ts; \
    fi

# *** ВАЖНО ***
# Добавляем аргументы сборки
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_API_BASE_URL

# Добавляем их в ENV
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Теперь билдим с этими переменными
RUN npm run build

# Этап production
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
