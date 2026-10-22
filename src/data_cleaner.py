"""
COVID-19 Data Cleaner & Statistical Processing Engine
Pure Python / Standard Library implementation for robust cross-platform execution.
Processes raw JHU CSSE time series into tidy records, calculates 7-day rolling averages,
detects historical regional spikes, and classifies countries into high/moderate/controlled risk zones.
"""

import os
import csv
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    # Formats in JHU: m/d/yy e.g. 1/22/20
    parts = date_str.split('/')
    m = int(parts[0])
    d = int(parts[1])
    y = int(parts[2]) + 2000
    return f"{y:04d}-{m:02d}-{d:02d}"

def clean_and_transform_data(data_dir="data"):
    conf_file = os.path.join(data_dir, "time_series_covid19_confirmed_global.csv")
    death_file = os.path.join(data_dir, "time_series_covid19_deaths_global.csv")
    rec_file = os.path.join(data_dir, "time_series_covid19_recovered_global.csv")

    for f in [conf_file, death_file, rec_file]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Missing file: {f}")

    print("[1/4] Reading and aggregating Confirmed, Deaths, Recovered time-series...")

    # Data structures: country_dates[country][date] = {'confirmed': 0, 'deaths': 0, 'recovered': 0}
    country_dates = defaultdict(lambda: defaultdict(lambda: {'confirmed': 0, 'deaths': 0, 'recovered': 0}))

    def process_file(filepath, key_name):
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            date_indices = [(idx, parse_date(header[idx])) for idx in range(4, len(header))]
            for row in reader:
                if not row or len(row) < 5:
                    continue
                country = row[1].strip()
                for idx, dt in date_indices:
                    val = int(row[idx]) if row[idx] and row[idx].strip() != '' else 0
                    country_dates[country][dt][key_name] += val

    process_file(conf_file, 'confirmed')
    process_file(death_file, 'deaths')
    process_file(rec_file, 'recovered')

    all_countries = sorted(country_dates.keys())
    print(f"Aggregated {len(all_countries)} countries/regions across global time series.")

    print("[2/4] Computing 7-day rolling averages, daily new cases/deaths, and CFR%...")
    tidy_records = []
    country_summary_stats = []

    for country in all_countries:
        dates = sorted(country_dates[country].keys())
        prev_conf = 0
        prev_deaths = 0
        daily_cases_window = []
        daily_deaths_window = []
        
        peak_daily_cases = 0
        peak_date = None

        for dt in dates:
            curr = country_dates[country][dt]
            conf = curr['confirmed']
            deaths = curr['deaths']
            rec = curr['recovered']
            
            # Active cases
            active = max(0, conf - deaths - rec)

            # Daily increments
            daily_c = max(0, conf - prev_conf)
            daily_d = max(0, deaths - prev_deaths)
            prev_conf = conf
            prev_deaths = deaths

            # Peak tracking
            if daily_c > peak_daily_cases:
                peak_daily_cases = daily_c
                peak_date = dt

            # Rolling 7-day MA
            daily_cases_window.append(daily_c)
            if len(daily_cases_window) > 7:
                daily_cases_window.pop(0)
            cases_7d_ma = sum(daily_cases_window) / len(daily_cases_window)

            daily_deaths_window.append(daily_d)
            if len(daily_deaths_window) > 7:
                daily_deaths_window.pop(0)
            deaths_7d_ma = sum(daily_deaths_window) / len(daily_deaths_window)

            cfr = (deaths / conf * 100) if conf > 0 else 0.0
            rec_rate = (rec / conf * 100) if conf > 0 else 0.0

            tidy_records.append({
                'Country': country,
                'Date': dt,
                'Confirmed': conf,
                'Deaths': deaths,
                'Recovered': rec,
                'Active': active,
                'Daily_Cases': daily_c,
                'Daily_Deaths': daily_d,
                'Daily_Cases_7d_MA': round(cases_7d_ma, 2),
                'Daily_Deaths_7d_MA': round(deaths_7d_ma, 2),
                'CFR_Pct': round(cfr, 2),
                'Recovery_Rate_Pct': round(rec_rate, 2)
            })

        # Latest record for country summary
        latest_dt = dates[-1]
        latest = country_dates[country][latest_dt]
        latest_conf = latest['confirmed']
        latest_deaths = latest['deaths']
        latest_rec = latest['recovered']
        latest_active = max(0, latest_conf - latest_deaths - latest_rec)
        latest_cfr = (latest_deaths / latest_conf * 100) if latest_conf > 0 else 0.0

        # Risk category classification
        if latest_conf >= 5_000_000 or latest_cfr >= 4.0:
            risk = "High Risk Zone"
        elif latest_conf >= 500_000 or latest_cfr >= 2.0:
            risk = "Moderate Risk Zone"
        else:
            risk = "Controlled / Low Risk Zone"

        country_summary_stats.append({
            'Country': country,
            'Total_Confirmed': latest_conf,
            'Total_Deaths': latest_deaths,
            'Total_Recovered': latest_rec,
            'Active_Cases': latest_active,
            'CFR_Pct': round(latest_cfr, 2),
            'Peak_Daily_Cases': peak_daily_cases,
            'Peak_Date': peak_date,
            'Risk_Category': risk
        })

    # Sort summary by Total_Confirmed descending
    country_summary_stats.sort(key=lambda x: x['Total_Confirmed'], reverse=True)

    print(f"[3/4] Exporting country risk summary ({len(country_summary_stats)} countries)...")
    summary_path = os.path.join(data_dir, "country_risk_summary.csv")
    with open(summary_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Country', 'Total_Confirmed', 'Total_Deaths', 'Total_Recovered',
            'Active_Cases', 'CFR_Pct', 'Peak_Daily_Cases', 'Peak_Date', 'Risk_Category'
        ])
        writer.writeheader()
        writer.writerows(country_summary_stats)
    print(f" -> Saved to {summary_path}")

    print("[4/4] Exporting tidy time-series dataset...")
    tidy_path = os.path.join(data_dir, "covid_global_tidy.csv")
    with open(tidy_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Country', 'Date', 'Confirmed', 'Deaths', 'Recovered', 'Active',
            'Daily_Cases', 'Daily_Deaths', 'Daily_Cases_7d_MA', 'Daily_Deaths_7d_MA',
            'CFR_Pct', 'Recovery_Rate_Pct'
        ])
        writer.writeheader()
        writer.writerows(tidy_records)
    print(f" -> Saved {len(tidy_records):,} records to {tidy_path}")

    # Print top 10 impacted nations
    print("\n" + "=" * 70)
    print("GLOBAL COVID-19 TOP IMPACTED NATIONS & RISK ZONES")
    print("=" * 70)
    print(f"{'Country':<20} {'Confirmed':<15} {'Deaths':<12} {'CFR %':<10} {'Risk Category'}")
    print("-" * 70)
    for c in country_summary_stats[:10]:
        print(f"{c['Country']:<20} {c['Total_Confirmed']:<15,} {c['Total_Deaths']:<12,} {c['CFR_Pct']:<10.2f}% {c['Risk_Category']}")
    print("=" * 70)

    return country_summary_stats

if __name__ == "__main__":
    clean_and_transform_data()
