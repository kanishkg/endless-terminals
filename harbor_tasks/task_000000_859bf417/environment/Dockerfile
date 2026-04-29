FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    grep \
    sed \
    gawk \
    iptables \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/firewall && chmod 0777 /home/user && chmod 0777 /home/user/firewall

RUN cat > /usr/local/bin/iptables << 'IPTABLES_WRAPPER'
#!/usr/bin/env python3
import sys
import os
import re

STATE_FILE = "/tmp/iptables_state.txt"

def load_state():
    state = {"policies": {}, "rules": []}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("POLICY:"):
                    parts = line[7:].split("=")
                    if len(parts) == 2:
                        state["policies"][parts[0]] = parts[1]
                elif line.startswith("RULE:"):
                    state["rules"].append(line[5:])
    return state

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        for chain, policy in state["policies"].items():
            f.write(f"POLICY:{chain}={policy}\n")
        for rule in state["rules"]:
            f.write(f"RULE:{rule}\n")

def parse_rule(rule_str):
    parts = rule_str.split()
    rule = {}
    i = 0
    while i < len(parts):
        if parts[i] == "-A":
            rule["chain"] = parts[i+1]
            i += 2
        elif parts[i] == "-s":
            rule["src"] = parts[i+1]
            i += 2
        elif parts[i] == "-d":
            rule["dst"] = parts[i+1]
            i += 2
        elif parts[i] == "-p":
            rule["proto"] = parts[i+1]
            i += 2
        elif parts[i] == "--dport":
            rule["dport"] = parts[i+1]
            i += 2
        elif parts[i] == "-j":
            rule["target"] = parts[i+1]
            i += 2
        elif parts[i] == "-i":
            rule["iface"] = parts[i+1]
            i += 2
        elif parts[i] == "-m":
            rule["match"] = parts[i+1]
            i += 2
        elif parts[i] == "--state":
            rule["state"] = parts[i+1]
            i += 2
        else:
            i += 1
    return rule

def ip_matches(rule_ip, packet_ip):
    if "/" in rule_ip:
        base, prefix = rule_ip.split("/")
        prefix = int(prefix)
        rule_parts = [int(x) for x in base.split(".")]
        packet_parts = [int(x) for x in packet_ip.split(".")]
        rule_int = (rule_parts[0] << 24) + (rule_parts[1] << 16) + (rule_parts[2] << 8) + rule_parts[3]
        packet_int = (packet_parts[0] << 24) + (packet_parts[1] << 16) + (packet_parts[2] << 8) + packet_parts[3]
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        return (rule_int & mask) == (packet_int & mask)
    return rule_ip == packet_ip

def check_packet(state, chain, src, dst, proto, dport, iface=None, pkt_state=None):
    for rule_str in state["rules"]:
        rule = parse_rule(rule_str)
        if rule.get("chain") != chain:
            continue
        if "src" in rule and not ip_matches(rule["src"], src):
            continue
        if "dst" in rule and not ip_matches(rule["dst"], dst):
            continue
        if "proto" in rule and rule["proto"] != proto:
            continue
        if "dport" in rule:
            if "proto" not in rule:
                continue
            if rule["dport"] != str(dport):
                continue
        if "iface" in rule and iface and rule["iface"] != iface:
            continue
        if "state" in rule:
            if pkt_state and pkt_state in rule["state"].split(","):
                return rule.get("target", "ACCEPT")
            continue
        return rule.get("target", "ACCEPT")
    return state["policies"].get(chain, "ACCEPT")

