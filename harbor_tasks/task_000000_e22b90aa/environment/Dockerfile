FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN pip3 install pytest pandas pyarrow

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/pipeline/raw \
    && mkdir -p /home/user/pipeline/staging \
    && mkdir -p /home/user/pipeline/processed \
    && mkdir -p /home/user/pipeline/output

RUN cat <<'EOF' > /home/user/pipeline/raw/sensor_a.csv
sensor_id,recorded_at,value,unit
sensor_a_001,2024-03-01 08:00:00,23.5,celsius
sensor_a_002,2024-03-01 08:05:00,24.1,celsius
sensor_a_003,2024-03-01 08:10:00,23.8,celsius
sensor_a_004,2024-03-01 08:15:00,24.3,celsius
sensor_a_005,2024-03-01 08:20:00,24.0,celsius
sensor_a_006,2024-03-01 08:25:00,23.9,celsius
sensor_a_007,2024-03-01 08:30:00,24.2,celsius
sensor_a_008,2024-03-01 08:35:00,24.5,celsius
sensor_a_009,2024-03-01 08:40:00,24.7,celsius
sensor_a_010,2024-03-01 08:45:00,24.4,celsius
sensor_a_011,2024-03-01 08:50:00,24.1,celsius
sensor_a_012,2024-03-01 08:55:00,23.7,celsius
sensor_a_013,2024-03-01 09:00:00,23.5,celsius
sensor_a_014,2024-03-01 09:05:00,23.3,celsius
sensor_a_015,2024-03-01 09:10:00,23.6,celsius
sensor_a_016,2024-03-01 09:15:00,23.9,celsius
sensor_a_017,2024-03-01 09:20:00,24.2,celsius
sensor_a_018,2024-03-01 09:25:00,24.4,celsius
sensor_a_019,2024-03-01 09:30:00,24.6,celsius
sensor_a_020,2024-03-01 09:35:00,24.8,celsius
sensor_a_021,2024-03-01 09:40:00,25.0,celsius
sensor_a_022,2024-03-01 09:45:00,25.2,celsius
sensor_a_023,2024-03-01 09:50:00,25.1,celsius
sensor_a_024,2024-03-01 09:55:00,24.9,celsius
sensor_a_025,2024-03-01 10:00:00,24.7,celsius
sensor_a_026,2024-03-01 10:05:00,24.5,celsius
sensor_a_027,2024-03-01 10:10:00,24.3,celsius
sensor_a_028,2024-03-01 10:15:00,24.1,celsius
sensor_a_029,2024-03-01 10:20:00,23.9,celsius
sensor_a_030,2024-03-01 10:25:00,23.7,celsius
sensor_a_031,2024-03-01 10:30:00,23.5,celsius
sensor_a_032,2024-03-01 10:35:00,23.3,celsius
sensor_a_033,2024-03-01 10:40:00,23.1,celsius
sensor_a_034,2024-03-01 10:45:00,22.9,celsius
sensor_a_035,2024-03-01 10:50:00,22.7,celsius
sensor_a_036,2024-03-01 10:55:00,22.5,celsius
sensor_a_037,2024-03-01 11:00:00,22.3,celsius
sensor_a_038,2024-03-01 11:05:00,22.1,celsius
sensor_a_039,2024-03-01 11:10:00,21.9,celsius
sensor_a_040,2024-03-01 11:15:00,21.7,celsius
EOF

