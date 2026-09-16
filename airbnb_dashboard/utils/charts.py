"""
Plotly chart factory for the Airbnb Market & Revenue Intelligence dashboard.

Each function returns a go.Figure ready to pass to st.plotly_chart().
Colour palette keeps a consistent professional look throughout the app.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Design tokens ─────────────────────────────────────────────────────────────
PRIMARY    = "#FF5A5F"   # Airbnb red
SECONDARY  = "#00A699"   # Airbnb teal
ACCENT     = "#FC642D"   # Airbnb orange
NEUTRAL    = "#484848"   # dark grey
LIGHT_BG   = "#F7F8FA"

CITY_COLORS = px.colors.qualitative.Pastel
ROOM_PALETTE = {
    "Entire place":  PRIMARY,
    "Private room":  SECONDARY,
    "Hotel room":    ACCENT,
    "Shared room":   "#767676",
}

LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=NEUTRAL),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
)


def _apply_defaults(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(title=dict(text=title, font_size=15, x=0.0), **LAYOUT_DEFAULTS)
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB")
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB", linecolor="#E5E7EB")
    return fig


# ── Room type pie ─────────────────────────────────────────────────────────────

def room_type_pie(room_df: pd.DataFrame) -> go.Figure:
    colors = [ROOM_PALETTE.get(rt, NEUTRAL) for rt in room_df["room_type"]]
    fig = go.Figure(go.Pie(
        labels=room_df["room_type"],
        values=room_df["count"],
        marker_colors=colors,
        hole=0.42,
        textinfo="percent+label",
        textfont_size=12,
        hovertemplate="%{label}<br>%{value:,} listings (%{percent})<extra></extra>",
    ))
    _apply_defaults(fig, "Room Type Distribution")
    fig.update_layout(showlegend=False)
    return fig


# ── Property type bar ─────────────────────────────────────────────────────────

def property_type_bar(prop_df: pd.DataFrame) -> go.Figure:
    prop_df = prop_df.sort_values("count")
    fig = go.Figure(go.Bar(
        x=prop_df["count"],
        y=prop_df["property_type"],
        orientation="h",
        marker_color=PRIMARY,
        text=prop_df["count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        hovertemplate="%{y}<br>%{x:,} listings<extra></extra>",
    ))
    _apply_defaults(fig, "Top Property Types")
    fig.update_layout(height=420)
    return fig


# ── Price by city bar ─────────────────────────────────────────────────────────

def price_by_city_bar(price_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Median Price",
        x=price_df["city"],
        y=price_df["median_price"],
        marker_color=PRIMARY,
        hovertemplate="%{x}<br>Median: %{y:.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Avg Price",
        x=price_df["city"],
        y=price_df["avg_price"],
        marker_color=SECONDARY,
        opacity=0.75,
        hovertemplate="%{x}<br>Average: %{y:.0f}<extra></extra>",
    ))
    fig.update_layout(barmode="group")
    _apply_defaults(fig, "Price by City (local currency)")
    fig.update_yaxes(title_text="Price")
    return fig


# ── Price by room type bar ────────────────────────────────────────────────────

def price_by_room_type_bar(price_df: pd.DataFrame) -> go.Figure:
    colors = [ROOM_PALETTE.get(rt, NEUTRAL) for rt in price_df["room_type"]]
    fig = go.Figure(go.Bar(
        x=price_df["room_type"],
        y=price_df["median_price"],
        marker_color=colors,
        text=price_df["median_price"].apply(lambda v: f"{v:.0f}"),
        textposition="outside",
        hovertemplate="%{x}<br>Median price: %{y:.0f}<extra></extra>",
    ))
    _apply_defaults(fig, "Median Price by Room Type")
    fig.update_yaxes(title_text="Median Price")
    return fig


# ── Price by accommodates line ────────────────────────────────────────────────

def price_by_accommodates_line(acc_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=acc_df["accommodates"],
        y=acc_df["avg_price"],
        mode="lines+markers",
        name="Avg Price",
        line=dict(color=PRIMARY, width=2),
        marker=dict(size=7),
        hovertemplate="Accommodates %{x}<br>Avg Price: %{y:.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=acc_df["accommodates"],
        y=acc_df["median_price"],
        mode="lines+markers",
        name="Median Price",
        line=dict(color=SECONDARY, width=2, dash="dash"),
        marker=dict(size=7),
        hovertemplate="Accommodates %{x}<br>Median Price: %{y:.0f}<extra></extra>",
    ))
    _apply_defaults(fig, "Price vs Capacity (Guests)")
    fig.update_xaxes(title_text="Number of Guests", dtick=1)
    fig.update_yaxes(title_text="Price")
    return fig


# ── Price distribution histogram ─────────────────────────────────────────────

def price_histogram(hist_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=hist_df["price"],
        y=hist_df["count"],
        marker_color=PRIMARY,
        marker_line_width=0,
        hovertemplate="Price ~%{x:.0f}<br>%{y:,} listings<extra></extra>",
    ))
    _apply_defaults(fig, "Price Distribution (up to 95th percentile)")
    fig.update_xaxes(title_text="Price (local currency)")
    fig.update_yaxes(title_text="Number of Listings")
    return fig


# ── Neighbourhood price bar ───────────────────────────────────────────────────

def neighbourhood_price_bar(nbh_df: pd.DataFrame, city: str) -> go.Figure:
    nbh_df = nbh_df.sort_values("median_price", ascending=True).tail(20)
    fig = go.Figure(go.Bar(
        x=nbh_df["median_price"],
        y=nbh_df["neighbourhood"],
        orientation="h",
        marker_color=SECONDARY,
        text=nbh_df["median_price"].apply(lambda v: f"{v:.0f}"),
        textposition="outside",
        hovertemplate="%{y}<br>Median price: %{x:.0f}<extra></extra>",
    ))
    _apply_defaults(fig, f"Median Price by Neighbourhood — {city}")
    fig.update_layout(height=500)
    return fig


# ── Map scatter ───────────────────────────────────────────────────────────────

def geo_scatter(geo_df: pd.DataFrame) -> go.Figure:
    # px.scatter_map is the new API (Plotly >= 5.24); scatter_mapbox is legacy
    has_scatter_map    = hasattr(px, "scatter_map")
    has_scatter_mapbox = hasattr(px, "scatter_mapbox")

    kwargs = dict(
        lat="latitude",
        lon="longitude",
        color="room_type",
        color_discrete_map=ROOM_PALETTE,
        opacity=0.6,
        hover_data={"price": True, "neighbourhood": True,
                    "city": True, "latitude": False, "longitude": False},
        zoom=4,
        height=480,
    )

    if has_scatter_map:
        fig = px.scatter_map(geo_df, map_style="carto-positron", **kwargs)
    else:
        fig = px.scatter_mapbox(geo_df, mapbox_style="carto-positron", **kwargs)

    map_layout = {k: v for k, v in LAYOUT_DEFAULTS.items() if k != "margin"}
    fig.update_layout(
        **map_layout,
        margin=dict(l=0, r=0, t=35, b=0),
        title=dict(text="Listing Locations", font_size=15, x=0.0),
        legend_title_text="Room Type",
    )
    return fig


# ── Review trend line ─────────────────────────────────────────────────────────

def reviews_trend_line(yearly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=yearly_df["year"],
        y=yearly_df["review_count"],
        marker_color=PRIMARY,
        hovertemplate="Year %{x}<br>%{y:,} reviews<extra></extra>",
    ))
    _apply_defaults(fig, "Reviews per Year")
    fig.update_xaxes(title_text="Year", dtick=1)
    fig.update_yaxes(title_text="Review Count")
    return fig


def reviews_monthly_line(monthly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=monthly_df["period"],
        y=monthly_df["review_count"],
        mode="lines",
        line=dict(color=PRIMARY, width=1.5),
        fill="tozeroy",
        fillcolor=f"rgba(255,90,95,0.12)",
        hovertemplate="%{x}<br>%{y:,} reviews<extra></extra>",
    ))
    _apply_defaults(fig, "Monthly Review Volume (2008–2021)")
    fig.update_xaxes(title_text="Month", nticks=20)
    fig.update_yaxes(title_text="Reviews")
    return fig


# ── Review score radar ────────────────────────────────────────────────────────

def score_radar(scores_df: pd.DataFrame) -> go.Figure:
    categories = scores_df["category"].tolist()
    values     = scores_df["avg_score"].tolist()
    # Close the polygon
    categories += [categories[0]]
    values     += [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor=f"rgba(255,90,95,0.18)",
        line=dict(color=PRIMARY, width=2),
        hovertemplate="%{theta}<br>Avg: %{r:.2f}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[8, 10], gridcolor="#E5E7EB"),
            angularaxis=dict(gridcolor="#E5E7EB"),
        ),
        **LAYOUT_DEFAULTS,
        title=dict(text="Average Sub-scores (out of 10)", font_size=15, x=0.0),
        showlegend=False,
    )
    return fig


# ── Rating distribution bar ───────────────────────────────────────────────────

def rating_dist_bar(rating_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=rating_df["rating_range"],
        y=rating_df["count"],
        marker_color=SECONDARY,
        text=rating_df["count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        hovertemplate="Rating %{x}<br>%{y:,} listings<extra></extra>",
    ))
    _apply_defaults(fig, "Overall Rating Distribution (out of 100)")
    fig.update_xaxes(title_text="Rating Range")
    fig.update_yaxes(title_text="Number of Listings")
    return fig


# ── Superhost comparison bar ──────────────────────────────────────────────────

def superhost_comparison(sh_df: pd.DataFrame) -> go.Figure:
    metrics = ["avg_price", "avg_rating", "avg_response_rate", "avg_acceptance_rate"]
    labels  = ["Avg Price", "Avg Rating", "Response Rate (%)", "Acceptance Rate (%)"]

    fig = make_subplots(
        rows=1, cols=len(metrics),
        subplot_titles=labels,
    )
    colors = {
        "Superhost": PRIMARY,
        "Regular":   SECONDARY,
    }
    for i, (metric, label) in enumerate(zip(metrics, labels), start=1):
        for _, row in sh_df.iterrows():
            fig.add_trace(go.Bar(
                name=str(row["host_type"]),
                x=[str(row["host_type"])],
                y=[row[metric]],
                marker_color=colors.get(str(row["host_type"]), NEUTRAL),
                showlegend=(i == 1),
                hovertemplate=f"{label}: %{{y:.1f}}<extra></extra>",
            ), row=1, col=i)

    fig.update_layout(
        barmode="group",
        **LAYOUT_DEFAULTS,
        title=dict(text="Superhost vs Regular Host — Key Metrics", font_size=15, x=0.0),
        height=340,
    )
    return fig


# ── Host growth bar ───────────────────────────────────────────────────────────

def host_growth_bar(growth_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=growth_df["host_since_year"],
        y=growth_df["new_hosts"],
        marker_color=ACCENT,
        hovertemplate="Year %{x}<br>%{y:,} new hosts<extra></extra>",
    ))
    _apply_defaults(fig, "New Hosts Joined per Year")
    fig.update_xaxes(title_text="Year", dtick=1)
    fig.update_yaxes(title_text="New Hosts")
    return fig


# ── Neighbourhood listing count ───────────────────────────────────────────────

def neighbourhood_listing_bar(nbh_df: pd.DataFrame, city: str, top_n: int = 20) -> go.Figure:
    nbh_df = nbh_df[nbh_df["city"] == city].sort_values("listing_count", ascending=True).tail(top_n)
    fig = go.Figure(go.Bar(
        x=nbh_df["listing_count"],
        y=nbh_df["neighbourhood"],
        orientation="h",
        marker_color=PRIMARY,
        text=nbh_df["listing_count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        hovertemplate="%{y}<br>%{x:,} listings<extra></extra>",
    ))
    _apply_defaults(fig, f"Listings by Neighbourhood — {city}")
    fig.update_layout(height=500)
    return fig


# ── Scores by city heatmap ────────────────────────────────────────────────────

def scores_by_city_heatmap(scores_df: pd.DataFrame) -> go.Figure:
    score_cols = ["Accuracy", "Cleanliness", "Check-in",
                  "Communication", "Location", "Value"]
    available  = [c for c in score_cols if c in scores_df.columns]
    z_vals     = scores_df[available].values
    cities     = scores_df["city"].astype(str).tolist()

    fig = go.Figure(go.Heatmap(
        z=z_vals,
        x=available,
        y=cities,
        colorscale=[[0, "#FFF5F5"], [0.5, PRIMARY], [1, "#7F0000"]],
        zmin=8, zmax=10,
        text=[[f"{v:.2f}" for v in row] for row in z_vals],
        texttemplate="%{text}",
        hovertemplate="%{y} — %{x}<br>Score: %{z:.2f}<extra></extra>",
        colorbar=dict(title="Score"),
    ))
    _apply_defaults(fig, "Average Review Sub-scores by City")
    fig.update_layout(height=400)
    return fig


# ── Price by property group ───────────────────────────────────────────────────

def price_by_property_group_bar(pg_df: pd.DataFrame) -> go.Figure:
    pg_df = pg_df.sort_values("median_price", ascending=True)
    fig = go.Figure(go.Bar(
        x=pg_df["median_price"],
        y=pg_df["property_type_group"],
        orientation="h",
        marker_color=ACCENT,
        text=pg_df["median_price"].apply(lambda v: f"{v:.0f}"),
        textposition="outside",
        hovertemplate="%{y}<br>Median price: %{x:.0f}<extra></extra>",
    ))
    _apply_defaults(fig, "Median Price by Property Group")
    return fig
