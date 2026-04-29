FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

RUN pip3 install pytest jsonschema==4.20.0

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/validator/schemas \
    && mkdir -p /home/user/validator/testdata \
    && mkdir -p /home/user/validator/cache

RUN cat << 'EOF' > /home/user/validator/validate.py
#!/usr/bin/env python3
"""
JSON Schema Validator with preprocessing via jq.
Validates JSON documents against JSON schemas.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import hashlib

import jsonschema
from jsonschema import Draft7Validator


SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), 'schemas')
TESTDATA_DIR = os.path.join(os.path.dirname(__file__), 'testdata')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')


def preprocess_schema(schema_path):
    """
    Preprocess schema using jq to expand $shortref to $ref.
    This handles our team's non-standard schema extensions.
    """
    # jq filter to expand $shortref to proper $ref format
    jq_filter = 'walk(if type == "object" and has("$shortref") then . + {"$ref": .["$shortref"]} | del(.["$shortref"]) else . end)'

    result = subprocess.run(
        ['jq', jq_filter, schema_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"jq preprocessing failed for {schema_path}: {result.stderr}")

    return json.loads(result.stdout)


def get_schema_hash(schema_path):
    """Compute hash of schema file for caching."""
    with open(schema_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_cached_schema(schema_path):
    """
    Try to get preprocessed schema from cache.
    This was an optimization attempt that didn't help.
    """
    schema_hash = get_schema_hash(schema_path)
    cache_file = os.path.join(CACHE_DIR, f"{schema_hash}.json")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)

    # Preprocess and cache
    schema = preprocess_schema(schema_path)
    with open(cache_file, 'w') as f:
        json.dump(schema, f)

    return schema


def validate_document(doc, schema_path):
    """
    Validate a document against a schema.

    # TODO: look into validator caching
    """
    # Load and preprocess schema
    schema = preprocess_schema(schema_path)

    # Create validator - this compiles the schema
    validator = Draft7Validator(schema)

    # Validate
    errors = list(validator.iter_errors(doc))
    return len(errors) == 0, errors


def get_schema_for_document(doc_filename):
    """
    Determine which schema to use for a document.
    Document naming convention: doc_NNN_SCHEMANAME.json
    """
    # Extract schema name from filename
    parts = doc_filename.replace('.json', '').split('_')
    if len(parts) >= 3:
        schema_name = parts[2]
        schema_path = os.path.join(SCHEMAS_DIR, f"{schema_name}.json")
        if os.path.exists(schema_path):
            return schema_path

    # Fallback to first schema
    schemas = sorted([f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.json')])
    if schemas:
        return os.path.join(SCHEMAS_DIR, schemas[0])

    raise RuntimeError("No schemas found")


def run_benchmark():
    """
    Run the benchmark suite - validate all documents in testdata/.
    """
    print("Starting benchmark...")

    # Get all test documents
    test_files = sorted([f for f in os.listdir(TESTDATA_DIR) if f.endswith('.json')])

    if not test_files:
        print("No test files found!")
        return

    print(f"Found {len(test_files)} test documents")

    start_time = time.time()
    validated = 0
    errors_found = 0

    for doc_file in test_files:
        doc_path = os.path.join(TESTDATA_DIR, doc_file)
        schema_path = get_schema_for_document(doc_file)

        with open(doc_path, 'r') as f:
            doc = json.load(f)

        valid, errors = validate_document(doc, schema_path)
        validated += 1

        if not valid:
            errors_found += 1

    end_time = time.time()
    elapsed = end_time - start_time
    throughput = validated / elapsed if elapsed > 0 else 0

    print(f"Validated {validated} documents in {elapsed:.2f}s ({throughput:.1f} docs/sec)")

    if errors_found > 0:
        print(f"Warning: {errors_found} documents had validation errors")


def main():
    parser = argparse.ArgumentParser(description='JSON Schema Validator')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark suite')
    parser.add_argument('--document', '-d', help='Document to validate')
    parser.add_argument('--schema', '-s', help='Schema to validate against')

    args = parser.parse_args()

    if args.benchmark:
        run_benchmark()
    elif args.document and args.schema:
        with open(args.document, 'r') as f:
            doc = json.load(f)
        valid, errors = validate_document(doc, args.schema)
        if valid:
            print("Document is valid")
        else:
            print("Document is invalid:")
            for err in errors:
                print(f"  - {err.message}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
EOF

RUN chmod 755 /home/user/validator/validate.py

RUN python3 << 'PYSCRIPT'
import json
import os
import random

SCHEMAS_DIR = "/home/user/validator/schemas"
TESTDATA_DIR = "/home/user/validator/testdata"

# Schema templates with $shortref (non-standard extension that jq expands)
schema_templates = [
    {
        "name": "schemaA",
        "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
                "active": {"type": "boolean"}
            },
            "required": ["id", "name"]
        }
    },
    {
        "name": "schemaB",
        "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "userId": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "productId": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 1}
                        },
                        "required": ["productId", "quantity"]
                    }
                },
                "total": {"type": "number"}
            },
            "required": ["userId", "items"]
        }
    },
    {
        "name": "schemaC",
        "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "allOf": [
                {
                    "properties": {
                        "timestamp": {"type": "string"},
                        "level": {"type": "string", "enum": ["debug", "info", "warn", "error"]}
                    },
                    "required": ["timestamp", "level"]
                },
                {
                    "properties": {
                        "message": {"type": "string"},
                        "context": {"type": "object"}
                    }
                }
            ]
        }
    },
    {
        "name": "schemaD",
        "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "anyOf": [
                {
                    "properties": {
                        "type": {"const": "user"},
                        "username": {"type": "string"}
                    },
                    "required": ["type", "username"]
                },
                {
                    "properties": {
                        "type": {"const": "service"},
                        "serviceId": {"type": "string"}
                    },
                    "required": ["type", "serviceId"]
                }
            ]
        }
    },
    {
        "name": "schemaE",
        "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "definitions": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "country": {"type": "string"}
                    }
                }
            },
            "properties": {
                "name": {"type": "string"},
                "billingAddress": {"$shortref": "#/definitions/address"},
                "shippingAddress": {"$shortref": "#/definitions/address"}
            }
        }
    }
]

# Generate 50 schemas (5 main ones + 45 variations)
for i, tmpl in enumerate(schema_templates):
    schema_path = os.path.join(SCHEMAS_DIR, f"{tmpl['name']}.json")
    with open(schema_path, 'w') as f:
        json.dump(tmpl['schema'], f, indent=2)

# Generate additional schemas as variations
for i in range(45):
    base = schema_templates[i % 5]['schema'].copy()
    base['title'] = f"Schema variation {i}"
    base['description'] = f"Auto-generated schema variation number {i} for testing purposes"
    schema_path = os.path.join(SCHEMAS_DIR, f"schema_{i:03d}.json")
    with open(schema_path, 'w') as f:
        json.dump(base, f, indent=2)

# Generate 200 test documents that match the 5 main schemas (round-robin)
schema_names = ['schemaA', 'schemaB', 'schemaC', 'schemaD', 'schemaE']

test_docs = {
    'schemaA': lambda i: {
        "id": i,
        "name": f"User {i}",
        "email": f"user{i}@example.com",
        "active": i % 2 == 0
    },
    'schemaB': lambda i: {
        "userId": i,
        "items": [
            {"productId": f"PROD-{j}", "quantity": j + 1}
            for j in range(random.randint(1, 5))
        ],
        "total": random.uniform(10, 1000)
    },
    'schemaC': lambda i: {
        "timestamp": f"2024-01-{(i % 28) + 1:02d}T12:00:00Z",
        "level": ["debug", "info", "warn", "error"][i % 4],
        "message": f"Log message number {i}",
        "context": {"requestId": f"req-{i}"}
    },
    'schemaD': lambda i: {
        "type": "user" if i % 2 == 0 else "service",
        "username": f"user{i}" if i % 2 == 0 else None,
        "serviceId": None if i % 2 == 0 else f"svc-{i}"
    },
    'schemaE': lambda i: {
        "name": f"Customer {i}",
        "billingAddress": {
            "street": f"{i} Main St",
            "city": "Anytown",
            "country": "USA"
        },
        "shippingAddress": {
            "street": f"{i} Oak Ave",
            "city": "Somewhere",
            "country": "USA"
        }
    }
}

random.seed(42)
for i in range(200):
    schema_name = schema_names[i % 5]
    doc = test_docs[schema_name](i)
    # Clean up None values for schemaD
    if schema_name == 'schemaD':
        doc = {k: v for k, v in doc.items() if v is not None}

    doc_path = os.path.join(TESTDATA_DIR, f"doc_{i:03d}_{schema_name}.json")
    with open(doc_path, 'w') as f:
        json.dump(doc, f, indent=2)

print(f"Generated {len(os.listdir(SCHEMAS_DIR))} schemas")
print(f"Generated {len(os.listdir(TESTDATA_DIR))} test documents")
PYSCRIPT

RUN python3 << 'PYSCRIPT'
import json
import os
import hashlib
import subprocess

SCHEMAS_DIR = "/home/user/validator/schemas"
CACHE_DIR = "/home/user/validator/cache"

# Create some cached files (from the "failed optimization attempt")
for schema_file in os.listdir(SCHEMAS_DIR)[:10]:
    schema_path = os.path.join(SCHEMAS_DIR, schema_file)
    with open(schema_path, 'rb') as f:
        schema_hash = hashlib.md5(f.read()).hexdigest()

    # Preprocess with jq
    jq_filter = 'walk(if type == "object" and has("$shortref") then . + {"$ref": .["$shortref"]} | del(.["$shortref"]) else . end)'
    result = subprocess.run(
        ['jq', jq_filter, schema_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        cache_file = os.path.join(CACHE_DIR, f"{schema_hash}.json")
        with open(cache_file, 'w') as f:
            f.write(result.stdout)

print(f"Created {len(os.listdir(CACHE_DIR))} cached schema files")
PYSCRIPT

RUN chown -R 1000:1000 /home/user/validator && chmod -R 755 /home/user/validator

WORKDIR /home/user

CMD ["/bin/bash"]
