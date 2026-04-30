FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest numpy==1.26.0 pandas==2.1.0 pyarrow==14.0.0

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/research/raw \
    && mkdir -p /home/user/research/output \
    && mkdir -p /home/user/research/utils \
    && chmod -R 0777 /home/user/research

RUN touch /home/user/research/utils/__init__.py && chmod 0666 /home/user/research/utils/__init__.py

RUN cat << 'EOF' > /home/user/research/utils/converters.py
"""Utility functions for data type conversions."""

import numpy as np


def convert_to_int_safe(series):
    """Convert a pandas series to integer, handling NaN values."""
    return series.fillna(0).astype(np.int)


def convert_object_columns(df, columns):
    """Convert specified columns to object dtype."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(np.object)
    return df


def convert_bool_column(series):
    """Convert a series to boolean type."""
    return series.fillna(False).astype(np.bool)


def standardize_dtypes(df):
    """Standardize dtypes across the dataframe."""
    # Convert ID columns to int
    if 'respondent_id' in df.columns:
        df['respondent_id'] = convert_to_int_safe(df['respondent_id'])

    # Convert text columns to object
    text_cols = ['comments', 'feedback']
    df = convert_object_columns(df, text_cols)

    # Convert boolean columns
    if 'is_complete' in df.columns:
        df['is_complete'] = convert_bool_column(df['is_complete'])

    return df
EOF
RUN chmod 0666 /home/user/research/utils/converters.py

RUN cat << 'EOF' > /home/user/research/prep_data.py
"""Data preparation script for survey responses."""

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from utils.converters import standardize_dtypes


def load_raw_data(filepath):
    """Load raw CSV data."""
    return pd.read_csv(filepath)


def clean_numeric_columns(df):
    """Clean and convert numeric columns."""
    # Convert score columns to float
    score_cols = ['satisfaction_score', 'recommendation_score', 'effort_score']
    for col in score_cols:
        if col in df.columns:
            df[col] = df[col].astype(np.float)

    # Convert age to float for handling missing values
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce').astype(np.float)

    return df


def prepare_data():
    """Main data preparation function."""
    # Load raw data
    df = load_raw_data('/home/user/research/raw/survey_responses.csv')

    # Clean numeric columns
    df = clean_numeric_columns(df)

    # Standardize dtypes using utility functions
    df = standardize_dtypes(df)

    # Write to parquet
    output_path = '/home/user/research/output/cleaned_survey.parquet'
    df.to_parquet(output_path, engine='pyarrow', index=False)

    print(f"Successfully wrote {len(df)} rows to {output_path}")


if __name__ == '__main__':
    prepare_data()
EOF
RUN chmod 0666 /home/user/research/prep_data.py

RUN python3 << 'PYSCRIPT'
import csv
import random
import os

random.seed(42)

# Generate 500 rows of survey data
headers = [
    'respondent_id', 'age', 'satisfaction_score', 'recommendation_score', 
    'effort_score', 'comments', 'feedback', 'is_complete'
]

comments_options = [
    'Great service!', 'Could be better', 'Very satisfied', 'No comment',
    'Excellent experience', 'Average', 'Will recommend', 'Needs improvement',
    '', 'Outstanding support', 'Fast response', 'Good quality'
]

feedback_options = [
    'Positive', 'Negative', 'Neutral', '', 'Mixed', 'Very positive',
    'Somewhat negative', 'No feedback'
]

rows = []
for i in range(1, 501):
    row = {
        'respondent_id': i,
        'age': random.choice([random.randint(18, 80), '']),  # Some missing ages
        'satisfaction_score': round(random.uniform(1, 10), 2),
        'recommendation_score': round(random.uniform(1, 10), 2),
        'effort_score': round(random.uniform(1, 10), 2),
        'comments': random.choice(comments_options),
        'feedback': random.choice(feedback_options),
        'is_complete': random.choice([True, False, ''])
    }
    rows.append(row)

output_path = '/home/user/research/raw/survey_responses.csv'
with open(output_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} rows to {output_path}")
PYSCRIPT

RUN chmod 0666 /home/user/research/raw/survey_responses.csv

RUN chmod -R 0777 /home/user/research

WORKDIR /home/user

CMD ["/bin/bash"]
