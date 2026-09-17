# Airbnb Market & Pricing Intelligence

A professional **Data Analytics project** that analyzes Airbnb listings, pricing patterns, locations, host characteristics, ratings, and review activity across 10 global cities.

> **IBM SkillsBuild Data Analytics Internship Project**

## 📌 Project Overview

Airbnb listings vary significantly by location, room type, property type, guest capacity, host characteristics, and customer feedback.

This project uses Python-based data analytics to answer practical marketplace questions such as:

- How is Airbnb supply distributed across cities and listing categories?
- How do advertised listing prices vary by city, room type, property type, and guest capacity?
- What descriptive differences can be observed between Superhosts and other hosts?
- How do ratings vary across markets and listing segments?
- How has review activity changed over time?
- What business insights can be derived from these patterns?

### Important data note

The supplied dataset contains **advertised listing prices**, not realized booking revenue or occupancy data. Therefore, this project focuses on **market and pricing intelligence** rather than actual revenue or profit analysis.

---

## 🎯 Objectives

1. Analyze Airbnb listing distribution across cities, room types, property types, and neighbourhoods.
2. Understand pricing patterns using mean, median, and segment-level comparisons.
3. Examine the relationship between guest capacity and advertised price.
4. Compare descriptive host characteristics, including Superhost status.
5. Analyze listing ratings and review activity.
6. Translate data-driven findings into practical business recommendations.

---

## 📊 Project Components

### 1. Jupyter Notebook

`DeepanshuGautam_AirbnbMarketPricingIntelligence.ipynb`

The notebook contains the detailed analytical workflow:

- Business problem and objectives
- Dataset understanding
- Data quality audit
- Data cleaning
- Feature engineering
- Exploratory Data Analysis
- Pricing intelligence
- Location analysis
- Host analysis
- Reviews and ratings analysis
- Cross-analysis
- Business findings
- Recommendations
- Limitations and future scope

### 2. Streamlit Dashboard

`app.py`

The interactive dashboard provides:

| Section | Focus |
|---|---|
| Overview | Marketplace KPIs and listing composition |
| Location | Geographic distribution and location patterns |
| Pricing | Price comparisons and capacity-related analysis |
| Property & Room | Property and room-type analysis |
| Hosts | Superhost and host-performance comparisons |
| Reviews | Ratings and review activity |

---

## 📊 Dataset

This project uses the **Airbnb Listings & Reviews Dataset**, containing Airbnb listing information and historical review data across 10 major cities.

### Dataset Source

The dataset was obtained from Kaggle:

🔗 **[Airbnb Listings & Reviews Dataset – Kaggle](https://www.kaggle.com/datasets/joyshil0599/airbnb-listings-reviews)**

The dataset includes:

- `Listings.csv` — listing, host, property, pricing, availability, and rating information
- `Reviews.csv` — historical review records
- `Listings_data_dictionary.csv` — data dictionary for listing variables
- `Reviews_data_dictionary.csv` — data dictionary for review variables

> **Note:** The raw `Listings.csv` and `Reviews.csv` files are large and are therefore managed separately using Git LFS for the Streamlit deployment. The data dictionaries are included in this repository.

### Cities Covered

Paris, New York, Sydney, Rome, Rio de Janeiro, Istanbul, Mexico City, Bangkok, Cape Town, and Hong Kong.

### Dataset fields used

Examples include:

`listing_id`, `host_id`, `host_since`, `host_response_rate`, `host_acceptance_rate`, `host_is_superhost`, `host_total_listings_count`, `neighbourhood`, `city`, `latitude`, `longitude`, `property_type`, `room_type`, `accommodates`, `bedrooms`, `price`, `minimum_nights`, `maximum_nights`, `review_scores_rating`, `review_scores_cleanliness`, `review_scores_location`, `review_scores_value`, `instant_bookable`

---

## 🧹 Data Cleaning

The project includes documented data-quality checks and cleaning steps, including:

- Duplicate checks
- Numeric conversion
- Date conversion
- Boolean standardization
- Invalid/zero-price removal
- Price outlier treatment using the 99.9th percentile
- Safe handling of missing analytical fields
- Feature creation such as `price_per_person`
- Simplification of granular property types into analytical groups

Cleaning decisions are documented in the notebook rather than silently applied.

---

## 📈 Visual Analytics

The notebook uses:

- **Pandas** for data manipulation
- **NumPy** for numerical operations
- **Matplotlib** for analytical charts
- **Seaborn** for statistical visualizations
- **Plotly** for interactive visualizations and geographic analysis
- **Streamlit** for the interactive dashboard

Charts cover listing supply, pricing, room types, property types, guest capacity, ratings, hosts, geography, and review trends.

---

## 🔍 Key Analytical Areas

### Pricing Intelligence

- Mean vs median listing price
- City-level price patterns
- Room-type pricing
- Property-type pricing
- Guest capacity vs price
- Price per accommodated guest

### Host Analysis

- Superhost distribution
- Rating comparison
- Response and acceptance rates
- Host listing concentration

### Reviews & Ratings

- Overall rating distribution
- Ratings by market and listing segment
- Review activity over time
- Reviews per listing

### Location Analysis

- Listing concentration by city
- Neighbourhood-level patterns where appropriate
- Geographic distribution using latitude and longitude

---

## 💡 Business Insights

The project focuses on **descriptive and evidence-based insights**.

Examples of questions addressed include:

- Which markets contain the largest listing supply?
- Which listing categories dominate the marketplace?
- Where are higher advertised prices observed?
- How does price per accommodated guest change with listing capacity?
- What descriptive differences exist between Superhosts and other hosts?
- When did review activity reach its highest observed level?

No causal conclusions are made from observational relationships.

---

## 🚀 How to Run

### Prerequisites

- Python 3.10+
- Jupyter Notebook / JupyterLab
- Streamlit

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Keep the dataset files locally

Place these files in the project root, alongside `app.py` and the notebook:

```text
Listings.csv
Reviews.csv
```

The datasets are intentionally **not included in the GitHub repository** because of their large file sizes.

### 3. Run the Jupyter Notebook

Open:

```text
DeepanshuGautam_AirbnbMarketPricingIntelligence.ipynb
```

Run the cells from top to bottom.

### 4. Run the Streamlit dashboard

```bash
streamlit run app.py
```

The dashboard will normally open at:

```text
http://localhost:8501
```

---

## 🗂️ Project Structure

```text
Airbnb-Market-Pricing-Intelligence/
│
├── app.py
├── DeepanshuGautam_AirbnbMarketPricingIntelligence.ipynb
├── README.md
├── BUSINESS_RECOMMENDATIONS.md
├── requirements.txt
├── .gitignore
│
└── airbnb_dashboard/
    └── utils/
        ├── __init__.py
        ├── data_loader.py
        ├── analytics.py
        └── charts.py
```

> `Listings.csv` and `Reviews.csv` are kept locally and excluded from GitHub through `.gitignore`.

---

## ⚙️ Performance Considerations

The reviews dataset contains more than 5 million records.

To keep analysis practical:

- Only required review columns are loaded for review analysis.
- Review activity is aggregated rather than repeatedly processing the full dataset.
- Large raw tables are not dumped into notebook outputs.
- Visualizations sample records only where necessary for readability.

---

## ⚠️ Limitations

- No actual booking revenue is available.
- No occupancy data is available.
- Advertised listing price is not the same as realized transaction revenue.
- Review activity does not equal booking activity.
- Some fields contain substantial missing values.
- Cross-city prices are recorded in local currencies and should not be treated as directly equivalent without currency normalization.
- Observational analysis can identify associations and patterns but cannot establish causality.
- The listing dataset represents a snapshot rather than a complete time series of dynamic prices.

---

## 🔮 Future Scope

Potential extensions include:

- Occupancy and booking analysis
- Actual revenue analysis
- Booking conversion analysis
- Dynamic pricing analysis
- Review-text sentiment analysis if review text becomes available
- Time-series forecasting
- Machine Learning as a separate future extension

Machine Learning is intentionally **outside the scope of this Data Analytics project**.

---

## 👨‍💻 Author

**Deepanshu Gautam**

IBM SkillsBuild Data Analytics Internship Project

### Project

**Airbnb Market & Pricing Intelligence**


## Copyright & Usage

© 2026 Deepanshu Gautam. All Rights Reserved.

This repository is shared for portfolio, educational, and evaluation purposes.

The code, analysis, visualizations, documentation, and project structure are original work and may not be copied, reproduced, redistributed, or submitted as another person's project without explicit permission from the author.