RUN cat <<'EOF' > /home/user/pipeline/raw/sensor_b.csv
sensor_id,recorded_at,value,unit
sensor_b_001,2024-03-01 08:00:00,1013.2,hPa
sensor_b_002,2024-03-01 08:05:00,1013.3,hPa
sensor_b_003,2024-03-01 08:10:00,1013.1,hPa
sensor_b_004,2024-03-01 08:15:00,1013.4,hPa
sensor_b_005,2024-03-01 08:20:00,1013.5,hPa
sensor_b_006,2024-03-01 08:25:00,1013.6,hPa
sensor_b_007,2024-03-01 08:30:00,1013.7,hPa
sensor_b_008,2024-03-01 08:35:00,1013.8,hPa
sensor_b_009,2024-03-01 08:40:00,1013.9,hPa
sensor_b_010,2024-03-01 08:45:00,1014.0,hPa
sensor_b_011,2024-03-01 08:50:00,1014.1,hPa
sensor_b_012,2024-03-01 08:55:00,1014.2,hPa
sensor_b_013,2024-03-01 09:00:00,1014.3,hPa
sensor_b_014,2024-03-01 09:05:00,1014.4,hPa
sensor_b_015,2024-03-01 09:10:00,1014.5,hPa
sensor_b_016,2024-03-01 09:15:00,1014.6,hPa
sensor_b_017,2024-03-01 09:20:00,1014.7,hPa
sensor_b_018,2024-03-01 09:25:00,1014.8,hPa
sensor_b_019,2024-03-01 09:30:00,1014.9,hPa
sensor_b_020,2024-03-01 09:35:00,1015.0,hPa
sensor_b_021,2024-03-01 09:40:00,1015.1,hPa
sensor_b_022,2024-03-01 09:45:00,1015.2,hPa
sensor_b_023,2024-03-01 09:50:00,1015.3,hPa
sensor_b_024,2024-03-01 09:55:00,1015.4,hPa
sensor_b_025,2024-03-01 10:00:00,1015.5,hPa
sensor_b_026,2024-03-01 10:05:00,1015.6,hPa
sensor_b_027,2024-03-01 10:10:00,1015.7,hPa
sensor_b_028,2024-03-01 10:15:00,1015.8,hPa
sensor_b_029,2024-03-01 10:20:00,1015.9,hPa
sensor_b_030,2024-03-01 10:25:00,1016.0,hPa
sensor_b_031,2024-03-01 10:30:00,1016.1,hPa
sensor_b_032,2024-03-01 10:35:00,1016.2,hPa
sensor_b_033,2024-03-01 10:40:00,1016.3,hPa
sensor_b_034,2024-03-01 10:45:00,1016.4,hPa
sensor_b_035,2024-03-01 10:50:00,1016.5,hPa
sensor_b_036,2024-03-01 10:55:00,1016.6,hPa
sensor_b_037,2024-03-01 11:00:00,1016.7,hPa
sensor_b_038,2024-03-01 11:05:00,1016.8,hPa
sensor_b_039,2024-03-01 11:10:00,1016.9,hPa
sensor_b_040,2024-03-01 11:15:00,1017.0,hPa
EOF

RUN cat <<'EOF' > /home/user/pipeline/raw/sensor_c.csv
sensor_id,recorded_at,value,unit
sensor_c_001,25/03/2024 14:30:00,65.2,percent
sensor_c_002,25/03/2024 14:35:00,65.5,percent
sensor_c_003,25/03/2024 14:40:00,65.8,percent
sensor_c_004,25/03/2024 14:45:00,66.1,percent
sensor_c_005,25/03/2024 14:50:00,66.4,percent
sensor_c_006,25/03/2024 14:55:00,66.7,percent
sensor_c_007,25/03/2024 15:00:00,67.0,percent
sensor_c_008,25/03/2024 15:05:00,67.3,percent
sensor_c_009,25/03/2024 15:10:00,67.6,percent
sensor_c_010,25/03/2024 15:15:00,67.9,percent
sensor_c_011,25/03/2024 15:20:00,68.2,percent
sensor_c_012,25/03/2024 15:25:00,68.5,percent
sensor_c_013,25/03/2024 15:30:00,68.8,percent
sensor_c_014,25/03/2024 15:35:00,69.1,percent
sensor_c_015,25/03/2024 15:40:00,69.4,percent
sensor_c_016,25/03/2024 15:45:00,69.7,percent
sensor_c_017,25/03/2024 15:50:00,70.0,percent
sensor_c_018,25/03/2024 15:55:00,70.3,percent
sensor_c_019,25/03/2024 16:00:00,70.6,percent
sensor_c_020,25/03/2024 16:05:00,70.9,percent
sensor_c_021,25/03/2024 16:10:00,71.2,percent
sensor_c_022,25/03/2024 16:15:00,71.5,percent
sensor_c_023,25/03/2024 16:20:00,71.8,percent
sensor_c_024,25/03/2024 16:25:00,72.1,percent
sensor_c_025,25/03/2024 16:30:00,72.4,percent
sensor_c_026,25/03/2024 16:35:00,72.7,percent
sensor_c_027,25/03/2024 16:40:00,73.0,percent
sensor_c_028,25/03/2024 16:45:00,73.3,percent
sensor_c_029,25/03/2024 16:50:00,73.6,percent
sensor_c_030,25/03/2024 16:55:00,73.9,percent
sensor_c_031,25/03/2024 17:00:00,74.2,percent
sensor_c_032,25/03/2024 17:05:00,74.5,percent
sensor_c_033,25/03/2024 17:10:00,74.8,percent
sensor_c_034,25/03/2024 17:15:00,75.1,percent
sensor_c_035,25/03/2024 17:20:00,75.4,percent
sensor_c_036,25/03/2024 17:25:00,75.7,percent
sensor_c_037,25/03/2024 17:30:00,76.0,percent
sensor_c_038,25/03/2024 17:35:00,76.3,percent
sensor_c_039,25/03/2024 17:40:00,76.6,percent
sensor_c_040,25/03/2024 17:45:00,76.9,percent
EOF

