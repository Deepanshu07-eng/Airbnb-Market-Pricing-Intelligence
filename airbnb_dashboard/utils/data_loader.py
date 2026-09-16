"""
Data loading and cleaning utilities for the Airbnb Market & Pricing Intelligence dashboard.

Designed for memory efficiency:
- Listings are cached once after cleaning (via st.cache_data).
- Reviews are aggregated at load time so the raw 5M+ row table is never kept in memory.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent.parent  # workspace root

LISTINGS_PATH = _DATA_DIR / "Listings.csv"
REVIEWS_PATH  = _DATA_DIR / "Reviews.csv"

# ── Listings ─────────────────────────────────────────────────────────────────
LISTINGS_DTYPES = {
    "listing_id":               "int32",
    "host_id":                  "int32",
    "accommodates":             "int8",
    "price":                    "float32",
    "minimum_nights":           "int16",
    "maximum_nights":           "int32",
    "review_scores_rating":     "float32",
    "review_scores_accuracy":   "float32",
    "review_scores_cleanliness":"float32",
    "review_scores_checkin":    "float32",
    "review_scores_communication":"float32",
    "review_scores_location":   "float32",
    "review_scores_value":      "float32",
    "host_total_listings_count":"float32",
    "latitude":                 "float32",
    "longitude":                "float32",
}

LISTINGS_USECOLS = [
    "listing_id", "name", "host_id", "host_since",
    "host_response_time", "host_response_rate", "host_acceptance_rate",
    "host_is_superhost", "host_total_listings_count",
    "host_has_profile_pic", "host_identity_verified",
    "neighbourhood", "city", "latitude", "longitude",
    "property_type", "room_type", "accommodates", "bedrooms",
    "price", "minimum_nights", "maximum_nights",
    "review_scores_rating", "review_scores_accuracy",
    "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location",
    "review_scores_value", "instant_bookable",
]


@st.cache_data(show_spinner="Loading listings data…")
def load_listings() -> pd.DataFrame:
    """Load, clean, and return the listings DataFrame (cached)."""
    df = pd.read_csv(
        LISTINGS_PATH,
        encoding="latin-1",
        usecols=LISTINGS_USECOLS,
        dtype={k: v for k, v in LISTINGS_DTYPES.items() if k in LISTINGS_USECOLS},
        low_memory=False,
    )

    # ── Boolean columns ───────────────────────────────────────────────────────
    for col in ["host_is_superhost", "host_has_profile_pic",
                "host_identity_verified", "instant_bookable"]:
        df[col] = df[col].map({"t": True, "f": False})

    # ── Dates ─────────────────────────────────────────────────────────────────
    df["host_since"] = pd.to_datetime(df["host_since"], errors="coerce")
    df["host_since_year"] = df["host_since"].dt.year.astype("Int16")

    # ── Numeric coercion (bedrooms may have mixed types) ─────────────────────
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").astype("float32")

    # ── Response rate / acceptance rate (may already be numeric 0-100) ───────
    for col in ["host_response_rate", "host_acceptance_rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    # ── Price: drop zero/outlier prices (> 99.9th percentile) ────────────────
    df = df[df["price"] > 0].copy()
    price_cap = df["price"].quantile(0.999)
    df = df[df["price"] <= price_cap].copy()

    # ── Category columns ─────────────────────────────────────────────────────
    for col in ["city", "neighbourhood", "property_type",
                "room_type", "host_response_time"]:
        df[col] = df[col].astype("category")

    # ── Derived columns ───────────────────────────────────────────────────────
    df["price_per_person"] = (df["price"] / df["accommodates"]).astype("float32")

    # Simplify property type for grouping
    df["property_type_group"] = df["property_type"].astype(str).apply(_simplify_property_type).astype("category")

    return df.reset_index(drop=True)


def _simplify_property_type(pt: str) -> str:
    pt_lower = pt.lower()
    if "apartment" in pt_lower or "condo" in pt_lower or "loft" in pt_lower:
        return "Apartment / Condo / Loft"
    if "house" in pt_lower or "villa" in pt_lower or "townhouse" in pt_lower or "cottage" in pt_lower:
        return "House / Villa / Townhouse"
    if "hotel" in pt_lower or "aparthotel" in pt_lower or "boutique" in pt_lower:
        return "Hotel / Boutique"
    if "bed and breakfast" in pt_lower or "b&b" in pt_lower or "guesthouse" in pt_lower:
        return "B&B / Guesthouse"
    if "guest suite" in pt_lower or "guest house" in pt_lower:
        return "Guest Suite"
    return "Other"


# ── Reviews (aggregated, memory-efficient) ────────────────────────────────────
@st.cache_data(show_spinner="Loading reviews data…")
def load_reviews_aggregated() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the reviews CSV, keep only listing_id + date, and return two aggregates:

    1. monthly_reviews : DataFrame with columns [year, month, period, review_count]
    2. listing_review_counts : DataFrame with columns [listing_id, review_count]

    The raw 5M+ row table is released from memory after aggregation.
    """
    raw = pd.read_csv(
        REVIEWS_PATH,
        usecols=["listing_id", "date"],
        parse_dates=["date"],
        dtype={"listing_id": "int32"},
    )

    # ── Monthly trend ─────────────────────────────────────────────────────────
    raw["year"]  = raw["date"].dt.year.astype("int16")
    raw["month"] = raw["date"].dt.month.astype("int8")
    raw["period"] = raw["date"].dt.to_period("M").astype(str)

    monthly = (
        raw.groupby("period", observed=True)
           .size()
           .reset_index(name="review_count")
           .sort_values("period")
    )
    monthly["year"]  = monthly["period"].str[:4].astype("int16")
    monthly["month"] = monthly["period"].str[5:7].astype("int8")

    # ── Per-listing review counts ─────────────────────────────────────────────
    listing_counts = (
        raw.groupby("listing_id", observed=True)
           .size()
           .reset_index(name="review_count")
    )
    listing_counts["listing_id"] = listing_counts["listing_id"].astype("int32")

    del raw   # release raw 5M+ row table

    return monthly, listing_counts


# ── Filter helpers ────────────────────────────────────────────────────────────
def apply_filters(
    df: pd.DataFrame,
    cities: list[str],
    room_types: list[str],
    property_groups: list[str],
    price_range: tuple[float, float],
    superhost_only: bool,
    min_rating: float,
) -> pd.DataFrame:
    """Apply sidebar filters to the listings DataFrame."""
    mask = pd.Series(True, index=df.index)

    if cities:
        mask &= df["city"].isin(cities)
    if room_types:
        mask &= df["room_type"].isin(room_types)
    if property_groups:
        mask &= df["property_type_group"].isin(property_groups)

    mask &= (df["price"] >= price_range[0]) & (df["price"] <= price_range[1])

    if superhost_only:
        mask &= df["host_is_superhost"] == True  # noqa: E712

    if min_rating > 0:
        rated = df["review_scores_rating"].notna()
        mask &= rated & (df["review_scores_rating"] >= min_rating)

    return df[mask].copy()
