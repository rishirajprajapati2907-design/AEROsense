"""
AEROsense Analytics Module
Generates time-series trend charts for hourly, daily, and weekly views using Plotly.
Includes statistical summaries and threshold reference bands.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import SENSOR_FIELDS
from thingspeak_client import TelemetryEntry


def entries_to_dataframe(entries: List[TelemetryEntry]) -> pd.DataFrame:
    """Convert list of TelemetryEntry objects into a clean Pandas DataFrame."""
    if not entries:
        cols = ["timestamp", "entry_id"] + list(SENSOR_FIELDS.keys())
        return pd.DataFrame(columns=cols)

    rows = []
    for e in entries:
        row: Dict[str, Any] = {
            "timestamp": e.timestamp,
            "entry_id": e.entry_id,
        }
        for field_id in SENSOR_FIELDS.keys():
            row[field_id] = e.values.get(field_id)
        rows.append(row)

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def filter_dataframe_by_timescale(df: pd.DataFrame, timescale: str = "Daily") -> pd.DataFrame:
    """
    Filter DataFrame based on selected timescale:
    - Hourly: last 60 minutes
    - Daily: last 24 hours
    - Weekly: last 7 days
    - All: full available buffer
    """
    if df.empty:
        return df

    now = df["timestamp"].max()
    if timescale == "Hourly":
        cutoff = now - timedelta(hours=1)
        filtered = df[df["timestamp"] >= cutoff]
        return filtered if not filtered.empty else df.tail(15)
    elif timescale == "Daily":
        cutoff = now - timedelta(hours=24)
        filtered = df[df["timestamp"] >= cutoff]
        return filtered if not filtered.empty else df
    elif timescale == "Weekly":
        cutoff = now - timedelta(days=7)
        filtered = df[df["timestamp"] >= cutoff]
        return filtered if not filtered.empty else df
    return df


def calculate_field_statistics(df: pd.DataFrame, field_id: str) -> Dict[str, Optional[float]]:
    """Calculate summary statistics for a sensor field."""
    if df.empty or field_id not in df.columns or df[field_id].dropna().empty:
        return {
            "current": None,
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "count": 0,
        }

    series = df[field_id].dropna()
    return {
        "current": float(series.iloc[-1]) if not series.empty else None,
        "min": float(series.min()),
        "max": float(series.max()),
        "mean": float(series.mean()),
        "std": float(series.std()) if len(series) > 1 else 0.0,
        "count": int(len(series)),
    }


def create_parameter_chart(
    df: pd.DataFrame,
    field_id: str,
    temp_unit: str = "°C",
) -> go.Figure:
    """
    Create an individual interactive Plotly trend chart for a sensor parameter.
    Includes threshold zones, markers, and dark theme styling.
    """
    cfg = SENSOR_FIELDS.get(field_id, {})
    name = cfg.get("name", field_id)
    unit = temp_unit if field_id == "field1" else cfg.get("default_unit", "")
    color = "#00D2FF"

    # Distinct accent colors for each parameter
    param_colors = {
        "field1": "#F59E0B",  # Orange/amber for Temp
        "field2": "#06B6D4",  # Cyan for Humidity
        "field3": "#94A3B8",  # Slate/Smoke
        "field4": "#EF4444",  # Red for CO
        "field5": "#A855F7",  # Purple for NH3
        "field6": "#EAB308",  # Yellow/Gold for NOx
        "field7": "#EC4899",  # Magenta/Pink for PM2.5
    }
    line_color = param_colors.get(field_id, color)

    fig = go.Figure()

    if df.empty or field_id not in df.columns or df[field_id].dropna().empty:
        fig.add_annotation(
            text="No telemetry recorded for this timeframe",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#94A3B8"),
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            margin=dict(l=40, r=20, t=35, b=35),
            height=280,
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
        )
        return fig

    # If field1 and temp_unit is °F, convert values for chart
    series_vals = df[field_id].copy()
    if field_id == "field1" and temp_unit == "°F":
        series_vals = series_vals.apply(lambda c: (c * 9/5 + 32) if pd.notnull(c) else None)

    # Line trace
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=series_vals,
            mode="lines+markers",
            name=name,
            line=dict(color=line_color, width=2.5, shape="spline"),
            marker=dict(size=4, color=line_color),
            hovertemplate=f"<b>{name}</b>: %{{y:.2f}} {unit}<br>Time: %{{x|%b %d, %H:%M:%S}}<extra></extra>",
        )
    )

    # Shaded threshold zones if applicable
    thresholds = cfg.get("thresholds", {})
    if "optimal_max" in thresholds:
        opt_max = thresholds["optimal_max"]
        if field_id == "field1" and temp_unit == "°F":
            opt_max = opt_max * 9/5 + 32
        fig.add_hline(
            y=opt_max,
            line_dash="dot",
            line_color="rgba(16, 185, 129, 0.6)",
            annotation_text=f"Target: {opt_max:.1f} {unit}",
            annotation_position="bottom right",
            annotation_font_size=10,
            annotation_font_color="#10B981",
        )

    if "warning_max" in thresholds:
        warn_max = thresholds["warning_max"]
        if field_id == "field1" and temp_unit == "°F":
            warn_max = warn_max * 9/5 + 32
        fig.add_hline(
            y=warn_max,
            line_dash="dash",
            line_color="rgba(239, 68, 68, 0.7)",
            annotation_text=f"Limit: {warn_max:.1f} {unit}",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color="#EF4444",
        )

    # Layout styling
    fig.update_layout(
        title=dict(
            text=f"<b>{name}</b> ({unit})",
            font=dict(size=14, color="#E2E8F0"),
            x=0.01,
            y=0.96,
        ),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#151C2C",
        margin=dict(l=40, r=20, t=40, b=35),
        height=270,
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            linecolor="#334155",
            tickfont=dict(color="#94A3B8", size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1E293B",
            linecolor="#334155",
            tickfont=dict(color="#94A3B8", size=10),
            title=dict(text=unit, font=dict(color="#94A3B8", size=11)),
        ),
    )

    return fig


def create_correlation_overview_chart(df: pd.DataFrame) -> go.Figure:
    """Create normalized multi-parameter overlay chart to visualize cross-pollutant events."""
    fig = go.Figure()

    if df.empty:
        return fig

    param_palette = {
        "field3": ("Smoke", "#94A3B8"),
        "field4": ("CO", "#EF4444"),
        "field5": ("NH3", "#A855F7"),
        "field6": ("NOx", "#EAB308"),
        "field7": ("PM2.5", "#EC4899"),
    }

    for f_id, (lbl, color) in param_palette.items():
        if f_id in df.columns and not df[f_id].dropna().empty:
            s = df[f_id].dropna()
            min_val = s.min()
            max_val = s.max()
            if max_val > min_val:
                norm_vals = (df[f_id] - min_val) / (max_val - min_val)
            else:
                norm_vals = df[f_id] * 0.0

            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=norm_vals,
                    mode="lines",
                    name=lbl,
                    line=dict(color=color, width=2),
                    hovertemplate=f"<b>{lbl}</b> (normalized): %{{y:.2f}}<extra></extra>",
                )
            )

    fig.update_layout(
        title=dict(
            text="<b>Multi-Pollutant Normalized Dynamics (Cross-Sensor Correlation)</b>",
            font=dict(size=14, color="#E2E8F0"),
            x=0.01,
            y=0.96,
        ),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#151C2C",
        margin=dict(l=40, r=20, t=45, b=35),
        height=320,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=11, color="#E2E8F0"),
        ),
        xaxis=dict(showgrid=True, gridcolor="#1E293B", tickfont=dict(color="#94A3B8", size=10)),
        yaxis=dict(
            title=dict(text="Normalized Index (0–1)", font=dict(color="#94A3B8", size=11)),
            showgrid=True,
            gridcolor="#1E293B",
            range=[0, 1.05],
            tickfont=dict(color="#94A3B8", size=10),
        ),
    )
    return fig


def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Generate Pearson correlation heatmap across all 7 sensor fields.
    Shows cross-coupling and emission source relationships.
    """
    field_keys = list(SENSOR_FIELDS.keys())
    labels = [SENSOR_FIELDS[f]["short_name"] for f in field_keys]

    fig = go.Figure()

    if df.empty or len(df.dropna(subset=field_keys, how="all")) < 5:
        fig.add_annotation(
            text="Insufficient data points for correlation matrix",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#94A3B8"),
        )
        fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="#111827")
        return fig

    # Compute correlation matrix
    valid_cols = [f for f in field_keys if f in df.columns]
    corr_matrix = df[valid_cols].corr()

    # Formatted z-values and text
    z_vals = corr_matrix.values
    text_vals = [[f"{val:.2f}" if pd.notnull(val) else "" for val in row] for row in z_vals]

    # Sleek cyan / turquoise to dark navy colorscale
    colorscale = [
        [0.0, "#0F172A"],
        [0.3, "#1E293B"],
        [0.5, "#0E7490"],
        [0.8, "#06B6D4"],
        [1.0, "#22D3EE"],
    ]

    fig.add_trace(
        go.Heatmap(
            z=z_vals,
            x=labels,
            y=labels,
            colorscale=colorscale,
            zmin=-1.0,
            zmax=1.0,
            text=text_vals,
            texttemplate="%{text}",
            textfont={"size": 11, "color": "#FFFFFF"},
            hoverongaps=False,
            colorbar=dict(
                title=dict(text="Pearson r", font=dict(color="#E2E8F0", size=11)),
                tickfont=dict(color="#94A3B8", size=10),
                thickness=12,
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Multi-Sensor Pearson Correlation Matrix</b>",
            font=dict(size=14, color="#E2E8F0"),
            x=0.01,
            y=0.96,
        ),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        margin=dict(l=50, r=30, t=50, b=40),
        height=340,
        xaxis=dict(tickfont=dict(color="#94A3B8", size=11)),
        yaxis=dict(tickfont=dict(color="#94A3B8", size=11)),
    )
    return fig


def create_sensor_comparison_chart(
    df: pd.DataFrame,
    field_a: str = "field7",
    field_b: str = "field4",
    temp_unit: str = "°C",
) -> go.Figure:
    """Create dual-axis interactive Plotly comparison chart between any two sensor fields."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if df.empty or field_a not in df.columns or field_b not in df.columns:
        return fig

    cfg_a = SENSOR_FIELDS.get(field_a, {})
    cfg_b = SENSOR_FIELDS.get(field_b, {})

    name_a = cfg_a.get("name", field_a)
    name_b = cfg_b.get("name", field_b)

    unit_a = temp_unit if field_a == "field1" else cfg_a.get("default_unit", "")
    unit_b = temp_unit if field_b == "field1" else cfg_b.get("default_unit", "")

    series_a = df[field_a]
    if field_a == "field1" and temp_unit == "°F":
        series_a = series_a.apply(lambda c: (c * 9/5 + 32) if pd.notnull(c) else None)

    series_b = df[field_b]
    if field_b == "field1" and temp_unit == "°F":
        series_b = series_b.apply(lambda c: (c * 9/5 + 32) if pd.notnull(c) else None)

    # Primary line (Cyan)
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=series_a,
            name=f"{name_a} ({unit_a})",
            line=dict(color="#00D2FF", width=2.5),
            hovertemplate=f"<b>{name_a}</b>: %{{y:.2f}} {unit_a}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Secondary line (Amber/Orange)
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=series_b,
            name=f"{name_b} ({unit_b})",
            line=dict(color="#F59E0B", width=2.5, dash="dot"),
            hovertemplate=f"<b>{name_b}</b>: %{{y:.2f}} {unit_b}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Direct Sensor Comparison: {name_a} vs. {name_b}</b>",
            font=dict(size=14, color="#E2E8F0"),
            x=0.01,
            y=0.96,
        ),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#151C2C",
        margin=dict(l=40, r=40, t=50, b=35),
        height=320,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=11, color="#E2E8F0"),
        ),
        xaxis=dict(showgrid=True, gridcolor="#1E293B", tickfont=dict(color="#94A3B8", size=10)),
    )

    fig.update_yaxes(
        title_text=f"{name_a} ({unit_a})",
        title_font=dict(color="#00D2FF", size=11),
        tickfont=dict(color="#00D2FF", size=10),
        secondary_y=False,
        showgrid=True,
        gridcolor="#1E293B",
    )
    fig.update_yaxes(
        title_text=f"{name_b} ({unit_b})",
        title_font=dict(color="#F59E0B", size=11),
        tickfont=dict(color="#F59E0B", size=10),
        secondary_y=True,
        showgrid=False,
    )
    return fig


def create_diurnal_pattern_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generate 24-hour diurnal cycle profile (hour-of-day 0 to 23)
    showing average pollution accumulation and ventilation curves.
    """
    fig = go.Figure()
    if df.empty or "timestamp" not in df.columns:
        return fig

    temp_df = df.copy()
    temp_df["hour"] = pd.to_datetime(temp_df["timestamp"]).dt.hour

    hourly_mean = temp_df.groupby("hour").mean(numeric_only=True).reset_index()

    traces = [
        ("field7", "PM2.5 (µg/m³)", "#EC4899", 1.0),
        ("field4", "CO (ppm × 5)", "#EF4444", 5.0),
        ("field3", "Smoke (ppm)", "#94A3B8", 1.0),
        ("field1", "Temperature (°C)", "#F59E0B", 1.0),
    ]

    for fid, label, color, multiplier in traces:
        if fid in hourly_mean.columns:
            y_vals = hourly_mean[fid] * multiplier
            fig.add_trace(
                go.Scatter(
                    x=hourly_mean["hour"],
                    y=y_vals,
                    mode="lines+markers",
                    name=label,
                    line=dict(color=color, width=2.4, shape="spline"),
                    marker=dict(size=5),
                    hovertemplate=f"<b>{label}</b> at %{{x}}:00: %{{y:.2f}}<extra></extra>",
                )
            )

    fig.update_layout(
        title=dict(
            text="<b>24-Hour Diurnal Pattern (Hourly Baseline Cycle)</b>",
            font=dict(size=14, color="#E2E8F0"),
            x=0.01,
            y=0.96,
        ),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#151C2C",
        margin=dict(l=40, r=20, t=50, b=35),
        height=320,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=11, color="#E2E8F0"),
        ),
        xaxis=dict(
            title=dict(text="Hour of Day (00:00 – 23:00)", font=dict(color="#94A3B8", size=11)),
            tickmode="linear",
            tick0=0,
            dtick=2,
            showgrid=True,
            gridcolor="#1E293B",
            tickfont=dict(color="#94A3B8", size=10),
        ),
        yaxis=dict(
            title=dict(text="Diurnal Average", font=dict(color="#94A3B8", size=11)),
            showgrid=True,
            gridcolor="#1E293B",
            tickfont=dict(color="#94A3B8", size=10),
        ),
    )
    return fig


