# XXX: GLM 5.2 is not that good at making dashboard, i'll ask another ai model
# This will serve as a bare minimum example

import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "database" / "data.csv"

ACCENT_BLUE = "#3b82f6"
ACCENT_GREEN = "#22c55e"
ACCENT_RED = "#ef4444"
ACCENT_AMBER = "#f59e0b"
CHART_COLORS = [
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_AMBER,
    ACCENT_RED,
    "#a855f7",
    "#06b6d4",
    "#ec4899",
]


def load_and_clean_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["jumlah_korupsi_num"] = df["jumlah_korupsi"].apply(_parse_rp)
    df["hukuman_denda_num"] = df["hukuman_denda"].apply(_parse_rp)
    df["uang_pengganti_num"] = df["uang_pengganti"].apply(_parse_rp)
    df["tahun_korupsi_num"] = df["tahun_korupsi"].apply(_parse_year)
    df["tahun_putusan_num"] = df["tahun_putusan"].apply(_parse_year)
    df["hukuman_penjara_num"] = df["hukuman_penjara"].apply(_parse_prison_years)
    return df


def _parse_rp(val: str) -> float | None:
    if pd.isna(val) or not val:
        return None
    cleaned = re.sub(r"[^\d]", "", str(val))
    return float(cleaned) if cleaned else None


def _parse_year(val: str) -> float | None:
    if pd.isna(val) or not val:
        return None
    match = re.search(r"\d{4}", str(val))
    return float(match.group()) if match else None


def _parse_prison_years(val: str) -> float | None:
    if pd.isna(val) or not val:
        return None
    match = re.search(r"(\d+)", str(val))
    return float(match.group(1)) if match else None


def _fmt_rp(val: float | None) -> str:
    if pd.isna(val) or val is None:
        return "-"
    return f"Rp {val:,.0f}".replace(",", ".")


def _fmt_short(val: float) -> str:
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}T"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val / 1_000:.0f}K"
    return f"{val:.0f}"


app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Korupnesia"

df = load_and_clean_data()
all_professions = sorted(df["profesi"].dropna().unique())
year_min = (
    int(df["tahun_korupsi_num"].min())
    if df["tahun_korupsi_num"].notna().any()
    else 2000
)
year_max = (
    int(df["tahun_korupsi_num"].max())
    if df["tahun_korupsi_num"].notna().any()
    else 2025
)