RUN cat <<'EOF' > /home/user/pipeline/raw/sensor_d.csv
sensor_id,recorded_at,value,unit
sensor_d_001,2024-03-01 08:00:00,5.2,m/s
sensor_d_002,2024-03-01 08:05:00,5.4,m/s
sensor_d_003,2024-03-01 08:10:00,5.6,m/s
sensor_d_004,2024-03-01 08:15:00,5.8,m/s
sensor_d_005,2024-03-01 08:20:00,6.0,m/s
sensor_d_006,2024-03-01 08:25:00,6.2,m/s
sensor_d_007,2024-03-01 08:30:00,6.4,m/s
sensor_d_008,2024-03-01 08:35:00,6.6,m/s
sensor_d_009,2024-03-01 08:40:00,6.8,m/s
sensor_d_010,2024-03-01 08:45:00,7.0,m/s
sensor_d_011,2024-03-01 08:50:00,7.2,m/s
sensor_d_012,2024-03-01 08:55:00,7.4,m/s
sensor_d_013,2024-03-01 09:00:00,7.6,m/s
sensor_d_014,2024-03-01 09:05:00,7.8,m/s
sensor_d_015,2024-03-01 09:10:00,8.0,m/s
sensor_d_016,2024-03-01 09:15:00,8.2,m/s
sensor_d_017,2024-03-01 09:20:00,8.4,m/s
sensor_d_018,2024-03-01 09:25:00,8.6,m/s
sensor_d_019,2024-03-01 09:30:00,8.8,m/s
sensor_d_020,2024-03-01 09:35:00,9.0,m/s
sensor_d_021,2024-03-01 09:40:00,9.2,m/s
sensor_d_022,2024-03-01 09:45:00,9.4,m/s
sensor_d_023,2024-03-01 09:50:00,9.6,m/s
sensor_d_024,2024-03-01 09:55:00,9.8,m/s
sensor_d_025,2024-03-01 10:00:00,10.0,m/s
sensor_d_026,2024-03-01 10:05:00,10.2,m/s
sensor_d_027,2024-03-01 10:10:00,10.4,m/s
sensor_d_028,2024-03-01 10:15:00,10.6,m/s
sensor_d_029,2024-03-01 10:20:00,10.8,m/s
sensor_d_030,2024-03-01 10:25:00,11.0,m/s
sensor_d_031,2024-03-01 10:30:00,11.2,m/s
sensor_d_032,2024-03-01 10:35:00,11.4,m/s
sensor_d_033,2024-03-01 10:40:00,11.6,m/s
sensor_d_034,2024-03-01 10:45:00,11.8,m/s
sensor_d_035,2024-03-01 10:50:00,12.0,m/s
sensor_d_036,2024-03-01 10:55:00,12.2,m/s
sensor_d_037,2024-03-01 11:00:00,12.4,m/s
sensor_d_038,2024-03-01 11:05:00,12.6,m/s
sensor_d_039,2024-03-01 11:10:00,12.8,m/s
sensor_d_040,2024-03-01 11:15:00,13.0,m/s
EOF

