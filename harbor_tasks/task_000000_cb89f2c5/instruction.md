I'm a Kubernetes operator and I need help analyzing our manifest files to understand which resource types we're deploying most frequently across our cluster configurations.

I have a directory at /home/user/k8s-manifests containing multiple YAML manifest files for different environments (dev, staging, prod). Each file contains one or more Kubernetes resource definitions with a "kind:" field specifying the resource type (like Deployment, Service, ConfigMap, Secret, etc.).

Please help me with the following:

1. First, extract all the "kind:" values from every YAML file in /home/user/k8s-manifests and its subdirectories. The kind field appears at the start of a line followed by a colon and space, like "kind: Deployment" or "kind: Service".

2. Count how many times each resource type (the value after "kind: ") appears across all manifest files.

3. Sort the results by frequency in descending order (most common first). If two resource types have the same count, sort them alphabetically.

4. Write the final report to /home/user/k8s-manifests/resource-frequency-report.txt

The output format in the report file must be exactly:
- One line per resource type
- Each line formatted as: COUNT RESOURCETYPE (a number, single space, then the resource type name)
- Sorted by count descending, then alphabetically for ties
- No leading spaces, no trailing spaces on lines
- No empty lines in the output

For example, if there were 5 Deployments and 3 Services, the output would look like:
5 Deployment
3 Service

This will help me understand our resource distribution and plan our operator development priorities.
