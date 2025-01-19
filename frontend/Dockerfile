# Этап 1: Сборка React приложения
FROM node:20-alpine AS build

WORKDIR /app

# Копируем только package.json и package-lock.json для кэширования зависимостей
COPY package*.json ./

# Устанавливаем зависимости с флагом для игнорирования проблем с зависимостями
RUN npm install --legacy-peer-deps --frozen-lockfile

# Копируем только измененные файлы после установки зависимостей
COPY . .

# Сборка React приложения
RUN npm run build

# Этап 2: Настройка Nginx
FROM nginx:stable-alpine

# Копируем собранное приложение из первого этапа
COPY --from=build /app/build /usr/share/nginx/html

# Копируем файл конфигурации Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
