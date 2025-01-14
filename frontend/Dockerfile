# Этап 1: Сборка React приложения
FROM node:20-alpine AS build

WORKDIR /app

# Устанавливаем зависимости
COPY package*.json ./

RUN npm install --frozen-lockfile

# Копируем исходный код и собираем приложение
COPY . .
RUN npm run build

# Этап 2: Настройка Nginx
FROM nginx:stable-alpine

# Копируем собранное приложение
COPY --from=build /app/build /usr/share/nginx/html

# Копируем файл конфигурации Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
