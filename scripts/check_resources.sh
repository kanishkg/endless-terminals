#!/usr/bin/env bash

# Gather raw values
mem_avail=$(free -h | awk '/^Mem:/{print $7}')
mem_total=$(free -h | awk '/^Mem:/{print $2}')

load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
ncores=$(nproc)
load_pct=$(awk "BEGIN {printf \"%d\", ($load/$ncores)*100}")

disk_free=$(df -h / | awk 'NR==2{print $4}')
disk_pct=$(df / | awk 'NR==2{print $5}')

docker_images=$(docker system df 2>/dev/null | awk '/^Images/{print $4}')
docker_containers=$(docker system df 2>/dev/null | awk '/^Containers/{print $2}')
docker_cache=$(docker system df 2>/dev/null | awk '/^Build Cache/{print $4}')

# Format status strings
ram_status="${mem_avail} available of ${mem_total}"
cpu_status="${load} / ${ncores} cores (~${load_pct}%)"
disk_status="${disk_free} free (${disk_pct} used)"
docker_status="${docker_images} images, ${docker_containers} containers, ${docker_cache} build cache"

# Table rendering
COL1=10
COL2=49

print_row() {
    local label="$1"
    local value="$2"
    local max=$COL2
    local first=true
    while [ ${#value} -gt 0 ]; do
        chunk="${value:0:$max}"
        value="${value:$max}"
        if $first; then
            printf "│ %-${COL1}s│ %-${COL2}s│\n" "$label" "$chunk"
            first=false
        else
            printf "│ %-${COL1}s│ %-${COL2}s│\n" "" "$chunk"
        fi
    done
}

print_divider() {
    printf "├──────────┼─────────────────────────────────────────────────┤\n"
}

printf "┌──────────┬─────────────────────────────────────────────────┐\n"
printf "│ %-${COL1}s│ %-${COL2}s│\n" "Resource" "Status"
print_divider
print_row "RAM"      "$ram_status"
print_divider
print_row "CPU load" "$cpu_status"
print_divider
print_row "Disk"     "$disk_status"
print_divider
print_row "Docker"   "$docker_status"
print_divider
while IFS= read -r line; do
    job=$(echo "$line" | grep -oP '\-\-job-name \K\S+')
    pid=$(echo "$line" | awk '{print $1}')
    cpu=$(echo "$line" | awk '{print $2}')
    [ -n "$job" ] && print_row "Harbor" "PID $pid | ${cpu}% CPU | $job"
done < <(ps aux | grep "harbor run" | grep -v "grep\|bash")
printf "└──────────┴─────────────────────────────────────────────────┘\n"
