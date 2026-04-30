FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    make \
    pandoc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/docs/src /home/user/docs/build

RUN cat <<'EOF' > /home/user/docs/src/intro.md
# Introduction

Welcome to our documentation. This guide will help you get started.

## Overview

This project provides the following features:

- Easy to use interface
- Comprehensive documentation
- Active community support

Here is some introductory text that explains the basics of our system.
EOF

RUN cat <<'EOF' > /home/user/docs/src/guide.md
# User Guide

This guide covers the main functionality of the application.

## Getting Started

Follow these steps to begin:

1. Install the software
2. Configure your settings
3. Run the application

## Configuration

You can configure the application using the config file.

### Basic Settings

- Set your username
- Choose your preferred theme
- Enable notifications
EOF

RUN cat <<'EOF' > /home/user/docs/src/reference.md
# API Reference

This document provides the complete API reference.

## Functions

### initialize()

Initializes the system with default parameters.

### process(data)

Processes the input data and returns results.

## Constants

The following constants are available:

- MAX_SIZE: Maximum allowed size
- DEFAULT_TIMEOUT: Default timeout value
- VERSION: Current version string
EOF

RUN chmod -R 0777 /home/user
