"""
Analytics and metrics computation for the Airbnb Market & Revenue Intelligence dashboard.

All functions receive a pre-filtered DataFrame so computation is done once per filter change.
"""

import pandas as pd
import numpy as np


# ── KPI / Overview ────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return top-level KPIs from the filtered listings DataFrame."""
    total_listings    = len(df)
    avg_price         = float(df["price"].mean()) if total_listings else 0.0
    median_price      = float(df["price"].median()) if total_listings else 0.0
    rated             = df["review_scores_rating"].dropna()
    avg_rating        = float(rated.mean()) if len(rated) else None
    pct_rated         = float(len(rated) / total_listings * 100) if total_listings else 0.0
    total_hosts       = int(df["host_id"].nunique())
    superhost_count   = int(df["host_is_superhost"].sum()) if "host_is_superhost" in df else 0
    pct_superhost     = float(superhost_count / total_listings * 100) if total_listings else 0.0
    instant_bookable  = int(df["instant_bookable"].sum()) if "instant_bookable" in df else 0
    pct_instant       = float(instant_bookable / total_listings * 100) if total_listings else 0.0
    cities_count      = int(df["city"].nunique())
    neighbourhoods    = int(df["neighbourhood"].nunique())

    return {
        "total_listings":      total_listings,
        "avg_price":           round(avg_price, 2),
        "median_price":        round(median_price, 2),
        "avg_rating":          round(avg_rating, 1) if avg_rating is not None else None,
        "pct_rated":           round(pct_rated, 1),
        "total_hosts":         total_hosts,
        "pct_superhost":       round(pct_superhost, 1),
        "pct_instant":         round(pct_instant, 1),
        "cities_count":        cities_count,
        "neighbourhoods":      neighbourhoods,
    }


# ── Room & Property Distribution ─────────────────────────────────────────────

def room_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    ct = df["room_type"].value_counts().reset_index()
    ct.columns = ["room_type", "count"]
    ct["pct"] = (ct["count"] / ct["count"].sum() * 100).round(1)
    return ct


