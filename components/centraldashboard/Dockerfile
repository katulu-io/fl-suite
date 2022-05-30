FROM nginx:stable-alpine
LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY dist /usr/share/nginx/html
