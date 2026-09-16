# Airbnb Market & Pricing Intelligence

An interactive data analytics dashboard built with **Python, Pandas, Streamlit, and Plotly** to explore Airbnb listings, pricing, hosts, locations, property types, room types, ratings, and review activity across 10 global cities.

> IBM SkillBuild Internship Project

## Project Overview

The project turns large Airbnb listing and review datasets into an interactive business-intelligence dashboard. Users can filter the listing dataset and investigate how **price, property type, room type, capacity, host characteristics, location, ratings, and review activity** vary across markets.

The project focuses on **market and pricing intelligence**. The available dataset does not contain booking-night or occupancy information, so the dashboard does **not** claim to calculate actual booking revenue.

## Dashboard Sections

| Tab | Analysis |
|---|---|
| 📊 Overview | KPIs, room-type distribution, property-type distribution, summary insights |
| 🗺️ Location | Geographic listing distribution, neighbourhood listing counts and prices |
| 💰 Pricing | City, capacity, property-group and price-distribution analysis |
| 🏡 Property & Room | Property groups, room types, capacity, pricing and ratings |
| 👤 Hosts | Superhost comparison, host growth, response-time and host-profile metrics |
| ⭐ Reviews | Review-score sub-metrics, rating distribution and review-volume trends |

## Dataset

| File | Rows | Description |
|---|---:|---|
| `Listings.csv` | 279,712 | Listing, host, location, property, room, price and review-score attributes |
| `Reviews.csv` | 5,373,143 | Review-level records containing listing ID, reviewer ID and review date |

**Cities covered:** Paris, New York, Sydney, Rome, Rio de Janeiro, Istanbul, Mexico City, Bangkok, Cape Town, and Hong Kong.

The dashboard reads only the listing columns required for analysis. For the reviews dataset, only `listing_id` and `date` are loaded before aggregation.

## Data Preparation

The pipeline includes:

- Removal of zero-price listings.
- Removal of listing prices above the 99.9th percentile to reduce the effect of extreme outliers.
- Conversion of boolean fields such as Superhost and Instant Bookable from `t`/`f` values.
- Parsing `host_since` into a datetime and deriving `host_since_year`.
- Numeric coercion of `bedrooms`, response rate, and acceptance rate.
- Creation of `price_per_person` from price and accommodates.
- Grouping detailed property types into broader analytical categories.
- Aggregation of the 5.37M review records into monthly review counts and listing-level review counts.

## Performance Approach

The review file is substantially larger than the listings file. To keep the Streamlit application practical:

1. Only `listing_id` and `date` are read from `Reviews.csv`.
2. Review records are aggregated into monthly and listing-level counts.
3. The raw review table is released after aggregation.
4. Streamlit caching avoids repeating expensive data-loading work during normal dashboard interaction.
5. Listings are loaded with selected columns and compact dtypes.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application and analytics logic |
| Pandas | Data loading, cleaning, transformation and aggregation |
| NumPy | Numeric/data-processing support |
| Plotly | Interactive charts and geographic visualisation |
| Streamlit | Interactive dashboard application |

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── Listings.csv
├── Reviews.csv
└── airbnb_dashboard/
    └── utils/
        ├── __init__.py
        ├── data_loader.py
        ├── analytics.py
        └── charts.py
```

## Setup and Run

### 1. Prerequisites

- Python 3.10+
- The dataset CSV files placed in the same project directory as `app.py`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
streamlit run app.py
```

The application will normally be available at `http://localhost:8501`.

## Important Dataset Note

The raw CSV files are large and are **not recommended for GitHub storage**. The repository should contain the application code, requirements, README, and project documentation, while the dataset can be obtained separately and placed beside `app.py` before running the application.

## Key Analytical Questions

The dashboard is designed to answer questions such as:

- How is Airbnb supply distributed across cities and neighbourhoods?
- How do prices vary by city, room type, property group, and guest capacity?
- What room and property categories represent the largest share of listings?
- How do Superhost and regular-host listing metrics differ?
- How do review scores vary across cities and score categories?
- How has review activity changed over time?

## Limitations

- The dataset provides listing prices, not realized booking revenue.
- Review counts are used as an activity signal and should not be interpreted as occupancy.
- The analysis describes the supplied dataset and should not automatically be treated as a current representation of Airbnb's live marketplace.
- Price is analysed as a listing attribute; it is not equivalent to realized transaction price.

## Disclaimer

This project is an educational analytics application developed for the IBM SkillBuild internship project using the supplied Airbnb datasets.