def property_type_distribution(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    ct = df["property_type"].value_counts().head(top_n).reset_index()
    ct.columns = ["property_type", "count"]
    ct["pct"] = (ct["count"] / df["property_type"].count() * 100).round(1)
    return ct


def property_group_distribution(df: pd.DataFrame) -> pd.DataFrame:
    ct = df["property_type_group"].value_counts().reset_index()
    ct.columns = ["property_type_group", "count"]
    ct["pct"] = (ct["count"] / ct["count"].sum() * 100).round(1)
    return ct


# ── Pricing Analysis ──────────────────────────────────────────────────────────

def price_by_city(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("city", observed=True)["price"]
          .agg(avg_price="mean", median_price="median", count="count")
          .reset_index()
    )
    g["avg_price"]    = g["avg_price"].round(2)
    g["median_price"] = g["median_price"].round(2)
    return g.sort_values("median_price", ascending=False)


def price_by_room_type(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("room_type", observed=True)["price"]
          .agg(avg_price="mean", median_price="median", count="count")
          .reset_index()
    )
    g["avg_price"]    = g["avg_price"].round(2)
    g["median_price"] = g["median_price"].round(2)
    return g.sort_values("median_price", ascending=False)


def price_by_property_group(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("property_type_group", observed=True)["price"]
          .agg(avg_price="mean", median_price="median", count="count")
          .reset_index()
    )
    g["avg_price"]    = g["avg_price"].round(2)
    g["median_price"] = g["median_price"].round(2)
    return g.sort_values("median_price", ascending=False)


def price_by_accommodates(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df[df["accommodates"] <= 12]
          .groupby("accommodates", observed=True)["price"]
          .agg(avg_price="mean", median_price="median", count="count")
          .reset_index()
    )
    g["avg_price"]    = g["avg_price"].round(2)
    g["median_price"] = g["median_price"].round(2)
    return g.sort_values("accommodates")


def price_by_neighbourhood(df: pd.DataFrame, city: str, top_n: int = 20) -> pd.DataFrame:
    subset = df[df["city"] == city] if city else df
    g = (
        subset.groupby("neighbourhood", observed=True)["price"]
              .agg(avg_price="mean", median_price="median", count="count")
              .reset_index()
    )
    g = g[g["count"] >= 10]  # only neighbourhoods with enough data
    g["avg_price"]    = g["avg_price"].round(2)
    g["median_price"] = g["median_price"].round(2)
    return g.sort_values("median_price", ascending=False).head(top_n)


def price_distribution_data(df: pd.DataFrame, bins: int = 60) -> pd.DataFrame:
    """Return histogram-ready data for price distribution."""
    prices = df["price"].dropna()
    p95 = prices.quantile(0.95)
    prices = prices[prices <= p95]
    counts, edges = np.histogram(prices, bins=bins)
    midpoints = (edges[:-1] + edges[1:]) / 2
    return pd.DataFrame({"price": midpoints.round(0), "count": counts})


# ── Location / Geo Analysis ───────────────────────────────────────────────────

def geo_sample(df: pd.DataFrame, max_points: int = 8000) -> pd.DataFrame:
    """Return a representative sample for map rendering."""
    cols = ["listing_id", "latitude", "longitude", "price", "room_type",
            "neighbourhood", "city", "review_scores_rating"]
    subset = df[cols].dropna(subset=["latitude", "longitude"])
    if len(subset) > max_points:
        subset = subset.sample(max_points, random_state=42)
    return subset


def neighbourhood_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-neighbourhood aggregated stats (within filtered data)."""
    g = (
        df.groupby(["city", "neighbourhood"], observed=True)
          .agg(
              listing_count=("listing_id", "count"),
              avg_price=("price", "mean"),
              median_price=("price", "median"),
              avg_rating=("review_scores_rating", "mean"),
          )
          .reset_index()
    )
    g["avg_price"]    = g["avg_price"].round(2)
    g["median_price"] = g["median_price"].round(2)
    g["avg_rating"]   = g["avg_rating"].round(1)
    return g.sort_values("listing_count", ascending=False)


# ── Host Analysis ─────────────────────────────────────────────────────────────

def host_overview(df: pd.DataFrame) -> dict:
    verified  = df["host_identity_verified"].sum()
    pic       = df["host_has_profile_pic"].sum()
    total     = len(df)
    multi_listing = df[df["host_total_listings_count"] > 1]

    return {
        "pct_identity_verified": round(float(verified) / total * 100, 1) if total else 0,
        "pct_has_profile_pic":   round(float(pic)      / total * 100, 1) if total else 0,
        "pct_multi_listing_hosts": round(len(multi_listing) / total * 100, 1) if total else 0,
        "avg_host_listings":     round(float(df["host_total_listings_count"].dropna().mean()), 1),
    }


def superhost_vs_regular(df: pd.DataFrame) -> pd.DataFrame:
    """Compare key metrics between superhosts and regular hosts."""
    df2 = df.dropna(subset=["host_is_superhost"])
    df2 = df2.copy()
    df2["host_type"] = df2["host_is_superhost"].map({True: "Superhost", False: "Regular"})
    g = (
        df2.groupby("host_type")
           .agg(
               listing_count=("listing_id", "count"),
               avg_price=("price", "mean"),
               avg_rating=("review_scores_rating", "mean"),
               avg_response_rate=("host_response_rate", "mean"),
               avg_acceptance_rate=("host_acceptance_rate", "mean"),
           )
           .reset_index()
    )
    g["avg_price"]           = g["avg_price"].round(2)
    g["avg_rating"]          = g["avg_rating"].round(1)
    g["avg_response_rate"]   = g["avg_response_rate"].round(1)
    g["avg_acceptance_rate"] = g["avg_acceptance_rate"].round(1)
    return g


def top_hosts_by_listings(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    g = (
        df.groupby("host_id")
          .agg(
              listing_count=("listing_id", "count"),
              avg_price=("price", "mean"),
              avg_rating=("review_scores_rating", "mean"),
              is_superhost=("host_is_superhost", "first"),
          )
          .reset_index()
    )
    g["avg_price"]  = g["avg_price"].round(2)
    g["avg_rating"] = g["avg_rating"].round(1)
    return g.sort_values("listing_count", ascending=False).head(top_n)


def host_since_distribution(df: pd.DataFrame) -> pd.DataFrame:
    ct = (
        df.dropna(subset=["host_since_year"])
          .groupby("host_since_year")
          .size()
          .reset_index(name="new_hosts")
    )
    ct["host_since_year"] = ct["host_since_year"].astype(int)
    return ct.sort_values("host_since_year")


def response_time_distribution(df: pd.DataFrame) -> pd.DataFrame:
    ct = df["host_response_time"].dropna().value_counts().reset_index()
    ct.columns = ["response_time", "count"]
    return ct


# ── Review Score Analysis ─────────────────────────────────────────────────────

SCORE_COLS = [
    "review_scores_accuracy",
    "review_scores_cleanliness",
    "review_scores_checkin",
    "review_scores_communication",
    "review_scores_location",
    "review_scores_value",
]
SCORE_LABELS = {
    "review_scores_accuracy":      "Accuracy",
    "review_scores_cleanliness":   "Cleanliness",
    "review_scores_checkin":       "Check-in",
    "review_scores_communication": "Communication",
    "review_scores_location":      "Location",
    "review_scores_value":         "Value",
}


def avg_scores_overall(df: pd.DataFrame) -> pd.DataFrame:
    avgs = {SCORE_LABELS[c]: round(float(df[c].mean()), 2) for c in SCORE_COLS if c in df.columns}
    return pd.DataFrame(list(avgs.items()), columns=["category", "avg_score"])


def avg_scores_by_city(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["city"] + [c for c in SCORE_COLS if c in df.columns]
    g = df[cols].groupby("city", observed=True).mean().reset_index()
    g = g.rename(columns=SCORE_LABELS)
    for col in SCORE_LABELS.values():
        if col in g.columns:
            g[col] = g[col].round(2)
    return g


def rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Histogram buckets for review_scores_rating (0-100)."""
    rated = df["review_scores_rating"].dropna()
    bins  = list(range(60, 101, 5))
    labels = [f"{b}-{b+4}" for b in bins[:-1]]
    cut = pd.cut(rated, bins=bins, labels=labels, right=True, include_lowest=True)
    ct  = cut.value_counts().sort_index().reset_index()
    ct.columns = ["rating_range", "count"]
    return ct


# ── Reviews Over Time (from aggregated reviews table) ────────────────────────

def reviews_yearly(monthly_reviews: pd.DataFrame) -> pd.DataFrame:
    g = (
        monthly_reviews.groupby("year")["review_count"]
                       .sum()
                       .reset_index()
    )
    return g.sort_values("year")


def reviews_monthly_trend(monthly_reviews: pd.DataFrame) -> pd.DataFrame:
    return monthly_reviews.sort_values("period")


def listings_with_review_counts(
    df: pd.DataFrame,
    listing_review_counts: pd.DataFrame,
) -> pd.DataFrame:
    """Merge per-listing review counts back into filtered listings."""
    merged = df.merge(listing_review_counts, on="listing_id", how="left")
    merged["review_count"] = merged["review_count"].fillna(0).astype("int32")
    return merged


def top_reviewed_listings(
    df_with_counts: pd.DataFrame,
    top_n: int = 20,
) -> pd.DataFrame:
    cols = ["listing_id", "name", "city", "neighbourhood",
            "room_type", "price", "review_count", "review_scores_rating"]
    g = (
        df_with_counts[cols]
        .sort_values("review_count", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return g
