FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the ci-pipelines directory
RUN mkdir -p /home/user/ci-pipelines && chmod 0777 /home/user/ci-pipelines

# Create Jenkinsfile
RUN cat <<EOF > /home/user/ci-pipelines/Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
}
EOF

# Create .gitlab-ci.yml
RUN cat <<EOF > /home/user/ci-pipelines/.gitlab-ci.yml
stages:
  - build
  - test
build_job:
  stage: build
  script:
    - echo "Building"
EOF

# Create azure-pipelines.yml
RUN cat <<EOF > /home/user/ci-pipelines/azure-pipelines.yml
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
steps:
  - script: echo Hello
EOF

# Set proper permissions on all created files
RUN chmod 0666 /home/user/ci-pipelines/Jenkinsfile && \
    chmod 0666 /home/user/ci-pipelines/.gitlab-ci.yml && \
    chmod 0666 /home/user/ci-pipelines/azure-pipelines.yml

# Set working directory
WORKDIR /home/user
