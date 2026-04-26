FROM nginx:alpine

ARG CARD_NUMBER="8600 0000 0000 0000"
ARG CARD_HOLDER="Support MyDict"

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY favicon.png /usr/share/nginx/html/favicon.png

# Inject card info from build args into the HTML
RUN sed -i "s|__CARD_NUMBER__|${CARD_NUMBER}|g" /usr/share/nginx/html/index.html && \
    sed -i "s|__CARD_HOLDER__|${CARD_HOLDER}|g" /usr/share/nginx/html/index.html

EXPOSE 80
