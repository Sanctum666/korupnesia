import dash
from dash import Dash, dcc, html
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
import re

# Parsing functions based on parsed_koruptor_data_example.json structure
def parse_rupiah(text):
    if pd.isna(text): return 0
    text = str(text).replace("Rp", "").replace(".", "").replace(",", "").strip()
    try:
        return int(text)
    except ValueError:
        return 0

def parse_penjara(text):
    if pd.isna(text): return 0
    match = re.search(r'(\d+)', str(text))
    if match:
        return int(match.group(1))
    return 0

def parse_year(text):
    if pd.isna(text): return None
    match = re.search(r'(\d{4})', str(text))
    if match:
        return int(match.group(1))
    return None

def format_rupiah(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

def format_rupiah_short(amount):
    if amount >= 1_000_000_000_000:
        return f"Rp {amount / 1_000_000_000_000:.2f} Triliun".replace(".", ",")
    elif amount >= 1_000_000_000:
        return f"Rp {amount / 1_000_000_000:.2f} Miliar".replace(".", ",")
    elif amount >= 1_000_000:
        return f"Rp {amount / 1_000_000:.2f} Juta".replace(".", ",")
    else:
        return f"Rp {amount:,.0f}".replace(",", ".")

# Load data
df = pd.read_csv("database/data.csv")

# Clean data
df["jumlah_korupsi_num"] = df["jumlah_korupsi"].apply(parse_rupiah)
df["hukuman_penjara_num"] = df["hukuman_penjara"].apply(parse_penjara)
df["tahun_korupsi_num"] = df["tahun_korupsi"].apply(parse_year)

# Metrics calculation
total_korupsi = df["jumlah_korupsi_num"].sum()
total_kasus = len(df)
avg_penjara = df["hukuman_penjara_num"].mean()

# Aggregates for charts
df_year = df.groupby("tahun_korupsi_num")["jumlah_korupsi_num"].sum().reset_index()
df_year = df_year.dropna()

fig = px.bar(
    df_year, 
    x="tahun_korupsi_num", 
    y="jumlah_korupsi_num", 
    title="Kerugian Negara per Tahun",
    labels={"tahun_korupsi_num": "Tahun", "jumlah_korupsi_num": "Total Kerugian (Rp)"}
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", 
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20)
)

top_10 = df.nlargest(10, "jumlah_korupsi_num")
table_body = [
    [
        row["nama"], 
        str(row["profesi"])[:30], 
        int(row["tahun_korupsi_num"]) if pd.notna(row["tahun_korupsi_num"]) else "-", 
        format_rupiah(row["jumlah_korupsi_num"]), 
        f"{row['hukuman_penjara_num']} Tahun"
    ]
    for _, row in top_10.iterrows()
]

# Initialize Dash App
app = Dash(__name__)

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Text("Korupnesia Dashboard", size="xl", fw=700, c="red"),
                        dmc.Badge("Budget App Style", color="gray")
                    ],
                    h="100%",
                    px="md",
                    align="center",
                )
            ),
            dmc.AppShellMain(
                dmc.Container(
                    [
                        dmc.Title("Ringkasan Data Koruptor", order=2, mt="md", mb="md"),
                        dmc.SimpleGrid(
                            cols=3,
                            children=[
                                dmc.Paper(
                                    [
                                        dmc.Text("Total Kerugian Negara", c="dimmed", size="sm"),
                                        dmc.Text(format_rupiah(total_korupsi), fw=700, size="xl", c="red"),
                                        dmc.Text(f"({format_rupiah_short(total_korupsi)})", c="dimmed", size="xs", mt=5),
                                    ],
                                    withBorder=True,
                                    shadow="sm",
                                    p="md",
                                    radius="md",
                                ),
                                dmc.Paper(
                                    [
                                        dmc.Text("Total Kasus Terdaftar", c="dimmed", size="sm"),
                                        dmc.Text(f"{total_kasus} Kasus", fw=700, size="xl"),
                                    ],
                                    withBorder=True,
                                    shadow="sm",
                                    p="md",
                                    radius="md",
                                ),
                                dmc.Paper(
                                    [
                                        dmc.Text("Rata-rata Hukuman Penjara", c="dimmed", size="sm"),
                                        dmc.Text(f"{avg_penjara:.1f} Tahun", fw=700, size="xl"),
                                    ],
                                    withBorder=True,
                                    shadow="sm",
                                    p="md",
                                    radius="md",
                                ),
                            ],
                            mb="xl",
                        ),
                        
                        dmc.Paper(
                            dcc.Graph(figure=fig),
                            withBorder=True,
                            shadow="sm",
                            p="md",
                            radius="md",
                            mb="xl"
                        ),

                        dmc.Title("10 Kasus dengan Kerugian Terbesar", order=3, mb="md"),
                        dmc.TableScrollContainer(
                            dmc.Table(
                                data={
                                    "head": ["Nama", "Profesi", "Tahun", "Jumlah Korupsi", "Hukuman"],
                                    "body": table_body
                                },
                                striped=True,
                                highlightOnHover=True,
                                withTableBorder=True,
                            ),
                            minWidth=500,
                            mb="xl"
                        )
                    ],
                    size="lg",
                )
            )
        ],
        header={"height": 60}
    )
)

if __name__ == "__main__":
    app.run(debug=True)
