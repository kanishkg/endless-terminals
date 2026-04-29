FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    diffutils \
    patch \
    dos2unix \
    python3 \
    python3-pip \
    rcs \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/workflow && chmod 0777 /home/user && chmod 0777 /home/user/workflow

RUN python3 << 'PYEOF'
import os

workflow_dir = "/home/user/workflow"

# Base file content - 80 lines, 5 sections with ~16 lines each
# Lines 1-40 use LF, lines 41-80 use CRLF (the trap)

base_lines = []

# [database] section - lines 1-16
base_lines.append("[database]")
base_lines.append("db_host=localhost")
base_lines.append("db_port=5432")
base_lines.append("db_name=myapp")
base_lines.append("db_user=admin")
base_lines.append("db_password=secret123")
base_lines.append("db_pool_size=10")
base_lines.append("db_timeout=30")
base_lines.append("db_ssl=true")
base_lines.append("db_charset=utf8")
base_lines.append("db_collation=utf8_general_ci")
base_lines.append("db_max_connections=100")
base_lines.append("db_retry_attempts=3")
base_lines.append("db_retry_delay=1000")
base_lines.append("db_log_queries=false")
base_lines.append("db_debug=false")

# [cache] section - lines 17-32
base_lines.append("[cache]")
base_lines.append("cache_enabled=true")
base_lines.append("cache_ttl=300")
base_lines.append("cache_backend=memcached")
base_lines.append("cache_prefix=app_")
base_lines.append("cache_host=127.0.0.1")
base_lines.append("cache_port=11211")
base_lines.append("cache_max_size=256mb")
base_lines.append("cache_eviction=lru")
base_lines.append("cache_compression=true")
base_lines.append("cache_serializer=json")
base_lines.append("cache_namespace=default")
base_lines.append("cache_stats=true")
base_lines.append("cache_warmup=false")
base_lines.append("cache_distributed=false")
base_lines.append("cache_sync_interval=60")

# [logging] section - lines 33-48
base_lines.append("[logging]")
base_lines.append("log_enabled=true")
base_lines.append("log_level=info")
base_lines.append("log_file=/var/log/app.log")
base_lines.append("log_max_size=100mb")
base_lines.append("log_rotate=daily")
base_lines.append("log_keep=7")
base_lines.append("log_format=json")

# Line 41 onwards will have CRLF - continuing [logging]
base_lines.append("log_timestamp=true")
base_lines.append("log_caller=false")
base_lines.append("log_stacktrace=true")
base_lines.append("log_color=false")
base_lines.append("log_async=true")
base_lines.append("log_buffer_size=1000")
base_lines.append("log_flush_interval=5")
base_lines.append("log_syslog=false")

# [auth] section - lines 49-64
base_lines.append("[auth]")
base_lines.append("auth_enabled=true")
base_lines.append("auth_provider=local")
base_lines.append("auth_session_ttl=3600")
base_lines.append("auth_timeout=30")
base_lines.append("auth_max_attempts=5")
base_lines.append("auth_lockout_duration=300")
base_lines.append("auth_password_min_length=8")
base_lines.append("auth_require_uppercase=true")
base_lines.append("auth_require_numbers=true")
base_lines.append("auth_require_special=false")
base_lines.append("auth_mfa_enabled=false")
base_lines.append("auth_jwt_secret=supersecretkey")
base_lines.append("auth_jwt_expiry=86400")
base_lines.append("auth_refresh_token=true")
base_lines.append("auth_cookie_secure=true")

# [features] section - lines 65-80
base_lines.append("[features]")
base_lines.append("feature_signup=true")
base_lines.append("feature_oauth=true")
base_lines.append("feature_api=true")
base_lines.append("feature_webhooks=false")
base_lines.append("feature_notifications=true")
base_lines.append("feature_analytics=true")
base_lines.append("feature_reports=false")
base_lines.append("feature_import=true")
base_lines.append("feature_bulk_ops=false")
base_lines.append("feature_audit_log=true")
base_lines.append("feature_rate_limit=true")
base_lines.append("feature_maintenance=false")
base_lines.append("feature_beta=false")
base_lines.append("feature_experimental=false")
base_lines.append("feature_legacy_api=true")

# Write base.txt with mixed line endings
# Lines 1-40 (index 0-39) use LF, lines 41-80 (index 40-79) use CRLF
with open(os.path.join(workflow_dir, "base.txt"), "wb") as f:
    for i, line in enumerate(base_lines):
        if i < 40:
            f.write((line + "\n").encode('utf-8'))
        else:
            f.write((line + "\r\n").encode('utf-8'))

# theirs.txt - normalized to LF, with cache changes and feature additions
theirs_lines = base_lines.copy()

# Find and modify cache section values
for i, line in enumerate(theirs_lines):
    if line == "cache_ttl=300":
        theirs_lines[i] = "cache_ttl=3600"
    elif line == "cache_backend=memcached":
        theirs_lines[i] = "cache_backend=redis"
    elif line == "cache_prefix=app_":
        theirs_lines[i] = "cache_prefix=v2_"

# Add feature additions at end (before the last line of features section)
# Find the last feature line and add after it
theirs_lines.append("feature_dark_mode=true")
theirs_lines.append("feature_export=csv,json")

# Write theirs.txt with all LF line endings
with open(os.path.join(workflow_dir, "theirs.txt"), "wb") as f:
    for line in theirs_lines:
        f.write((line + "\n").encode('utf-8'))

# ours.txt - preserves mixed line endings, with logging changes and auth deletion
ours_lines = base_lines.copy()

# Find and modify logging section values
for i, line in enumerate(ours_lines):
    if line == "log_level=info":
        ours_lines[i] = "log_level=debug"
    elif line == "log_rotate=daily":
        ours_lines[i] = "log_rotate=weekly"

# Remove auth_timeout line
ours_lines = [line for line in ours_lines if line != "auth_timeout=30"]

# Write ours.txt with same mixed line endings as base
# But now we have 79 lines, need to figure out the cutoff
# Original lines 1-40 had LF, 41-80 had CRLF
# After removing auth_timeout (which was at original index 52), 
# we need to preserve the pattern based on original positions
with open(os.path.join(workflow_dir, "ours.txt"), "wb") as f:
    original_index = 0
    for line in ours_lines:
        # Track original position to determine line ending
        # auth_timeout was at index 52 in base_lines
        if line == "auth_timeout=30":
            original_index += 1
            continue

        if original_index < 40:
            f.write((line + "\n").encode('utf-8'))
        else:
            f.write((line + "\r\n").encode('utf-8'))
        original_index += 1
PYEOF

RUN chmod 0666 /home/user/workflow/base.txt /home/user/workflow/theirs.txt /home/user/workflow/ours.txt