def main():
    args = sys.argv[1:]
    if not args:
        print("iptables wrapper")
        sys.exit(0)

    if args[0] == "-F":
        if os.path.exists(STATE_FILE):
            state = load_state()
            state["rules"] = []
            save_state(state)
        sys.exit(0)

    if args[0] == "-X":
        sys.exit(0)

    if args[0] == "-P":
        if len(args) >= 3:
            state = load_state()
            state["policies"][args[1]] = args[2]
            save_state(state)
        sys.exit(0)

    if args[0] == "-A":
        rule_str = " ".join(args)
        if "--dport" in rule_str and "-p tcp" not in rule_str and "-p udp" not in rule_str:
            sys.stderr.write("Warning: --dport used without -p tcp/udp, rule will never match\n")
        state = load_state()
        state["rules"].append(rule_str)
        save_state(state)
        sys.exit(0)

    if args[0] == "-C":
        state = load_state()
        chain = None
        src = "0.0.0.0"
        dst = "0.0.0.0"
        proto = "tcp"
        dport = 0
        iface = None
        i = 1
        while i < len(args):
            if args[i] == "-s" and i+1 < len(args):
                src = args[i+1]
                i += 2
            elif args[i] == "-d" and i+1 < len(args):
                dst = args[i+1]
                i += 2
            elif args[i] == "-p" and i+1 < len(args):
                proto = args[i+1]
                i += 2
            elif args[i] == "--dport" and i+1 < len(args):
                dport = args[i+1]
                i += 2
            elif args[i] == "-i" and i+1 < len(args):
                iface = args[i+1]
                i += 2
            elif i == 1:
                chain = args[i]
                i += 1
            else:
                i += 1

        if chain is None:
            chain = "INPUT"

        result = check_packet(state, chain, src, dst, proto, dport, iface)
        if result == "ACCEPT":
            sys.exit(0)
        else:
            sys.exit(1)

    if args[0] == "-L":
        state = load_state()
        print("Policies:")
        for chain, policy in state["policies"].items():
            print(f"  {chain}: {policy}")
        print("Rules:")
        for rule in state["rules"]:
            print(f"  {rule}")
        sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
IPTABLES_WRAPPER

RUN chmod 755 /usr/local/bin/iptables

RUN cat > /home/user/firewall/rules.sh << 'RULESEOF'
#!/bin/bash
iptables -F
iptables -X
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Block all input first for security
iptables -A INPUT -j DROP

# Allow frontend to API
iptables -A OUTPUT -s 10.0.1.10 -d 10.0.1.20 --dport 8080 -j ACCEPT

# Allow API to postgres  
iptables -A INPUT -s 10.0.1.20 -d 10.0.1.130 --dport 5432 -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow localhost
iptables -A INPUT -i lo -j ACCEPT
RULESEOF

RUN chmod 755 /home/user/firewall/rules.sh

RUN cat > /home/user/firewall/test_frontend_to_api.sh << 'TESTFEEOF'
#!/bin/bash
# Test if frontend (10.0.1.10) can reach API (10.0.1.20:8080)
iptables -C INPUT -s 10.0.1.10 -d 10.0.1.20 -p tcp --dport 8080
exit $?
TESTFEEOF

RUN chmod 755 /home/user/firewall/test_frontend_to_api.sh

RUN cat > /home/user/firewall/test_api_to_postgres.sh << 'TESTPGEOF'
#!/bin/bash
# Test if API (10.0.1.20) can reach Postgres (10.0.1.30:5432)
iptables -C INPUT -s 10.0.1.20 -d 10.0.1.30 -p tcp --dport 5432
exit $?
TESTPGEOF

RUN chmod 755 /home/user/firewall/test_api_to_postgres.sh

RUN cat > /home/user/firewall/test_all.sh << 'TESTALLEOF'
#!/bin/bash
echo "Testing frontend to API connectivity..."
bash /home/user/firewall/test_frontend_to_api.sh
RESULT1=$?
if [ $RESULT1 -eq 0 ]; then
    echo "  PASS: Frontend can reach API on port 8080"
else
    echo "  FAIL: Frontend cannot reach API on port 8080"
fi

echo "Testing API to Postgres connectivity..."
bash /home/user/firewall/test_api_to_postgres.sh
RESULT2=$?
if [ $RESULT2 -eq 0 ]; then
    echo "  PASS: API can reach Postgres on port 5432"
else
    echo "  FAIL: API cannot reach Postgres on port 5432"
fi

echo ""
if [ $RESULT1 -eq 0 ] && [ $RESULT2 -eq 0 ]; then
    echo "All tests PASSED"
    exit 0
else
    echo "Some tests FAILED"
    exit 1
fi
TESTALLEOF

RUN chmod 755 /home/user/firewall/test_all.sh

RUN chown -R 1000:1000 /home/user/firewall

RUN touch /tmp/iptables_state.txt && chmod 666 /tmp/iptables_state.txt

WORKDIR /home/user

USER 1000

CMD ["/bin/bash"]
