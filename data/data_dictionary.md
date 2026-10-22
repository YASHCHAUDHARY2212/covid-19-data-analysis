# COVID-19 Dataset Dictionary & Schema

## 1. Raw JHU CSSE Files
- `time_series_covid19_confirmed_global.csv`: Daily cumulative confirmed cases by province/state and country.
- `time_series_covid19_deaths_global.csv`: Daily cumulative death counts by province/state and country.
- `time_series_covid19_recovered_global.csv`: Daily cumulative recovery numbers.

---

## 2. Processed Tidy Dataset: `data/covid_global_tidy.csv`
A standardized, long-format time series dataset aggregated at the national level.

| Column | Data Type | Description |
|:---|:---|:---|
| **Country** | String | Name of the country or territory (201 unique entities) |
| **Date** | Date (`YYYY-MM-DD`)| Surveillance date (2020-01-22 through 2023-03-09) |
| **Confirmed** | Integer | Cumulative confirmed positive test cases |
| **Deaths** | Integer | Cumulative recorded fatalities |
| **Recovered** | Integer | Cumulative recovered patients |
| **Active** | Integer | Active estimated cases (`Confirmed - Deaths - Recovered`) |
| **Daily_Cases** | Integer | New reported cases on that specific calendar day |
| **Daily_Deaths** | Integer | New reported fatalities on that specific calendar day |
| **Daily_Cases_7d_MA**| Float | 7-day rolling moving average of daily cases |
| **Daily_Deaths_7d_MA**| Float | 7-day rolling moving average of daily fatalities |
| **CFR_Pct** | Float | Cumulative Case Fatality Rate (`(Deaths / Confirmed) * 100`) |
| **Recovery_Rate_Pct**| Float | Cumulative Recovery Rate (`(Recovered / Confirmed) * 100`) |

---

## 3. Country Risk Summary: `data/country_risk_summary.csv`
Snapshot table ranking each nation's cumulative burden and risk tier.

| Column | Description |
|:---|:---|
| **Country** | Country name |
| **Total_Confirmed**| Latest cumulative confirmed cases |
| **Total_Deaths** | Latest cumulative deaths |
| **Total_Recovered**| Latest cumulative recoveries |
| **Active_Cases** | Current active estimated burden |
| **CFR_Pct** | Overall Case Fatality Rate percentage |
| **Peak_Daily_Cases**| Highest single-day case spike recorded historically |
| **Peak_Date** | Calendar date when the historical peak occurred |
| **Risk_Category** | Epidemiological risk tier (`High Risk Zone`, `Moderate Risk Zone`, `Controlled / Low Risk Zone`) |