def create_mini_sparkline(df: pd.DataFrame, field_id: str, color: str = "#00D2FF", height: int = 55) -> go.Figure:
    """Generate high-density lightweight mini sparkline for embedding inside KPI cards."""
    fig = go.Figure()
    if df.empty or field_id not in df.columns or df[field_id].dropna().empty:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    # Take last 25 readings for sparkline
    recent = df.tail(25)
    fig.add_trace(
        go.Scatter(
            x=recent["timestamp"],
            y=recent[field_id],
            mode="lines",
            line=dict(color=color, width=2.0),
            fill="tozeroy",
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.12)",
            hoverinfo="none",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=2, r=2, t=4, b=2),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def create_distribution_chart(
    df: pd.DataFrame,
    field_id: str,
    temp_unit: str = "°C",
    chart_type: str = "Histogram",
) -> go.Figure:
    """
    Generate reading distribution visualization (Histogram or Box Plot)
    with statistical quartiles and density estimation.
    """
    cfg = SENSOR_FIELDS.get(field_id, {})
    name = cfg.get("name", field_id)
    unit = temp_unit if field_id == "field1" else cfg.get("default_unit", "")

    fig = go.Figure()

    if df.empty or field_id not in df.columns or df[field_id].dropna().empty:
        fig.add_annotation(
            text="No data available for distribution",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#94A3B8"),
        )
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="#111827")
        return fig

    series = df[field_id].dropna().copy()
    if field_id == "field1" and temp_unit == "°F":
        series = series * 9 / 5 + 32

    # Accent color map
    param_colors = {
        "field1": "#F59E0B",
        "field2": "#06B6D4",
        "field3": "#94A3B8",
        "field4": "#EF4444",
        "field5": "#A855F7",
        "field6": "#EAB308",
        "field7": "#EC4899",
    }
    color = param_colors.get(field_id, "#00D2FF")

    if chart_type == "Box Plot":
        fig.add_trace(
            go.Box(
                y=series,
                name=f"{name} ({unit})",
                boxpoints="outliers",
                jitter=0.3,
                pointpos=-1.8,
                marker=dict(color=color, size=4),
                line=dict(color=color, width=2),
                fillcolor=f"rgba(14, 116, 144, 0.35)",
            )
        )
        fig.update_layout(
            title=dict(text=f"<b>{name} Box Plot & Outlier Spread</b>", font=dict(color="#E2E8F0", size=13)),
            yaxis=dict(title=dict(text=f"{name} ({unit})", font=dict(color="#94A3B8", size=11)), showgrid=True, gridcolor="#1E293B"),
        )
    else:
        # Histogram
        fig.add_trace(
            go.Histogram(
                x=series,
                name=f"{name} Frequency",
                nbinsx=35,
                marker=dict(
                    color=color,
                    line=dict(color="#0B1120", width=1),
                ),
                opacity=0.85,
                hovertemplate=f"Range: %{{x}} {unit}<br>Count: %{{y}}<extra></extra>",
            )
        )
        # Add Mean vertical line
        mean_val = float(series.mean())
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="#22D3EE",
            annotation_text=f"Mean: {mean_val:.1f} {unit}",
            annotation_position="top right",
            annotation_font_color="#22D3EE",
            annotation_font_size=10,
        )
        fig.update_layout(
            title=dict(text=f"<b>{name} Frequency Distribution Histogram</b>", font=dict(color="#E2E8F0", size=13)),
            xaxis=dict(title=dict(text=f"{name} ({unit})", font=dict(color="#94A3B8", size=11)), showgrid=True, gridcolor="#1E293B"),
            yaxis=dict(title=dict(text="Frequency Count", font=dict(color="#94A3B8", size=11)), showgrid=True, gridcolor="#1E293B"),
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#151C2C",
        margin=dict(l=40, r=20, t=45, b=35),
        height=280,
    )
    return fig


