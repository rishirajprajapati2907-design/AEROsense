"""
AEROsense Circular AQI-Style Gauge Component
Interactive animated circular gauge displaying preliminary multi-pollutant indoor air severity index.
Explicitly labeled as preliminary diagnostic guidance (not an official certified statutory AQI).
"""

from typing import Optional
import plotly.graph_objects as go


def calculate_preliminary_air_score(values: dict) -> float:
    """
    Computes a normalized composite indoor air severity index (0 - 100)
    based on relative contributions of PM2.5, CO, Smoke, NH3, and NOx.
    0 = Pristine / Clean, 100 = Hazardous.
    """
    if not values:
        return 0.0

    scores = []
    # PM2.5 (0 - 55 ug/m3 maps to 0 - 100)
    pm25 = values.get("field7")
    if pm25 is not None:
        scores.append(min(100.0, (pm25 / 55.4) * 80.0))

    # CO (0 - 50 ppm maps to 0 - 100)
    co = values.get("field4")
    if co is not None:
        scores.append(min(100.0, (co / 50.0) * 85.0))

    # Smoke (0 - 180 ppm maps to 0 - 100)
    smoke = values.get("field3")
    if smoke is not None:
        scores.append(min(100.0, (smoke / 180.0) * 80.0))

    # NH3 (0 - 25 ppm maps to 0 - 100)
    nh3 = values.get("field5")
    if nh3 is not None:
        scores.append(min(100.0, (nh3 / 25.0) * 75.0))

    # NOx (0 - 0.20 ppm maps to 0 - 100)
    nox = values.get("field6")
    if nox is not None:
        scores.append(min(100.0, (nox / 0.20) * 80.0))

    if not scores:
        return 0.0

    # Primary driver gets 60% weight, average of others gets 40% weight
    scores.sort(reverse=True)
    composite = scores[0] * 0.65 + (sum(scores[1:]) / max(1, len(scores) - 1)) * 0.35
    return round(min(100.0, max(0.0, composite)), 1)


def create_circular_aqi_gauge(
    values: dict,
    status_label: str = "Optimal Air",
    status_color: str = "#B7F34A",
    height: int = 340,
) -> go.Figure:
    """Create a high-end circular gauge with color-coded safety steps."""
    score = calculate_preliminary_air_score(values)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0.05, 0.95], "y": [0.05, 0.95]},
            title={
                "text": "<b>PRELIMINARY INDOOR AIR INDEX</b><br><span style='font-size:11px;color:rgba(232,237,235,0.65);'>Validated Threshold Multi-Gas Aggregate</span>",
                "font": {"size": 13, "color": "#E8EDEB"},
            },
            number={
                "suffix": " / 100",
                "font": {"size": 34, "color": "#E8EDEB", "family": "Plus Jakarta Sans, Inter, sans-serif"},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "rgba(232, 237, 235, 0.25)",
                    "tickfont": {"size": 10, "color": "#E8EDEB"},
                    "nticks": 6,
                },
                "bar": {"color": status_color, "thickness": 0.22},
                "bgcolor": "#16222F",
                "borderwidth": 1,
                "bordercolor": "rgba(232, 237, 235, 0.12)",
                "steps": [
                    {"range": [0, 30], "color": "rgba(183, 243, 74, 0.22)"},
                    {"range": [30, 60], "color": "rgba(245, 158, 11, 0.22)"},
                    {"range": [60, 80], "color": "rgba(249, 115, 22, 0.25)"},
                    {"range": [80, 100], "color": "rgba(239, 68, 68, 0.28)"},
                ],
                "threshold": {
                    "line": {"color": "#EF4444", "width": 3},
                    "thickness": 0.8,
                    "value": 80,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E8EDEB"},
        margin=dict(l=20, r=20, t=50, b=25),
        height=height,
    )

    return fig