RUN cat <<'EOF' > /home/user/pipeline/raw/sensor_e.csv
sensor_id,recorded_at,value,unit
sensor_e_001,2024-03-01 08:00:00,850.5,lux
sensor_e_002,2024-03-01 08:05:00,875.2,lux
sensor_e_003,2024-03-01 08:10:00,900.1,lux
sensor_e_004,2024-03-01 08:15:00,925.8,lux
sensor_e_005,2024-03-01 08:20:00,950.3,lux
sensor_e_006,2024-03-01 08:25:00,975.6,lux
sensor_e_007,2024-03-01 08:30:00,1000.2,lux
sensor_e_008,2024-03-01 08:35:00,1025.9,lux
sensor_e_009,2024-03-01 08:40:00,1050.4,lux
sensor_e_010,2024-03-01 08:45:00,1075.7,lux
sensor_e_011,2024-03-01 08:50:00,1100.1,lux
sensor_e_012,2024-03-01 08:55:00,1125.8,lux
sensor_e_013,2024-03-01 09:00:00,1150.3,lux
sensor_e_014,2024-03-01 09:05:00,1175.6,lux
sensor_e_015,2024-03-01 09:10:00,1200.2,lux
sensor_e_016,2024-03-01 09:15:00,1225.9,lux
sensor_e_017,2024-03-01 09:20:00,1250.4,lux
sensor_e_018,2024-03-01 09:25:00,1275.7,lux
sensor_e_019,2024-03-01 09:30:00,1300.1,lux
sensor_e_020,2024-03-01 09:35:00,1325.8,lux
sensor_e_021,2024-03-01 09:40:00,1350.3,lux
sensor_e_022,2024-03-01 09:45:00,1375.6,lux
sensor_e_023,2024-03-01 09:50:00,1400.2,lux
sensor_e_024,2024-03-01 09:55:00,1425.9,lux
sensor_e_025,2024-03-01 10:00:00,1450.4,lux
sensor_e_026,2024-03-01 10:05:00,1475.7,lux
sensor_e_027,2024-03-01 10:10:00,1500.1,lux
sensor_e_028,2024-03-01 10:15:00,1525.8,lux
sensor_e_029,2024-03-01 10:20:00,1550.3,lux
sensor_e_030,2024-03-01 10:25:00,1575.6,lux
sensor_e_031,2024-03-01 10:30:00,1600.2,lux
sensor_e_032,2024-03-01 10:35:00,1625.9,lux
sensor_e_033,2024-03-01 10:40:00,1650.4,lux
sensor_e_034,2024-03-01 10:45:00,1675.7,lux
sensor_e_035,2024-03-01 10:50:00,1700.1,lux
sensor_e_036,2024-03-01 10:55:00,1725.8,lux
sensor_e_037,2024-03-01 11:00:00,1750.3,lux
sensor_e_038,2024-03-01 11:05:00,1775.6,lux
sensor_e_039,2024-03-01 11:10:00,1800.2,lux
sensor_e_040,2024-03-01 11:15:00,1825.9,lux
EOF

RUN cat <<'EOF' > /home/user/pipeline/extract.py
#!/usr/bin/env python3
"""
Extract stage: Read CSVs from raw/ and write to staging/ as parquet files.
Performs minimal validation.
"""

import os
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
STAGING_DIR = Path(__file__).parent / "staging"

