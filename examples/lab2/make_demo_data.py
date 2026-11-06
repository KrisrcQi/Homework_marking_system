"""Create a small, synthetic retail dataset for trying the example notebooks.

This is original demonstration data, not the course's retail dataset.
"""
from pathlib import Path
import csv


def write_demo(path):
    rows = [
        ['03/01/2025', 'South', 'P001', 'Office', 100, 60, 40],
        ['05/01/2025', 'North', 'P002', 'Home', 80, 50, 30],
        ['06/02/2025', 'South', 'P003', 'Office', 120, '', 50],
        ['07/02/2025', '', 'P004', 'Home', 90, 40, 50],
        ['08/03/2025', 'West', 'P005', '', 70, 35, 35],
        ['09/03/2025', 'East', 'P006', 'Fashion', -10, 20, -30],
        ['10/01/2026', 'South', 'P007', 'Office', 150, 80, 70],
        ['11/02/2026', 'North', 'P008', 'Home', 110, 60, 50],
        ['12/03/2026', 'West', 'P009', 'Electronics', 95, 50, 45],
        ['13/03/2026', 'South', 'P010', 'Office', 140, 75, 65],
        ['14/03/2026', 'East', 'P011', 'Fashion', 60, 40, 20],
    ]
    rows.append(rows[0].copy())
    path = Path(path)
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Region', 'Product', 'Category', 'Sales', 'Cost', 'Profit'])
        writer.writerows(rows)
    return path


if __name__ == '__main__':
    target = Path(__file__).with_name('retail_data.csv')
    if target.exists():
        raise SystemExit('retail_data.csv already exists; move it before creating demo data.')
    print(write_demo(target))
