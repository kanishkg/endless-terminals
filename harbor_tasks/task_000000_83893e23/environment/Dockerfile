FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pandas numpy scipy pytest

RUN mkdir -p /home/user/capacity/data /home/user/capacity/output && \
    chmod -R 0777 /home/user

RUN python3 << 'PYGEN'
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# Generate hosts.csv - 52 weeks of hourly data for 3 hosts
# 52 weeks * 7 days * 24 hours = 8736 hours per host
start_date = datetime(2024, 1, 1, 0, 0, 0)
hours_per_year = 52 * 7 * 24  # 8736

hosts_data = []
host_ids = ['host-a', 'host-b', 'host-c']

for host_id in host_ids:
    for hour in range(hours_per_year):
        ts = start_date + timedelta(hours=hour)
        # Generate cpu_hours that will average ~847/week across all hosts when summed
        # 847 / 3 hosts / 168 hours per week ≈ 1.68 per host per hour
        # Add some variation
        base_cpu = 1.5 + random.gauss(0.18, 0.3)
        base_cpu = max(0.5, min(3.0, base_cpu))  # clamp
        mem_gb = base_cpu * 2 + random.gauss(0, 0.5)
        mem_gb = max(0.5, mem_gb)
        hosts_data.append({
            'host_id': host_id,
            'timestamp': ts.isoformat(),
            'cpu_hours': round(base_cpu, 4),
            'mem_gb_hours': round(mem_gb, 4)
        })

hosts_df = pd.DataFrame(hosts_data)
hosts_df.to_csv('/home/user/capacity/data/hosts.csv', index=False)

# Generate reservations.csv - ~150 reservations spread across the year
reservations_data = []
reservation_counts = {'host-a': 50, 'host-b': 55, 'host-c': 45}  # ~150 total

res_id = 1
for host_id, count in reservation_counts.items():
    for _ in range(count):
        # Random start time within the year
        start_hour = random.randint(0, hours_per_year - 168)  # at least 1 week before end
        duration_hours = random.randint(24, 168)  # 1-7 days
        start_time = start_date + timedelta(hours=start_hour)
        end_time = start_time + timedelta(hours=duration_hours)
        requested_cpu = random.randint(10, 100)
        reservations_data.append({
            'reservation_id': f'res-{res_id:04d}',
            'host_id': host_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'requested_cpu_hours': requested_cpu
        })
        res_id += 1

reservations_df = pd.DataFrame(reservations_data)
reservations_df.to_csv('/home/user/capacity/data/reservations.csv', index=False)

print(f"Generated {len(hosts_df)} host records")
print(f"Generated {len(reservations_df)} reservation records")
PYGEN

RUN cat << 'FORECAST_SCRIPT' > /home/user/capacity/forecast.py
#!/usr/bin/env python3
"""
Capacity Forecasting Pipeline

Loads host metrics and reservation data, rolls up to weekly totals,
fits a growth curve, and projects forward.
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

HOSTS_CSV = DATA_DIR / "hosts.csv"
RESERVATIONS_CSV = DATA_DIR / "reservations.csv"
OUTPUT_CSV = OUTPUT_DIR / "forecast.csv"


def exponential_growth(x, a, b, c):
    """Exponential growth model: y = a * exp(b * x) + c"""
    return a * np.exp(b * x) + c


def load_data():
    """Load host metrics and reservation data."""
    print("Loading hosts.csv...")
    hosts = pd.read_csv(HOSTS_CSV)
    hosts['timestamp'] = pd.to_datetime(hosts['timestamp'])

    print("Loading reservations.csv...")
    reservations = pd.read_csv(RESERVATIONS_CSV)
    reservations['start_time'] = pd.to_datetime(reservations['start_time'])
    reservations['end_time'] = pd.to_datetime(reservations['end_time'])

    return hosts, reservations


def enrich_metrics_with_reservations(hosts, reservations):
    """Merge host metrics with reservation context for enriched analysis."""
    # Join hosts with reservations to get reservation context
    merged = pd.merge(hosts, reservations, on='host_id')
    return merged


def compute_weekly_totals(data):
    """Aggregate metrics to weekly totals."""
    # Extract ISO week number
    data = data.copy()
    data['week'] = data['timestamp'].dt.isocalendar().week

    # Sum cpu_hours by week
    weekly = data.groupby('week')['cpu_hours'].sum().reset_index()
    weekly.columns = ['week', 'cpu_hours']

    return weekly


def fit_growth_curve(weekly):
    """Fit exponential growth curve to weekly data."""
    x = weekly['week'].values
    y = weekly['cpu_hours'].values

    # Initial guess for parameters
    try:
        popt, _ = curve_fit(
            exponential_growth, 
            x, y,
            p0=[1, 0.01, y.mean()],
            maxfev=10000,
            bounds=([0, -0.1, 0], [np.inf, 0.5, np.inf])
        )
    except RuntimeError:
        # Fallback to linear if exponential doesn't converge
        popt = [0, 0, y.mean()]

    return popt


def generate_forecast(weekly, params, weeks_ahead=8):
    """Generate forecast for future weeks."""
    last_week = weekly['week'].max()

    # Historical data
    historical = weekly.copy()
    historical['type'] = 'historical'

    # Forecast data
    forecast_weeks = list(range(last_week + 1, last_week + weeks_ahead + 1))
    forecast_values = [exponential_growth(w, *params) for w in forecast_weeks]

    forecast = pd.DataFrame({
        'week': forecast_weeks,
        'cpu_hours': forecast_values,
        'type': ['forecast'] * len(forecast_weeks)
    })

    # Combine
    result = pd.concat([historical, forecast], ignore_index=True)

    return result


def main():
    """Main pipeline."""
    print("=" * 50)
    print("Capacity Forecasting Pipeline")
    print("=" * 50)

    # Load data
    hosts, reservations = load_data()
    print(f"Loaded {len(hosts)} host metric records")
    print(f"Loaded {len(reservations)} reservation records")

    # Enrich metrics with reservation data
    print("\nEnriching metrics with reservation context...")
    enriched = enrich_metrics_with_reservations(hosts, reservations)
    print(f"Enriched dataset has {len(enriched)} records")

    # Compute weekly totals
    print("\nComputing weekly totals...")
    weekly = compute_weekly_totals(enriched)
    print(f"Generated {len(weekly)} weekly data points")

    # Fit growth curve
    print("\nFitting growth curve...")
    params = fit_growth_curve(weekly)
    print(f"Model parameters: a={params[0]:.4f}, b={params[1]:.6f}, c={params[2]:.2f}")

    # Generate forecast
    print("\nGenerating 8-week forecast...")
    result = generate_forecast(weekly, params)

    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)
    print(f"\nForecast saved to {OUTPUT_CSV}")

    # Summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    q4_weeks = weekly[weekly['week'] >= 40]
    print(f"Q4 average (weeks 40-52): {q4_weeks['cpu_hours'].mean():.1f} cpu_hours/week")
    print(f"Last week ({weekly['week'].max()}): {weekly['cpu_hours'].iloc[-1]:.1f} cpu_hours")
    forecast_only = result[result['type'] == 'forecast']
    print(f"Forecast range: {forecast_only['cpu_hours'].min():.1f} - {forecast_only['cpu_hours'].max():.1f} cpu_hours")


if __name__ == "__main__":
    main()
FORECAST_SCRIPT

RUN chmod +x /home/user/capacity/forecast.py

RUN cd /home/user/capacity && python3 forecast.py

RUN chmod -R 0777 /home/user

WORKDIR /home/user

CMD ["/bin/bash"]
