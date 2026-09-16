"""
Airbnb Market & Pricing Intelligence — Streamlit Dashboard
==========================================================
Run with:  streamlit run app.py
"""

import sys
from pathlib import Path

# Allow imports from airbnb_dashboard/utils without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from airbnb_dashboard.utils.data_loader import (
    load_listings,
    load_reviews_aggregated,
    apply_filters,
)
from airbnb_dashboard.utils import analytics as an
from airbnb_dashboard.utils import charts as ch

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airbnb Market & Pricing Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global font */
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

/* KPI cards */
.kpi-card {
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-value { font-size: 28px; font-weight: 700; color: #FF5A5F; margin: 0; }
.kpi-label { font-size: 12px; color: #767676; margin: 4px 0 0 0; text-transform: uppercase; letter-spacing: 0.05em; }

/* Section header */
.section-header {
    font-size: 20px; font-weight: 600; color: #484848;
    border-left: 4px solid #FF5A5F;
    padding-left: 10px; margin: 24px 0 12px 0;
}

/* Insight box */
.insight-box {
    background: #FFF8F8;
    border-left: 3px solid #FF5A5F;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 13px;
    color: #484848;
    line-height: 1.6;
}

/* Sidebar */
section[data-testid="stSidebar"] { background: #FAFAFA; }

/* Tab styling */
button[data-baseweb="tab"] { font-size: 14px; }

/* Remove default streamlit padding on top */
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, col) -> None:
    col.markdown(
        f'<div class="kpi-card"><p class="kpi-value">{value}</p>'
        f'<p class="kpi-label">{label}</p></div>',
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def insight(text: str) -> None:
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)


def fmt_price(v: float) -> str:
    return f"{v:,.0f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_listings():
    return load_listings()


@st.cache_data(show_spinner=False)
def get_reviews():
    return load_reviews_aggregated()


with st.spinner("Loading dataset…"):
    df_raw = get_listings()
    monthly_reviews, listing_review_counts = get_reviews()


# ── Sidebar: filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_B%C3%A9lo.svg",
        width=140,
    )
    st.title("Filters")
    st.caption(f"Dataset: **{len(df_raw):,}** listings across **{df_raw['city'].nunique()}** cities")

    # City
    all_cities = sorted(df_raw["city"].dropna().unique().tolist())
    sel_cities = st.multiselect("City", all_cities, default=all_cities,
                                help="Select one or more cities")

    # Room type
    all_rooms = sorted(df_raw["room_type"].dropna().unique().tolist())
    sel_rooms = st.multiselect("Room Type", all_rooms, default=all_rooms)

    # Property group
    all_groups = sorted(df_raw["property_type_group"].dropna().unique().astype(str).tolist())
    sel_groups = st.multiselect("Property Group", all_groups, default=all_groups)

    # Price range
    p_min = float(df_raw["price"].min())
    p_max = float(df_raw["price"].quantile(0.99))
    price_range = st.slider(
        "Price Range",
        min_value=p_min,
        max_value=p_max,
        value=(p_min, p_max),
        step=10.0,
        format="%.0f",
    )

    # Superhost
    superhost_only = st.checkbox("Superhosts Only", value=False)

    # Min rating
    min_rating = st.slider("Min Overall Rating", 0, 100, 0, step=5,
                           help="Filter listings with rating ≥ selected value (0 = no filter)")

    st.divider()
    st.caption("Airbnb Market & Pricing Intelligence\nIBM SkillBuild Project")


# ── Apply filters ─────────────────────────────────────────────────────────────
df = apply_filters(
    df_raw,
    cities=sel_cities,
    room_types=sel_rooms,
    property_groups=sel_groups,
    price_range=price_range,
    superhost_only=superhost_only,
    min_rating=min_rating,
)

if len(df) == 0:
    st.warning("No listings match the current filters. Please adjust the sidebar filters.")
    st.stop()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "## 🏠 Airbnb Market & Pricing Intelligence",
    unsafe_allow_html=False,
)
st.caption(
    f"Showing **{len(df):,}** listings · "
    f"**{', '.join(sel_cities[:4])}{'…' if len(sel_cities) > 4 else ''}**"
)

st.divider()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Overview",
    "🗺️ Location",
    "💰 Pricing",
    "🏡 Property & Room",
    "👤 Hosts",
    "⭐ Reviews",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    kpis = an.compute_kpis(df)

    # KPI row 1
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card("Total Listings",       f"{kpis['total_listings']:,}",  c1)
    kpi_card("Cities",               str(kpis['cities_count']),       c2)
    kpi_card("Unique Hosts",         f"{kpis['total_hosts']:,}",      c3)
    kpi_card("Neighbourhoods",       str(kpis['neighbourhoods']),     c4)
    kpi_card("Avg Price",            fmt_price(kpis['avg_price']),    c5)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI row 2
    c6, c7, c8, c9, c10 = st.columns(5)
    kpi_card("Median Price",         fmt_price(kpis['median_price']),  c6)
    avg_r = f"{kpis['avg_rating']}" if kpis['avg_rating'] else "N/A"
    kpi_card("Avg Rating (out of 100)", avg_r,                          c7)
    kpi_card("% Listings Rated",     fmt_pct(kpis['pct_rated']),       c8)
    kpi_card("% Superhosts",         fmt_pct(kpis['pct_superhost']),   c9)
    kpi_card("% Instant Bookable",   fmt_pct(kpis['pct_instant']),     c10)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Distribution at a Glance")

    col_room, col_prop = st.columns([1, 1.6])
    with col_room:
        room_df = an.room_type_distribution(df)
        st.plotly_chart(ch.room_type_pie(room_df), use_container_width=True, key="overview_room_type_pie")
    with col_prop:
        prop_df = an.property_type_distribution(df, top_n=12)
        st.plotly_chart(ch.property_type_bar(prop_df), use_container_width=True, key="overview_property_type_bar")

    section("Business Insights")
    dominant_room = an.room_type_distribution(df).iloc[0]
    pct_dominant  = dominant_room["pct"]
    insight(
        f"**{dominant_room['room_type']}** listings dominate the selection at "
        f"**{pct_dominant}%** of all filtered listings."
    )
    if kpis["avg_rating"] is not None:
        diff = kpis["avg_rating"] - 95
        sign = "above" if diff >= 0 else "below"
        insight(
            f"Average overall rating is **{kpis['avg_rating']}/100**, "
            f"{abs(diff):.1f} points {sign} the 95/100 benchmark. "
            f"Only **{kpis['pct_rated']}%** of listed properties have received ratings."
        )
    insight(
        f"**{kpis['pct_superhost']:.1f}%** of hosts in this selection are Superhosts, and "
        f"**{kpis['pct_instant']:.1f}%** of listings support instant booking."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Location
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    section("Geographic Distribution")
    geo_df = an.geo_sample(df, max_points=8000)
    st.plotly_chart(ch.geo_scatter(geo_df), use_container_width=True, key="location_geo_scatter")

    st.markdown("<br>", unsafe_allow_html=True)
    section("Neighbourhood Deep-Dive")

    available_cities = sorted(df["city"].dropna().unique().tolist())
    selected_city    = st.selectbox("Select a city to explore", available_cities,
                                    key="loc_city_select")

    col_nbh_count, col_nbh_price = st.columns(2)
    nbh_summary = an.neighbourhood_summary(df)

    with col_nbh_count:
        st.plotly_chart(
            ch.neighbourhood_listing_bar(nbh_summary, selected_city),
            use_container_width=True,
            key="location_nbh_listing_bar",
        )
    with col_nbh_price:
        price_nbh = an.price_by_neighbourhood(df, selected_city)
        st.plotly_chart(
            ch.neighbourhood_price_bar(price_nbh, selected_city),
            use_container_width=True,
            key="location_nbh_price_bar",
        )

    section("Neighbourhood Table")
    city_nbh = nbh_summary[nbh_summary["city"] == selected_city].drop(columns="city")
    city_nbh = city_nbh.rename(columns={
        "neighbourhood": "Neighbourhood",
        "listing_count": "Listings",
        "avg_price": "Avg Price",
        "median_price": "Median Price",
        "avg_rating": "Avg Rating",
    })
    st.dataframe(
        city_nbh.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    section("Business Insights")
    top_nbh = nbh_summary[nbh_summary["city"] == selected_city].iloc[0] if len(nbh_summary[nbh_summary["city"] == selected_city]) else None
    if top_nbh is not None:
        insight(
            f"In **{selected_city}**, the neighbourhood **{top_nbh['neighbourhood']}** has "
            f"the most listings (**{top_nbh['listing_count']:,}**) with a median price of "
            f"**{top_nbh['median_price']:,.0f}**."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Pricing
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    section("Price Overview")

    col_hist, col_room_price = st.columns(2)
    with col_hist:
        hist_df = an.price_distribution_data(df)
        st.plotly_chart(ch.price_histogram(hist_df), use_container_width=True, key="pricing_histogram")
    with col_room_price:
        room_price_df = an.price_by_room_type(df)
        st.plotly_chart(ch.price_by_room_type_bar(room_price_df), use_container_width=True, key="pricing_room_type_bar")

    section("Price by City")
    city_price_df = an.price_by_city(df)
    st.plotly_chart(ch.price_by_city_bar(city_price_df), use_container_width=True, key="pricing_city_bar")

    section("Price by Property Group & Capacity")
    col_pg, col_acc = st.columns(2)
    with col_pg:
        pg_price = an.price_by_property_group(df)
        st.plotly_chart(ch.price_by_property_group_bar(pg_price), use_container_width=True, key="pricing_property_group_bar")
    with col_acc:
        acc_df = an.price_by_accommodates(df)
        st.plotly_chart(ch.price_by_accommodates_line(acc_df), use_container_width=True, key="pricing_accommodates_line")

    section("Business Insights")
    if len(city_price_df) > 1:
        most_exp  = city_price_df.iloc[0]
        least_exp = city_price_df.iloc[-1]
        insight(
            f"**{most_exp['city']}** is the most expensive city with a median price of "
            f"**{most_exp['median_price']:,.0f}**, while **{least_exp['city']}** is the "
            f"most affordable at **{least_exp['median_price']:,.0f}** (local currencies)."
        )

    max_room = room_price_df.iloc[0]
    min_room = room_price_df.iloc[-1]
    insight(
        f"**{max_room['room_type']}** commands the highest median price at "
        f"**{max_room['median_price']:,.0f}**, while **{min_room['room_type']}** is the "
        f"most budget-friendly at **{min_room['median_price']:,.0f}**."
    )

    if len(acc_df) >= 2:
        price_diff = acc_df.iloc[-1]["avg_price"] - acc_df.iloc[0]["avg_price"]
        insight(
            f"Price increases with capacity — listings for the largest groups cost on average "
            f"**{price_diff:,.0f}** more than single-guest listings."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Property & Room
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    section("Property Type Breakdown")
    col_pg2, col_pt2 = st.columns(2)
    with col_pg2:
        group_df = an.property_group_distribution(df)
        fig_group = ch.room_type_pie(
            group_df.rename(columns={"property_type_group": "room_type"})
        )
        fig_group.update_layout(title_text="Property Group Distribution")
        st.plotly_chart(fig_group, use_container_width=True, key="property_group_pie")
    with col_pt2:
        prop12 = an.property_type_distribution(df, top_n=12)
        st.plotly_chart(ch.property_type_bar(prop12), use_container_width=True, key="property_type_bar2")

    section("Room Type vs Price & Rating")
    col_rt1, col_rt2 = st.columns(2)
    with col_rt1:
        rt_price = an.price_by_room_type(df)
        st.plotly_chart(ch.price_by_room_type_bar(rt_price), use_container_width=True, key="property_room_price_bar")
    with col_rt2:
        # Avg rating by room type
        rt_rating = (
            df.groupby("room_type", observed=True)["review_scores_rating"]
              .mean()
              .reset_index()
              .rename(columns={"review_scores_rating": "avg_rating"})
              .dropna()
        )
        rt_rating["avg_rating"] = rt_rating["avg_rating"].round(1)
        fig_rt_rat = go.Figure(go.Bar(
            x=rt_rating["room_type"].astype(str),
            y=rt_rating["avg_rating"],
            marker_color=ch.SECONDARY,
            text=rt_rating["avg_rating"],
            textposition="outside",
            hovertemplate="%{x}<br>Avg rating: %{y:.1f}<extra></extra>",
        ))
        ch._apply_defaults(fig_rt_rat, "Avg Overall Rating by Room Type")
        fig_rt_rat.update_yaxes(range=[90, 101], title_text="Rating (out of 100)")
        st.plotly_chart(fig_rt_rat, use_container_width=True, key="property_room_rating_bar")

    section("Capacity Distribution")
    cap_dist = (
        df[df["accommodates"] <= 16]["accommodates"]
          .value_counts()
          .sort_index()
          .reset_index()
    )
    cap_dist.columns = ["accommodates", "count"]
    fig_cap = go.Figure(go.Bar(
        x=cap_dist["accommodates"].astype(str),
        y=cap_dist["count"],
        marker_color=ch.ACCENT,
        hovertemplate="Accommodates %{x}<br>%{y:,} listings<extra></extra>",
    ))
    ch._apply_defaults(fig_cap, "Number of Listings by Guest Capacity")
    fig_cap.update_xaxes(title_text="Guests Accommodated")
    fig_cap.update_yaxes(title_text="Listings")
    st.plotly_chart(fig_cap, use_container_width=True, key="property_capacity_bar")

    section("Business Insights")
    top_group = group_df.iloc[0]
    insight(
        f"**{top_group['property_type_group']}** is the dominant property group with "
        f"**{top_group['pct']}%** of listings, reflecting Airbnb's apartment-centric supply."
    )
    cap_mode = cap_dist.loc[cap_dist["count"].idxmax(), "accommodates"]
    insight(
        f"The most common listing capacity is **{cap_mode} guests**, "
        f"typical of urban studio and 1-bedroom apartments."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Hosts
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    section("Host Overview")
    host_ov = an.host_overview(df)
    h1, h2, h3, h4 = st.columns(4)
    kpi_card("% Identity Verified",    fmt_pct(host_ov["pct_identity_verified"]),    h1)
    kpi_card("% Has Profile Pic",      fmt_pct(host_ov["pct_has_profile_pic"]),      h2)
    kpi_card("% Multi-Listing Hosts",  fmt_pct(host_ov["pct_multi_listing_hosts"]), h3)
    kpi_card("Avg Listings / Host",    str(host_ov["avg_host_listings"]),            h4)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Superhost vs Regular Host")
    sh_df = an.superhost_vs_regular(df)
    if len(sh_df) == 2:
        st.plotly_chart(ch.superhost_comparison(sh_df), use_container_width=True, key="hosts_superhost_comparison")
    else:
        st.info("Not enough superhost data in current filter selection.")

    col_grow, col_rt = st.columns(2)
    with col_grow:
        section("Host Growth Over Time")
        growth_df = an.host_since_distribution(df)
        st.plotly_chart(ch.host_growth_bar(growth_df), use_container_width=True, key="hosts_growth_bar")
    with col_rt:
        section("Host Response Time")
        rt_dist = an.response_time_distribution(df)
        if len(rt_dist):
            fig_rt = go.Figure(go.Pie(
                labels=rt_dist["response_time"].astype(str),
                values=rt_dist["count"],
                hole=0.4,
                textinfo="percent+label",
                textfont_size=11,
            ))
            ch._apply_defaults(fig_rt, "Response Time Distribution")
            fig_rt.update_layout(showlegend=False)
            st.plotly_chart(fig_rt, use_container_width=True, key="hosts_response_time_pie")
        else:
            st.info("No response time data available for current selection.")

    section("Top Hosts by Listing Count")
    top_hosts = an.top_hosts_by_listings(df, top_n=15)
    top_hosts["is_superhost"] = top_hosts["is_superhost"].map(
        {True: "✅ Yes", False: "No", None: "—"}
    )
    st.dataframe(
        top_hosts.rename(columns={
            "host_id": "Host ID",
            "listing_count": "Listings",
            "avg_price": "Avg Price",
            "avg_rating": "Avg Rating",
            "is_superhost": "Superhost",
        }),
        use_container_width=True,
        hide_index=True,
    )

    section("Business Insights")
    insight(
        f"**{host_ov['pct_identity_verified']:.0f}%** of hosts have verified identities and "
        f"**{host_ov['pct_has_profile_pic']:.0f}%** have profile pictures — "
        f"key trust signals on the platform."
    )
    insight(
        f"**{host_ov['pct_multi_listing_hosts']:.1f}%** of listings belong to hosts with "
        f"multiple properties, indicating a notable presence of professional/commercial hosts."
    )
    if len(sh_df) == 2:
        sh_row = sh_df[sh_df["host_type"] == "Superhost"].iloc[0]
        reg_row = sh_df[sh_df["host_type"] == "Regular"].iloc[0]
        if pd.notna(sh_row["avg_rating"]) and pd.notna(reg_row["avg_rating"]):
            diff = sh_row["avg_rating"] - reg_row["avg_rating"]
            insight(
                f"Superhosts have an average rating of **{sh_row['avg_rating']:.1f}** vs "
                f"**{reg_row['avg_rating']:.1f}** for regular hosts — "
                f"a difference of **{diff:+.1f} points**."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Reviews
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    section("Review Score Summary")
    scores_df = an.avg_scores_overall(df)
    col_radar, col_heatmap = st.columns([1, 1.8])
    with col_radar:
        if len(scores_df):
            st.plotly_chart(ch.score_radar(scores_df), use_container_width=True, key="reviews_score_radar")
    with col_heatmap:
        scores_city = an.avg_scores_by_city(df)
        if len(scores_city):
            st.plotly_chart(ch.scores_by_city_heatmap(scores_city), use_container_width=True, key="reviews_scores_heatmap")

    section("Rating Distribution")
    rating_df = an.rating_distribution(df)
    st.plotly_chart(ch.rating_dist_bar(rating_df), use_container_width=True, key="reviews_rating_dist")

    section("Review Activity Over Time")
    yearly_df  = an.reviews_yearly(monthly_reviews)
    monthly_df = an.reviews_monthly_trend(monthly_reviews)
    col_yr, col_mo = st.columns(2)
    with col_yr:
        st.plotly_chart(ch.reviews_trend_line(yearly_df), use_container_width=True, key="reviews_yearly_bar")
    with col_mo:
        st.plotly_chart(ch.reviews_monthly_line(monthly_df), use_container_width=True, key="reviews_monthly_line")

    section("Most-Reviewed Listings (Filtered Selection)")
    df_with_rev = an.listings_with_review_counts(df, listing_review_counts)
    top_reviewed = an.top_reviewed_listings(df_with_rev, top_n=20)
    st.dataframe(
        top_reviewed.rename(columns={
            "listing_id": "ID",
            "name": "Name",
            "city": "City",
            "neighbourhood": "Neighbourhood",
            "room_type": "Room Type",
            "price": "Price",
            "review_count": "# Reviews",
            "review_scores_rating": "Rating",
        }),
        use_container_width=True,
        hide_index=True,
    )

    section("Business Insights")
    top_score = scores_df.sort_values("avg_score", ascending=False).iloc[0] if len(scores_df) else None
    low_score = scores_df.sort_values("avg_score").iloc[0] if len(scores_df) else None
    if top_score is not None:
        insight(
            f"**{top_score['category']}** is the highest-rated dimension at "
            f"**{top_score['avg_score']:.2f}/10**, while **{low_score['category']}** "
            f"scores the lowest at **{low_score['avg_score']:.2f}/10** — "
            f"the area with the most room for improvement."
        )
    total_reviews = int(monthly_reviews["review_count"].sum())
    peak_year = int(yearly_df.loc[yearly_df["review_count"].idxmax(), "year"])
    peak_count = int(yearly_df["review_count"].max())
    insight(
        f"The dataset contains **{total_reviews:,}** total reviews spanning 2008–2021. "
        f"Peak review activity was in **{peak_year}** with **{peak_count:,}** reviews, "
        f"reflecting Airbnb's rapid pre-pandemic growth."
    )

    covid_2020 = int(yearly_df[yearly_df["year"] == 2020]["review_count"].sum()) if 2020 in yearly_df["year"].values else 0
    covid_2019 = int(yearly_df[yearly_df["year"] == 2019]["review_count"].sum()) if 2019 in yearly_df["year"].values else 0
    if covid_2019 and covid_2020:
        drop_pct = (covid_2019 - covid_2020) / covid_2019 * 100
        insight(
            f"Review volume dropped **{drop_pct:.0f}%** from 2019 to 2020 — a clear signal "
            f"of the COVID-19 pandemic's impact on Airbnb booking activity globally."
        )
