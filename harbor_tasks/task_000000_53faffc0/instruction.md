I'm testing a simple API integration and need to create a data pipeline that fetches data from a local mock API endpoint, handles potential errors gracefully, and saves the results to a file.

Here's what I need you to do:

1. First, there's a mock API server script at `/home/user/api_server.py` that I've prepared. Start this server in the background - it runs on port 8765.

2. The API has three endpoints:
   - `GET /api/users` - returns a JSON list of users
   - `GET /api/products` - returns a JSON list of products  
   - `GET /api/orders` - this endpoint is intentionally broken and returns a 500 error

3. Create a shell script at `/home/user/data_pipeline.sh` that:
   - Makes requests to all three endpoints
   - For each successful request, extracts and saves the data
   - For failed requests, logs the error but continues processing other endpoints
   - The script should be executable

4. Run your pipeline script and generate a results file at `/home/user/pipeline_results.log` with the following exact format:
   ```
   ENDPOINT: /api/users
   STATUS: SUCCESS
   COUNT: <number of items received>
   
   ENDPOINT: /api/products
   STATUS: SUCCESS
   COUNT: <number of items received>
   
   ENDPOINT: /api/orders
   STATUS: ERROR
   ERROR_CODE: <http status code>
   ```

   Each endpoint section should be separated by a blank line. The COUNT field should show the actual number of items in the JSON array returned. The ERROR_CODE should be the HTTP status code received (500 in this case).

5. After running the pipeline, stop the background API server process.

The mock API server is already set up and ready to use. Just start it and run your pipeline against it.