def create_scatter_relationship(
    df: pd.DataFrame,
    field_x: str = "field3",
    field_y: str = "field4",
    temp_unit: str = "°C",
) -> go.Figure:
    """
    Generate interactive scatter plot showing correlation relationship between two parameters
    with linear regression trendline.
    """
    cfg_x = SENSOR_FIELDS.get(field_x, {})
    cfg_y = SENSOR_FIELDS.get(field_y, {})
    name_x = cfg_x.get("name", field_x)
    name_y = cfg_y.get("name", field_y)
    unit_x = temp_unit if field_x == "field1" else cfg_x.get("default_unit", "")
    unit_y = temp_unit if field_y == "field1" else cfg_y.get("default_unit", "")

    fig = go.Figure()

    clean_sub = df[[field_x, field_y, "timestamp"]].dropna() if (field_x in df.columns and field_y in df.columns) else pd.DataFrame()
    if clean_sub.empty or len(clean_sub) < 5:
        fig.add_annotation(
            text="Insufficient coincident readings for scatter correlation",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#94A3B8"),
        )
        fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="#111827")
        return fig

    # Values
    x_vals = clean_sub[field_x].values
    y_vals = clean_sub[field_y].values

    # Scatter points
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name="Coincident Readings",
            marker=dict(
                size=5,
                color="#00D2FF",
                opacity=0.6,
                line=dict(width=0.5, color="#14B8A6"),
            ),
            hovertemplate=f"<b>{name_x}</b>: %{{x:.2f}} {unit_x}<br><b>{name_y}</b>: %{{y:.2f}} {unit_y}<extra></extra>",
        )
    )

    # Linear trendline
    if len(x_vals) > 2 and np.std(x_vals) > 1e-4:
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        x_trend = np.linspace(np.min(x_vals), np.max(x_vals), 50)
        y_trend = slope * x_trend + intercept
        corr_r = np.corrcoef(x_vals, y_vals)[0, 1]

        fig.add_trace(
            go.Scatter(
                x=x_trend,
                y=y_trend,
                mode="lines",
                name=f"OLS Trendline (r={corr_r:.2f})",
                line=dict(color="#EF4444", width=2.5, dash="dash"),
            )
        )

    fig.update_layout(
        title=dict(
            text=f"<b>Correlation Scatter: {name_x} vs. {name_y}</b>",
            font=dict(size=14, color="#E2E8F0"),
            x=0.01,
            y=0.96,
        ),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#151C2C",
        margin=dict(l=45, r=20, t=50, b=40),
        height=320,
        xaxis=dict(
            title=dict(text=f"{name_x} ({unit_x})", font=dict(color="#94A3B8", size=11)),
            showgrid=True,
            gridcolor="#1E293B",
            tickfont=dict(color="#94A3B8", size=10),
        ),
        yaxis=dict(
            title=dict(text=f"{name_y} ({unit_y})", font=dict(color="#94A3B8", size=11)),
            showgrid=True,
            gridcolor="#1E293B",
            tickfont=dict(color="#94A3B8", size=10),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=10, color="#E2E8F0"),
        ),
    )
    return fig


