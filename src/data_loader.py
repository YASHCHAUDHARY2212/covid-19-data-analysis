"""
COVID-19 Data Ingestion Module
Downloads official Johns Hopkins University (JHU CSSE) time-series datasets
and verifies integrity.
"""

import os
import urllib.request

JHU_BASE_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"

FILES = {
    "confirmed": "time_series_covid19_confirmed_global.csv",
    "deaths": "time_series_covid19_deaths_global.csv",
    "recovered": "time_series_covid19_recovered_global.csv"
}

def download_data(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    for key, filename in FILES.items():
        url = f"{JHU_BASE_URL}/{filename}"
        dest_path = os.path.join(output_dir, filename)
        if not os.path.exists(dest_path) or os.path.getsize(dest_path) < 1000:
            print(f"Downloading {key} dataset from JHU CSSE...")
            urllib.request.urlretrieve(url, dest_path)
            print(f" -> Saved to {dest_path} ({os.path.getsize(dest_path) / 1024:.1f} KB)")
        else:
            print(f"Dataset {filename} already present locally.")
        paths[key] = dest_path
    return paths

if __name__ == "__main__":
    download_data()
