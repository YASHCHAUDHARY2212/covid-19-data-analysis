"""
COVID-19 Exploratory Data Analysis & Epidemiological Risk Engine
Analyzes global trajectory, regional wave spikes, CFR comparisons,
and outputs statistical metrics for reports and dashboards.
"""

import os
import csv
import json
from collections import defaultdict

def run_eda(data_dir="data"):
    tidy_file = os.path.join(data_dir, "covid_global_tidy.csv")
    summary_file = os.path.join(data_dir, "country_risk_summary.csv")

    if not os.path.exists(tidy_file) or not os.path.exists(summary_file):
        raise FileNotFoundError("Run data_cleaner.py first to generate processed datasets.")

    print("[1/3] Reading country summaries and computing global aggregates...")
    country_summaries = []
    with open(summary_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            country_summaries.append({
                'Country': r['Country'],
                'Confirmed': int(r['Total_Confirmed']),
                'Deaths': int(r['Total_Deaths']),
                'Recovered': int(r['Total_Recovered']),
                'Active': int(r['Active_Cases']),
                'CFR_Pct': float(r['CFR_Pct']),
                'Peak_Daily_Cases': int(r['Peak_Daily_Cases']),
                'Peak_Date': r['Peak_Date'],
                'Risk_Category': r['Risk_Category']
            })

    total_global_confirmed = sum(c['Confirmed'] for c in country_summaries)
    total_global_deaths = sum(c['Deaths'] for c in country_summaries)
    total_global_recovered = sum(c['Recovered'] for c in country_summaries)
    global_cfr = (total_global_deaths / total_global_confirmed * 100) if total_global_confirmed > 0 else 0

    risk_counts = defaultdict(int)
    risk_cases = defaultdict(int)
    for c in country_summaries:
        risk_counts[c['Risk_Category']] += 1
        risk_cases[c['Risk_Category']] += c['Confirmed']

    print(f"Global Confirmed: {total_global_confirmed:,}")
    print(f"Global Deaths:    {total_global_deaths:,}")
    print(f"Global CFR:       {global_cfr:.2f}%")

    print("[2/3] Analyzing regional wave spikes for key hotspot nations...")
    hotspot_nations = ['US', 'India', 'Brazil', 'United Kingdom', 'France']
    hotspot_wave_data = {}

    for target in hotspot_nations:
        target_records = [c for c in country_summaries if c['Country'] == target]
        if target_records:
            t = target_records[0]
            hotspot_wave_data[target] = {
                'total_cases': t['Confirmed'],
                'total_deaths': t['Deaths'],
                'cfr_pct': t['CFR_Pct'],
                'peak_daily_spike': t['Peak_Daily_Cases'],
                'peak_date': t['Peak_Date'],
                'risk_tier': t['Risk_Category']
            }

    # Identify highest CFR nations (with at least 50,000 cases to avoid small-sample bias)
    qualified_countries = [c for c in country_summaries if c['Confirmed'] >= 50000]
    highest_cfr_nations = sorted(qualified_countries, key=lambda x: x['CFR_Pct'], reverse=True)[:5]
    lowest_cfr_nations = sorted(qualified_countries, key=lambda x: x['CFR_Pct'])[:5]

    results = {
        'global_kpis': {
            'total_confirmed': total_global_confirmed,
            'total_deaths': total_global_deaths,
            'total_recovered': total_global_recovered,
            'global_cfr_pct': round(global_cfr, 2),
            'total_countries_tracked': len(country_summaries)
        },
        'risk_zones_breakdown': {
            'counts': dict(risk_counts),
            'cases_share_pct': {
                k: round((v / total_global_confirmed) * 100, 2) for k, v in risk_cases.items()
            }
        },
        'top_10_countries': country_summaries[:10],
        'hotspot_spikes': hotspot_wave_data,
        'highest_mortality_nations': highest_cfr_nations,
        'lowest_mortality_nations': lowest_cfr_nations
    }

    out_json = os.path.join(data_dir, "eda_insights.json")
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"[3/3] Analysis completed and exported to {out_json}!")
    return results

if __name__ == "__main__":
    run_eda()
