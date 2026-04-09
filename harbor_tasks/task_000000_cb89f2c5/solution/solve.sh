#!/bin/bash
# Auto-generated solve script
set -e

find /home/user/k8s-manifests -type f -name "*.yaml" -o -name "*.yml" | head -20
grep -rh "^kind:" /home/user/k8s-manifests --include="*.yaml" --include="*.yml"
grep -rh "^kind:" /home/user/k8s-manifests --include="*.yaml" --include="*.yml" | sed 's/^kind: //' | sort | uniq -c | sort -k1,1rn -k2,2
grep -rh "^kind:" /home/user/k8s-manifests --include="*.yaml" --include="*.yml" | sed 's/^kind: //' | sort | uniq -c | sort -k1,1rn -k2,2 | awk '{print $1, $2}' > /home/user/k8s-manifests/resource-frequency-report.txt
cat /home/user/k8s-manifests/resource-frequency-report.txt
cat -A /home/user/k8s-manifests/resource-frequency-report.txt