app.layout = html.Div(
    style={
        "fontFamily": "Inter, Segoe UI, sans-serif",
        "padding": "24px",
        "maxWidth": "1400px",
        "margin": "0 auto",
    },
    children=[
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "24px",
            },
            children=[
                html.Div(
                    [
                        html.H1(
                            "Korupnesia", style={"margin": "0", "fontSize": "24px"}
                        ),
                        html.P(
                            "Data koruptor dari Korupedia",
                            style={
                                "margin": "2px 0 0 0",
                                "color": "#6b7280",
                                "fontSize": "13px",
                            },
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Span(
                            f"{len(df)} total records",
                            style={"fontSize": "12px", "color": "#9ca3af"},
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            style={
                "display": "flex",
                "gap": "16px",
                "marginBottom": "20px",
                "alignItems": "flex-end",
                "flexWrap": "wrap",
            },
            children=[
                html.Div(
                    style={"flex": "2", "minWidth": "280px"},
                    children=[
                        html.Label(
                            "Tahun Korupsi",
                            style={
                                "fontSize": "12px",
                                "fontWeight": "600",
                                "marginBottom": "4px",
                                "display": "block",
                            },
                        ),
                        dcc.RangeSlider(
                            id="year-slider",
                            min=year_min,
                            max=year_max,
                            value=[year_min, year_max],
                            marks={y: str(y) for y in range(year_min, year_max + 1, 3)},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                ),
                html.Div(
                    style={"flex": "1", "minWidth": "220px"},
                    children=[
                        html.Label(
                            "Profesi",
                            style={
                                "fontSize": "12px",
                                "fontWeight": "600",
                                "marginBottom": "4px",
                                "display": "block",
                            },
                        ),
                        dcc.Dropdown(
                            id="profession-filter",
                            options=[{"label": p, "value": p} for p in all_professions],
                            multi=True,
                            placeholder="Semua profesi",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id="kpi-row",
            style={
                "display": "flex",
                "gap": "12px",
                "marginBottom": "20px",
                "flexWrap": "wrap",
            },
        ),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "16px",
                "marginBottom": "16px",
            },
            children=[
                html.Div(
                    dcc.Graph(id="chart-corruption-by-profession"),
                    style={
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                ),
                html.Div(
                    dcc.Graph(id="chart-cases-by-year"),
                    style={
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                ),
            ],
        ),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "16px",
                "marginBottom": "20px",
            },
            children=[
                html.Div(
                    dcc.Graph(id="chart-sentence-dist"),
                    style={
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                ),
                html.Div(
                    dcc.Graph(id="chart-top-fines"),
                    style={
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                ),
            ],
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "5fr 2fr", "gap": "16px"},
            children=[
                html.Div(
                    style={
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "padding": "16px",
                    },
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "marginBottom": "12px",
                            },
                            children=[
                                html.H3(
                                    "Data Koruptor",
                                    style={"margin": "0", "fontSize": "15px"},
                                ),
                                html.Span(
                                    id="table-count",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#9ca3af",
                                        "alignSelf": "center",
                                    },
                                ),
                            ],
                        ),
                        html.Div(id="data-table-container"),
                    ],
                ),
                html.Div(
                    style={
                        "border": "1px solid #e5e7eb",
                        "borderRadius": "8px",
                        "padding": "16px",
                    },
                    children=[
                        html.H3(
                            "Detail Kasus",
                            style={"margin": "0 0 12px 0", "fontSize": "15px"},
                        ),
                        html.Div(
                            id="case-detail",
                            children=html.P(
                                "Klik baris pada tabel",
                                style={
                                    "color": "#9ca3af",
                                    "fontSize": "13px",
                                    "fontStyle": "italic",
                                },
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


def _kpi(title: str, value: str, color: str = ACCENT_BLUE) -> html.Div:
    return html.Div(
        style={
            "flex": "1",
            "minWidth": "150px",
            "border": "1px solid #e5e7eb",
            "borderRadius": "8px",
            "padding": "16px",
        },
        children=[
            html.P(
                title,
                style={
                    "margin": "0",
                    "color": "#6b7280",
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                },
            ),
            html.H2(
                value,
                style={
                    "margin": "4px 0 0 0",
                    "fontSize": "22px",
                    "fontWeight": "700",
                    "color": color,
                },
            ),
        ],
    )


def _filter_data(year_range: list[int], professions: list[str]) -> pd.DataFrame:
    filtered = df.copy()
    if year_range:
        filtered = filtered[
            filtered["tahun_korupsi_num"].between(year_range[0], year_range[1])
            | filtered["tahun_korupsi_num"].isna()
        ]
    if professions:
        filtered = filtered[filtered["profesi"].isin(professions)]
    return filtered


TABLE_STYLE_HEADER = {
    "backgroundColor": "#f9fafb",
    "fontWeight": "600",
    "fontSize": "12px",
    "border": "1px solid #e5e7eb",
    "padding": "10px 12px",
}
TABLE_STYLE_CELL = {
    "textAlign": "left",
    "fontSize": "13px",
    "padding": "10px 12px",
    "border": "1px solid #e5e7eb",
    "whiteSpace": "nowrap",
    "overflow": "hidden",
    "textOverflow": "ellipsis",
    "maxWidth": "200px",
}
TABLE_STYLE_DATA_COND = [
    {"if": {"row_index": "odd"}, "backgroundColor": "#f9fafb"},
    {
        "if": {"state": "selected"},
        "backgroundColor": "#eff6ff",
        "border": "1px solid #3b82f6",
    },
]


@callback(
    Output("kpi-row", "children"),
    Output("chart-corruption-by-profession", "figure"),
    Output("chart-cases-by-year", "figure"),
    Output("chart-sentence-dist", "figure"),
    Output("chart-top-fines", "figure"),
    Output("data-table-container", "children"),
    Output("table-count", "children"),
    Input("year-slider", "value"),
    Input("profession-filter", "value"),
)
def update_dashboard(year_range, professions):
    filtered = _filter_data(year_range, professions)
    total = len(filtered)
    total_corruption = filtered["jumlah_korupsi_num"].sum()
    avg_sentence = filtered["hukuman_penjara_num"].mean()
    avg_fine = filtered["hukuman_denda_num"].mean()

    kpi_children = [
        _kpi("Total Kasus", f"{total:,}"),
        _kpi("Total Kerugian", _fmt_short(total_corruption), ACCENT_RED),
        _kpi(
            "Rata-rata Hukuman",
            f"{avg_sentence:.1f} thn" if pd.notna(avg_sentence) else "-",
            ACCENT_AMBER,
        ),
        _kpi(
            "Rata-rata Denda",
            f"Rp {_fmt_short(avg_fine)}" if pd.notna(avg_fine) else "-",
            ACCENT_GREEN,
        ),
    ]

    chart_font = dict(family="Inter, Segoe UI, sans-serif")
    chart_margin = dict(t=44, b=28, l=12, r=12)
    chart_grid = dict(gridcolor="#f3f4f6")

    # Corruption by profession
    by_prof = (
        filtered.dropna(subset=["profesi", "jumlah_korupsi_num"])
        .groupby("profesi")["jumlah_korupsi_num"]
        .sum()
        .sort_values(ascending=True)
        .tail(12)
        .reset_index()
    )
    fig_prof = go.Figure(
        go.Bar(
            x=by_prof["jumlah_korupsi_num"],
            y=by_prof["profesi"],
            orientation="h",
            marker_color=ACCENT_BLUE,
            hovertemplate="%{y}<br>Rp %{x:,.0f}<extra></extra>",
        )
    )
    fig_prof.update_layout(
        title=dict(text="Kerugian per Profesi", font=dict(size=14)),
        margin=chart_margin,
        height=340,
        font=chart_font,
        xaxis=dict(gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
        showlegend=False,
    )

    # Cases by year
    by_year = (
        filtered.dropna(subset=["tahun_korupsi_num"])
        .groupby("tahun_korupsi_num")
        .size()
        .reset_index(name="jumlah_kasus")
        .sort_values("tahun_korupsi_num")
    )
    fig_year = go.Figure(
        go.Bar(
            x=by_year["tahun_korupsi_num"].astype(int),
            y=by_year["jumlah_kasus"],
            marker_color=ACCENT_GREEN,
            hovertemplate="Tahun %{x}<br>%{y} kasus<extra></extra>",
        )
    )
    fig_year.update_layout(
        title=dict(text="Kasus per Tahun", font=dict(size=14)),
        margin=chart_margin,
        height=340,
        font=chart_font,
        xaxis=dict(gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
        showlegend=False,
        bargap=0.3,
    )

    # Sentence distribution donut
    sentence_data = filtered["hukuman_penjara"].dropna().replace("", pd.NA).dropna()
    if len(sentence_data) > 0:
        sent_counts = sentence_data.value_counts().head(8).reset_index()
        fig_sent = go.Figure(
            go.Pie(
                labels=sent_counts["hukuman_penjara"],
                values=sent_counts["count"],
                hole=0.5,
                marker=dict(colors=CHART_COLORS),
            )
        )
        fig_sent.add_annotation(
            text=f"<b>{total}</b><br>kasus", showarrow=False, font=dict(size=16)
        )
    else:
        fig_sent = go.Figure()
    fig_sent.update_layout(
        title=dict(text="Distribusi Hukuman", font=dict(size=14)),
        margin=chart_margin,
        height=340,
        font=chart_font,
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
    )

    # Top fines
    by_fine = (
        filtered.dropna(subset=["nama", "hukuman_denda_num"])
        .nlargest(12, "hukuman_denda_num")
        .sort_values("hukuman_denda_num", ascending=True)
    )
    fig_fine = go.Figure(
        go.Bar(
            x=by_fine["hukuman_denda_num"],
            y=by_fine["nama"],
            orientation="h",
            marker_color=ACCENT_AMBER,
            hovertemplate="%{y}<br>Rp %{x:,.0f}<extra></extra>",
        )
    )
    fig_fine.update_layout(
        title=dict(text="Denda Tertinggi", font=dict(size=14)),
        margin=chart_margin,
        height=340,
        font=chart_font,
        xaxis=dict(gridcolor="#f3f4f6"),
        yaxis=dict(gridcolor="#f3f4f6"),
        showlegend=False,
    )

    # Table
    table_cols = [
        "nama",
        "profesi",
        "tahun_korupsi",
        "jumlah_korupsi",
        "hukuman_penjara",
        "hukuman_denda",
    ]
    table_df = filtered[[c for c in table_cols if c in filtered.columns]].copy()
    table = dash_table.DataTable(
        id="korupsi-table",
        columns=[
            {"name": c.replace("_", " ").title(), "id": c}
            for c in table_cols
            if c in filtered.columns
        ],
        data=table_df.to_dict("records"),
        page_size=10,
        sort_action="native",
        filter_action="native",
        row_selectable="single",
        style_table={"overflowX": "auto", "maxHeight": "420px", "overflowY": "auto"},
        style_header=TABLE_STYLE_HEADER,
        style_cell=TABLE_STYLE_CELL,
        style_data_conditional=TABLE_STYLE_DATA_COND,
    )

    count_text = f"{total} dari {len(df)} records"
    return kpi_children, fig_prof, fig_year, fig_sent, fig_fine, table, count_text


@callback(
    Output("case-detail", "children"),
    Input("korupsi-table", "selected_rows"),
    State("korupsi-table", "data"),
)
def show_detail(selected_rows, table_data):
    if not selected_rows:
        return html.P(
            "Klik baris pada tabel",
            style={"color": "#9ca3af", "fontSize": "13px", "fontStyle": "italic"},
        )

    row = table_data[selected_rows[0]]
    nama = row.get("nama", "-")

    fields = [
        ("Profesi", "profesi"),
        ("Tahun Korupsi", "tahun_korupsi"),
        ("Jumlah Korupsi", "jumlah_korupsi"),
        ("Hukuman Penjara", "hukuman_penjara"),
        ("Hukuman Denda", "hukuman_denda"),
        ("Uang Pengganti", "uang_pengganti"),
        ("Tahun Putusan", "tahun_putusan"),
        ("Nomor Putusan", "nomor_putusan_akhir"),
    ]

    items = []
    for label, key in fields:
        val = row.get(key, "")
        if val and str(val).strip():
            items.append(
                html.Div(
                    style={"marginBottom": "12px"},
                    children=[
                        html.Div(
                            label,
                            style={
                                "fontSize": "10px",
                                "fontWeight": "600",
                                "color": "#9ca3af",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px",
                                "marginBottom": "2px",
                            },
                        ),
                        html.Div(
                            str(val), style={"fontSize": "13px", "lineHeight": "1.5"}
                        ),
                    ],
                )
            )

    deskripsi = row.get("deskripsi", "")
    if deskripsi and str(deskripsi).strip():
        items.append(
            html.Div(
                style={
                    "marginTop": "12px",
                    "paddingTop": "12px",
                    "borderTop": "1px solid #e5e7eb",
                },
                children=[
                    html.Div(
                        "Deskripsi",
                        style={
                            "fontSize": "10px",
                            "fontWeight": "600",
                            "color": "#9ca3af",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                            "marginBottom": "4px",
                        },
                    ),
                    html.P(
                        str(deskripsi),
                        style={
                            "fontSize": "12px",
                            "color": "#6b7280",
                            "lineHeight": "1.6",
                            "margin": "0",
                        },
                    ),
                ],
            )
        )

    return html.Div(
        [
            html.H4(nama, style={"margin": "0 0 14px 0", "fontSize": "16px"}),
            *items,
        ]
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
