#!/bin/bash
# Auto-generated solve script
set -e

cat /home/user/api_server.py
python3 /home/user/api_server.py &
sleep 1 && curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/api/users
cat > /home/user/data_pipeline.sh << 'EOF'
#!/bin/bash

OUTPUT_FILE="/home/user/pipeline_results.log"
BASE_URL="http://localhost:8765"

# Clear the output file
> "$OUTPUT_FILE"

# Function to process an endpoint
process_endpoint() {
    local endpoint="$1"
    local url="${BASE_URL}${endpoint}"
    
    # Make request and capture both response body and HTTP status code
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    echo "ENDPOINT: $endpoint" >> "$OUTPUT_FILE"
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        # Success - count items in JSON array
        count=$(echo "$body" | jq 'length')
        echo "STATUS: SUCCESS" >> "$OUTPUT_FILE"
        echo "COUNT: $count" >> "$OUTPUT_FILE"
    else
        # Error
        echo "STATUS: ERROR" >> "$OUTPUT_FILE"
        echo "ERROR_CODE: $http_code" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
}

# Process all endpoints
process_endpoint "/api/users"
process_endpoint "/api/products"
process_endpoint "/api/orders"
EOF
chmod +x /home/user/data_pipeline.sh
/home/user/data_pipeline.sh
cat > /home/user/data_pipeline.sh << 'EOF'
#!/bin/bash

OUTPUT_FILE="/home/user/pipeline_results.log"
BASE_URL="http://localhost:8765"

# Clear the output file
> "$OUTPUT_FILE"

# Function to process an endpoint
process_endpoint() {
    local endpoint="$1"
    local url="${BASE_URL}${endpoint}"
    
    # Make request and capture both response body and HTTP status code
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    echo "ENDPOINT: $endpoint" >> "$OUTPUT_FILE"
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        # Success - count items in JSON array using Python
        count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
        echo "STATUS: SUCCESS" >> "$OUTPUT_FILE"
        echo "COUNT: $count" >> "$OUTPUT_FILE"
    else
        # Error
        echo "STATUS: ERROR" >> "$OUTPUT_FILE"
        echo "ERROR_CODE: $http_code" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
}

# Process all endpoints
process_endpoint "/api/users"
process_endpoint "/api/products"
process_endpoint "/api/orders"
EOF
/home/user/data_pipeline.sh
cat /home/user/pipeline_results.log
pkill -f "python3 /home/user/api_server.py"
pgrep -f "api_server.py" || echo "Server stopped successfully"
kill -9 126 2>/dev/null; sleep 1; pgrep -f "api_server.py" || echo "Server stopped successfully"
ps aux | grep api_server
curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/api/users 2>/dev/null || echo "Server is stopped (connection refused)"
ls -la /home/user/data_pipeline.sh && echo "---" && cat /home/user/pipeline_results.log
