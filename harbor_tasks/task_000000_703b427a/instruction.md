Monitoring script at /home/user/scripts/top_ips.sh is supposed to spit out the top 10 source IPs by request count from yesterday's access logs — been running it via cron for months. Started throwing weird results last week, ops noticed the counts are way off compared to what they see in grafana. Like it's reporting maybe 1/3 of the actual traffic.

Logs live in /var/log/httpd/, one file per day, format is access_YYYYMMDD.log. Script worked fine before, nothing's changed on our end afaict. Need it actually counting all requests again.