def extract():
    """Read all CSV files from raw/ and write to staging/ as parquet."""
    STAGING_DIR.mkdir(exist_ok=True)

    csv_files = list(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {RAW_DIR}")

    for csv_file in csv_files:
        print(f"Extracting {csv_file.name}...")
        df = pd.read_csv(csv_file)

        # Minimal validation
        required_columns = {"sensor_id", "recorded_at", "value", "unit"}
        if not required_columns.issubset(set(df.columns)):
            raise ValueError(f"{csv_file.name} missing required columns")

        # Write to staging as parquet (keep recorded_at as string for now)
        output_file = STAGING_DIR / f"{csv_file.stem}.parquet"
        df.to_parquet(output_file, index=False)
        print(f"  -> Written to {output_file.name}")

if __name__ == "__main__":
    extract()
    print("Extract stage complete.")
EOF

RUN cat <<'EOF' > /home/user/pipeline/transform.py
#!/usr/bin/env python3
"""
Transform stage: Read from staging/, apply transformations, write to processed/.
Includes unit conversions and datetime parsing.
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime

STAGING_DIR = Path(__file__).parent / "staging"
PROCESSED_DIR = Path(__file__).parent / "processed"

def convert_units(df):
    """Apply unit conversions where needed."""
    # Convert Celsius to Kelvin for temperature sensors
    mask = df['unit'] == 'celsius'
    df.loc[mask, 'value'] = df.loc[mask, 'value'] + 273.15
    df.loc[mask, 'unit'] = 'kelvin'
    return df

def parse_timestamps(df):
    """Parse recorded_at strings to datetime objects."""
    # BUG: This hardcoded format doesn't handle European date format (DD/MM/YYYY)
    # from sensor_c.csv, causing those rows to become NaT
    df['recorded_at'] = pd.to_datetime(
        df['recorded_at'], 
        format="%Y-%m-%d %H:%M:%S",
        errors='coerce'
    )
    return df

def transform():
    """Read from staging/, transform, and write to processed/."""
    PROCESSED_DIR.mkdir(exist_ok=True)

    parquet_files = list(STAGING_DIR.glob("*.parquet"))
    if not parquet_files:
        raise ValueError(f"No parquet files found in {STAGING_DIR}")

    for parquet_file in parquet_files:
        print(f"Transforming {parquet_file.name}...")
        df = pd.read_parquet(parquet_file)

        # Apply transformations
        df = parse_timestamps(df)
        df = convert_units(df)

        # Write to processed
        output_file = PROCESSED_DIR / parquet_file.name
        df.to_parquet(output_file, index=False)
        print(f"  -> Written to {output_file.name}")

if __name__ == "__main__":
    transform()
    print("Transform stage complete.")
EOF

RUN cat <<'EOF' > /home/user/pipeline/load.py
#!/usr/bin/env python3
"""
Load stage: Concatenate all parquet files from processed/ into output/merged.parquet.
"""

import os
import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent / "processed"
OUTPUT_DIR = Path(__file__).parent / "output"

def load():
    """Concatenate all processed parquet files into merged output."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    parquet_files = list(PROCESSED_DIR.glob("*.parquet"))
    if not parquet_files:
        raise ValueError(f"No parquet files found in {PROCESSED_DIR}")

    print(f"Loading {len(parquet_files)} files...")
    dfs = []
    for parquet_file in sorted(parquet_files):
        print(f"  Reading {parquet_file.name}...")
        df = pd.read_parquet(parquet_file)
        dfs.append(df)

    merged_df = pd.concat(dfs, ignore_index=True)

    output_file = OUTPUT_DIR / "merged.parquet"
    merged_df.to_parquet(output_file, index=False)
    print(f"Merged {len(merged_df)} rows into {output_file}")

if __name__ == "__main__":
    load()
    print("Load stage complete.")
EOF

RUN cat <<'EOF' > /home/user/pipeline/run.sh
#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 extract.py && python3 transform.py && python3 load.py
EOF

RUN chmod +x /home/user/pipeline/run.sh

RUN cd /home/user/pipeline && bash run.sh

RUN chmod -R 0777 /home/user/pipeline

WORKDIR /home/user

CMD ["/bin/bash"]
