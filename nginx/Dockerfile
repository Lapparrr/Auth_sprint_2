FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY site.conf /etc/nginx/conf.d/site.conf
COPY ssl.key /home/ssl.key
COPY ssl.pem /home/ssl.pem

RUN openssl req -x509 -newkey rsa:4096 -keyout /home/ssl.key -out /home/ssl.pem -days 10000 -nodes -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=examplebrooklyn.com"
