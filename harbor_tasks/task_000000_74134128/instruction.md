Our synthetic-monitoring stack runs health checks every 5 minutes from /home/user/monitor/check_uptime.py — it hits three internal services, logs timestamps, and fires an alert if any service was down for more than 15 minutes in the past hour. Problem is, we're getting phantom alerts at exactly 2am and 3am every day, claiming services were down for 60+ minutes when they definitely weren't. Logs look fine, services never actually went offline.

Started happening after we migrated the monitoring box to a new VM last month. Old box was configured identically afaict. The script itself hasn't changed in ages and worked fine before. I'm guessing something with the new VM's tz setup but I checked and /etc/timezone says America/New_York which is correct.

Need this to stop crying wolf every night — real alerts only.
