FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    tar \
    gzip \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /tmp/metrics-export/prometheus \
    && mkdir -p /tmp/metrics-export/grafana/dashboards \
    && mkdir -p /tmp/metrics-export/alertmanager

RUN echo "groups:" > /tmp/metrics-export/prometheus/rules.yml \
    && echo "  - name: example" >> /tmp/metrics-export/prometheus/rules.yml \
    && echo "    rules:" >> /tmp/metrics-export/prometheus/rules.yml \
    && echo "      - alert: HighMemoryUsage" >> /tmp/metrics-export/prometheus/rules.yml \
    && echo "        expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.1" >> /tmp/metrics-export/prometheus/rules.yml

RUN echo "global:" > /tmp/metrics-export/prometheus/prometheus.yml \
    && echo "  scrape_interval: 15s" >> /tmp/metrics-export/prometheus/prometheus.yml \
    && echo "scrape_configs:" >> /tmp/metrics-export/prometheus/prometheus.yml \
    && echo "  - job_name: 'prometheus'" >> /tmp/metrics-export/prometheus/prometheus.yml \
    && echo "    static_configs:" >> /tmp/metrics-export/prometheus/prometheus.yml \
    && echo "      - targets: ['localhost:9090']" >> /tmp/metrics-export/prometheus/prometheus.yml

RUN echo '{"dashboard": {"id": null, "title": "System Overview", "panels": [{"id": 1, "type": "graph", "title": "CPU Usage"}], "version": 1}}' > /tmp/metrics-export/grafana/dashboards/system-overview.json

RUN echo '{"dashboard": {"id": null, "title": "Network Traffic", "panels": [{"id": 1, "type": "graph", "title": "Bytes In/Out"}], "version": 1}}' > /tmp/metrics-export/grafana/dashboards/network-traffic.json

RUN echo '{"dashboard": {"id": null, "title": "App Latency", "panels": [{"id": 1, "type": "graph", "title": "Request Latency"}], "version": 1}}' > /tmp/metrics-export/grafana/dashboards/app-latency.json

RUN echo "[server]" > /tmp/metrics-export/grafana/grafana.ini \
    && echo "http_port = 3000" >> /tmp/metrics-export/grafana/grafana.ini \
    && echo "[security]" >> /tmp/metrics-export/grafana/grafana.ini \
    && echo "admin_user = admin" >> /tmp/metrics-export/grafana/grafana.ini

RUN echo "global:" > /tmp/metrics-export/alertmanager/alertmanager.yml \
    && echo "  resolve_timeout: 5m" >> /tmp/metrics-export/alertmanager/alertmanager.yml \
    && echo "route:" >> /tmp/metrics-export/alertmanager/alertmanager.yml \
    && echo "  receiver: 'default'" >> /tmp/metrics-export/alertmanager/alertmanager.yml \
    && echo "receivers:" >> /tmp/metrics-export/alertmanager/alertmanager.yml \
    && echo "  - name: 'default'" >> /tmp/metrics-export/alertmanager/alertmanager.yml

RUN cd /tmp && tar -czvf /home/user/metrics-export.tar.gz metrics-export/

RUN chmod 644 /home/user/metrics-export.tar.gz

RUN rm -rf /tmp/metrics-export

WORKDIR /home/user

CMD ["/bin/bash"]
