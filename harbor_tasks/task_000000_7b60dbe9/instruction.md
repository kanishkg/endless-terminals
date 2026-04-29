Building a unified health-check dashboard — /home/user/monitor/check_all.py should poll three internal services (inventory on 8081, pricing on 8082, fulfillment on 8083) and write a json report to /home/user/monitor/status.json with each service's state and an overall "healthy" boolean.

Problem is it's reporting everything degraded even though curling each service individually returns 200 with `{"status":"ok"}`. The script runs, no exceptions, just wrong output. Thought maybe it was a timeout thing so I bumped the request timeout to 30s, same deal. All three show degraded in the report, overall shows false.

Services are up right now if you want to poke them. Need the report accurate — if they're actually healthy it should say so.
