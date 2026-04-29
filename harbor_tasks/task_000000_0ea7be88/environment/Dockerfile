FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gawk \
    sed \
    grep \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/logs && chmod 0777 /home/user && chmod 0777 /home/user/logs

RUN cat <<'EOF' > /home/user/logs/access.log
192.168.1.45 - - [15/Jan/2024:10:23:15 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
10.0.0.12 - - [15/Jan/2024:10:23:16 +0000] "POST /api/login HTTP/1.1" 401 567 "-" "curl/7.68.0"
172.16.5.99 - - [15/Jan/2024:10:23:17 +0000] "GET /favicon.ico HTTP/1.1" 404 209 "-" "Mozilla/5.0"
192.168.0.1 - - [15/Jan/2024:10:23:18 +0000] "GET /about.html HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
10.10.10.10 - - [15/Jan/2024:10:23:19 +0000] "POST /api/data HTTP/1.1" 500 123 "-" "Python/3.9"
172.20.0.55 - - [15/Jan/2024:10:23:20 +0000] "GET /css/style.css HTTP/1.1" 200 890 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:23:21 +0000] "GET /js/app.js HTTP/1.1" 200 4567 "-" "Mozilla/5.0"
10.0.0.5 - - [15/Jan/2024:10:23:22 +0000] "DELETE /api/user/123 HTTP/1.1" 403 234 "-" "curl/7.68.0"
172.16.0.1 - - [15/Jan/2024:10:23:23 +0000] "GET /images/logo.png HTTP/1.1" 304 0 "-" "Mozilla/5.0"
192.168.2.50 - - [15/Jan/2024:10:23:24 +0000] "PUT /api/update HTTP/1.1" 201 456 "-" "Python/3.9"
10.0.1.1 - - [15/Jan/2024:10:23:25 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"
172.17.0.2 - - [15/Jan/2024:10:23:26 +0000] "GET /robots.txt HTTP/1.1" 404 123 "-" "Googlebot/2.1"
192.168.1.75 - - [15/Jan/2024:10:23:27 +0000] "POST /api/submit HTTP/1.1" 200 789 "-" "Mozilla/5.0"
10.0.0.20 - - [15/Jan/2024:10:23:28 +0000] "GET /sitemap.xml HTTP/1.1" 200 2345 "-" "Bingbot/2.0"
172.16.5.10 - - [15/Jan/2024:10:23:29 +0000] "GET /privacy.html HTTP/1.1" 200 5678 "-" "Mozilla/5.0"
192.168.0.25 - - [15/Jan/2024:10:23:30 +0000] "GET /terms.html HTTP/1.1" 200 6789 "-" "Mozilla/5.0"
10.10.0.100 - - [15/Jan/2024:10:23:31 +0000] "POST /api/auth HTTP/1.1" 401 234 "-" "curl/7.68.0"
172.20.1.1 - - [15/Jan/2024:10:23:32 +0000] "GET /blog/post-1 HTTP/1.1" 200 12345 "-" "Mozilla/5.0"
192.168.1.200 - - [15/Jan/2024:10:23:33 +0000] "GET /blog/post-2 HTTP/1.1" 200 11234 "-" "Mozilla/5.0"
10.0.0.30 - - [15/Jan/2024:10:23:34 +0000] "GET /api/health HTTP/1.1" 200 45 "-" "HealthChecker/1.0"
172.16.0.50 - - [15/Jan/2024:10:23:35 +0000] "GET /downloads/file.zip HTTP/1.1" 200 1048576 "-" "Mozilla/5.0"
192.168.2.100 - - [15/Jan/2024:10:23:36 +0000] "POST /upload HTTP/1.1" 413 567 "-" "Mozilla/5.0"
10.0.1.50 - - [15/Jan/2024:10:23:37 +0000] "GET /admin HTTP/1.1" 403 234 "-" "Mozilla/5.0"
172.17.0.10 - - [15/Jan/2024:10:23:38 +0000] "GET /dashboard HTTP/1.1" 302 0 "-" "Mozilla/5.0"
192.168.1.150 - - [15/Jan/2024:10:23:39 +0000] "GET /login HTTP/1.1" 200 3456 "-" "Mozilla/5.0"
10.0.0.40 - - [15/Jan/2024:10:23:40 +0000] "POST /login HTTP/1.1" 200 567 "-" "Mozilla/5.0"
172.16.5.25 - - [15/Jan/2024:10:23:41 +0000] "GET /logout HTTP/1.1" 302 0 "-" "Mozilla/5.0"
192.168.0.75 - - [15/Jan/2024:10:23:42 +0000] "GET /profile HTTP/1.1" 200 4567 "-" "Mozilla/5.0"
10.10.10.50 - - [15/Jan/2024:10:23:43 +0000] "PUT /profile/update HTTP/1.1" 200 234 "-" "Mozilla/5.0"
172.20.0.100 - - [15/Jan/2024:10:23:44 +0000] "GET /settings HTTP/1.1" 200 5678 "-" "Mozilla/5.0"
192.168.1.25 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 8901 "-" "curl/7.68.0"
10.0.0.60 - - [15/Jan/2024:10:23:46 +0000] "GET /api/products HTTP/1.1" 200 12345 "-" "Python/3.9"
172.16.0.75 - - [15/Jan/2024:10:23:47 +0000] "POST /api/orders HTTP/1.1" 201 567 "-" "Mozilla/5.0"
192.168.2.25 - - [15/Jan/2024:10:23:48 +0000] "GET /api/orders/456 HTTP/1.1" 200 890 "-" "Mozilla/5.0"
10.0.1.75 - - [15/Jan/2024:10:23:49 +0000] "DELETE /api/orders/789 HTTP/1.1" 204 0 "-" "curl/7.68.0"
172.17.0.25 - - [15/Jan/2024:10:23:50 +0000] "GET /search?q=test HTTP/1.1" 200 6789 "-" "Mozilla/5.0"
192.168.1.175 - - [15/Jan/2024:10:23:51 +0000] "GET /category/electronics HTTP/1.1" 200 23456 "-" "Mozilla/5.0"
10.0.0.70 - - [15/Jan/2024:10:23:52 +0000] "GET /product/12345 HTTP/1.1" 200 7890 "-" "Mozilla/5.0"
172.16.5.50 - - [15/Jan/2024:10:23:53 +0000] "POST /cart/add HTTP/1.1" 200 234 "-" "Mozilla/5.0"
192.168.0.100 - - [15/Jan/2024:10:23:54 +0000] "GET /cart HTTP/1.1" 200 4567 "-" "Mozilla/5.0"
10.10.0.25 - - [15/Jan/2024:10:23:55 +0000] "POST /checkout HTTP/1.1" 200 890 "-" "Mozilla/5.0"
172.20.1.50 - - [15/Jan/2024:10:23:56 +0000] "GET /confirmation/98765 HTTP/1.1" 200 3456 "-" "Mozilla/5.0"
192.168.1.225 - - [15/Jan/2024:10:23:57 +0000] "GET /help HTTP/1.1" 200 5678 "-" "Mozilla/5.0"
10.0.0.80 - - [15/Jan/2024:10:23:58 +0000] "GET /faq HTTP/1.1" 200 6789 "-" "Mozilla/5.0"
172.16.0.100 - - [15/Jan/2024:10:23:59 +0000] "POST /support/ticket HTTP/1.1" 201 456 "-" "Mozilla/5.0"
192.168.2.75 - - [15/Jan/2024:10:24:00 +0000] "GET /newsletter HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
10.0.1.100 - - [15/Jan/2024:10:24:01 +0000] "POST /newsletter/subscribe HTTP/1.1" 200 123 "-" "Mozilla/5.0"
172.17.0.50 - - [15/Jan/2024:10:24:02 +0000] "GET /unsubscribe HTTP/1.1" 200 234 "-" "Mozilla/5.0"
192.168.1.50 - - [15/Jan/2024:10:24:03 +0000] "GET /careers HTTP/1.1" 200 8901 "-" "Mozilla/5.0"
10.0.0.90 - - [15/Jan/2024:10:24:04 +0000] "POST /apply HTTP/1.1" 200 567 "-" "Mozilla/5.0"
EOF

RUN chmod 644 /home/user/logs/access.log

RUN useradd -m -d /home/user -s /bin/bash user

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