def calculate_peak_periods(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Detects top peak pollution periods / emission events across historical telemetry.
    Ranks events by particulate and combustion severity.
    """
    if df.empty or "timestamp" not in df.columns:
        return []

    peaks = []
    # Check PM2.5, Smoke, and CO
    target_fields = [("field7", "PM2.5"), ("field4", "Carbon Monoxide"), ("field3", "Smoke")]
    for fid, fname in target_fields:
        if fid in df.columns and not df[fid].dropna().empty:
            top_records = df.nlargest(top_n, fid)[["timestamp", "entry_id", fid]]
            cfg = SENSOR_FIELDS.get(fid, {})
            unit = cfg.get("default_unit", "")
            for _, r in top_records.iterrows():
                peaks.append({
                    "timestamp": r["timestamp"],
                    "entry_id": int(r["entry_id"]) if pd.notnull(r["entry_id"]) else 0,
                    "parameter": fname,
                    "field_id": fid,
                    "value": round(float(r[fid]), 2),
                    "unit": unit,
                    "severity": "Critical" if r[fid] > cfg.get("thresholds", {}).get("warning_max", 100) else "Elevated",
                })

    # Sort by timestamp
    peaks.sort(key=lambda x: x["timestamp"], reverse=True)
    return peaks[:top_n]

