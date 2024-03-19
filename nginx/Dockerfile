FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p /var/cache/nginx

COPY nginx.conf /etc/nginx/conf.d
