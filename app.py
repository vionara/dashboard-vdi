import os
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine, text

load_dotenv()
st.set_page_config(page_title="Dashboard Populasi & Ekonomi", page_icon="🌍", layout="wide")

DB_PATH = os.getenv("SQLITE_PATH", "database/world_data.db")
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "vdi_dashboard")

@st.cache_resource
def get_sql_engine():
    return create_engine(f"sqlite:///{DB_PATH}")

@st.cache_resource
def get_mongo_collection():
    if not MONGO_URI:
        return None
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    return client[MONGO_DB]

def load_data():
    engine = get_sql_engine()
    with engine.connect() as conn:
        data = pd.read_sql(text("""
            SELECT country_code, country_name, year, population, gdp_per_capita
            FROM indicators
            ORDER BY year
        """), conn)

    # DBMS 2: metadata negara disimpan di MongoDB.
    # Dokumen metadata digabungkan dengan tabel SQLite menggunakan Pandas merge().
    db = get_mongo_collection()
    if db is None:
        data["region"] = "MongoDB belum dikonfigurasi"
        data["income_group"] = "Tidak tersedia"
    else:
        metadata = list(db["country_metadata"].find(
            {}, {"_id": 0, "country_code": 1, "region": 1, "income_group": 1}
        ))
        if not metadata:
            defaults = [
                {"country_code":"IDN","region":"Asia Tenggara","income_group":"Menengah"},
                {"country_code":"MYS","region":"Asia Tenggara","income_group":"Menengah"},
                {"country_code":"SGP","region":"Asia Tenggara","income_group":"Tinggi"},
                {"country_code":"THA","region":"Asia Tenggara","income_group":"Menengah"},
                {"country_code":"PHL","region":"Asia Tenggara","income_group":"Menengah"},
                {"country_code":"VNM","region":"Asia Tenggara","income_group":"Menengah"},
                {"country_code":"JPN","region":"Asia Timur","income_group":"Tinggi"},
                {"country_code":"KOR","region":"Asia Timur","income_group":"Tinggi"},
                {"country_code":"CHN","region":"Asia Timur","income_group":"Menengah"},
                {"country_code":"IND","region":"Asia Selatan","income_group":"Menengah"},
                {"country_code":"USA","region":"Amerika Utara","income_group":"Tinggi"},
                {"country_code":"GBR","region":"Eropa","income_group":"Tinggi"},
                {"country_code":"AUS","region":"Oseania","income_group":"Tinggi"},
            ]
            db["country_metadata"].insert_many(defaults)
            metadata = defaults
        metadata_df = pd.DataFrame(metadata)
        data = data.merge(metadata_df, on="country_code", how="left")
    return data

def save_activity(action, details):
    try:
        db = get_mongo_collection()
        if db is not None:
            db["activity_logs"].insert_one({
                "action": action,
                "details": details,
                "created_at": datetime.now(timezone.utc)
            })
    except Exception as exc:
        st.sidebar.warning(f"MongoDB belum terhubung: {exc}")

st.title("🌍 Dashboard Analisis Populasi dan Ekonomi Dunia")
st.caption("Integrasi SQLite + MongoDB | Python, Pandas, Plotly, dan Streamlit")

try:
    df = load_data()
except Exception as exc:
    st.error("Database SQLite belum tersedia. Jalankan seed database terlebih dahulu.")
    st.code("python database/seed_data.py")
    st.exception(exc)
    st.stop()

if df.empty:
    st.warning("Belum ada data. Jalankan python database/seed_data.py.")
    st.stop()

st.sidebar.header("Filter Dashboard")
country_options = sorted(df["country_name"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Pilih negara", country_options,
    default=[x for x in ["Indonesia", "Malaysia", "Singapore", "Thailand", "United States"] if x in country_options]
)
min_year, max_year = int(df.year.min()), int(df.year.max())
year_range = st.sidebar.slider("Rentang tahun", min_year, max_year, (min_year, max_year))

filtered = df[
    df["country_name"].isin(selected_countries)
    & df["year"].between(year_range[0], year_range[1])
].copy()
save_activity("dashboard_opened", {
    "selected_countries": selected_countries,
    "year_range": list(year_range)
})

if filtered.empty:
    st.info("Pilih minimal satu negara untuk menampilkan visualisasi.")
    st.stop()

latest_year = int(filtered["year"].max())
latest = filtered[filtered["year"] == latest_year]
c1, c2, c3 = st.columns(3)
c1.metric("Negara dipilih", filtered["country_name"].nunique())
c2.metric(f"Total populasi ({latest_year})", f"{latest['population'].sum():,.0f}")
avg_gdp = latest["gdp_per_capita"].mean()
c3.metric(f"Rata-rata GDP per kapita ({latest_year})", f"${avg_gdp:,.0f}" if pd.notna(avg_gdp) else "Tidak tersedia")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Tren Populasi")
    fig_pop = px.line(filtered, x="year", y="population", color="country_name",
                      markers=True, labels={"year":"Tahun","population":"Populasi","country_name":"Negara"})
    fig_pop.update_layout(legend_title_text="Negara")
    st.plotly_chart(fig_pop, use_container_width=True)
with right:
    st.subheader("Tren GDP per Kapita")
    gdp_df = filtered.dropna(subset=["gdp_per_capita"])
    fig_gdp = px.line(gdp_df, x="year", y="gdp_per_capita", color="country_name",
                      markers=True, labels={"year":"Tahun","gdp_per_capita":"GDP per kapita (US$)","country_name":"Negara"})
    st.plotly_chart(fig_gdp, use_container_width=True)

st.subheader(f"Perbandingan Populasi pada Tahun {latest_year}")
fig_bar = px.bar(latest, x="country_name", y="population", color="country_name",
                 labels={"country_name":"Negara","population":"Populasi"})
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Data hasil integrasi SQLite + MongoDB")
st.write("Data indikator dari SQLite digabungkan dengan metadata negara dari MongoDB menggunakan Pandas merge().")

st.dataframe(filtered, use_container_width=True)
st.download_button("Unduh data CSV", filtered.to_csv(index=False).encode("utf-8"),
                   file_name="data_populasi_ekonomi.csv", mime="text/csv")

with st.sidebar:
    st.divider()
    st.caption("Status database")
    st.success("SQLite: data berhasil dibaca")
    try:
        collection = get_mongo_collection()
        if collection is not None:
            st.success("MongoDB: terhubung")
            st.caption(f"Metadata negara: {collection['country_metadata'].count_documents({})}")
            st.caption(f"Log aktivitas: {collection['activity_logs'].count_documents({})}")
        else:
            st.warning("MongoDB: MONGO_URI belum diisi")
    except Exception:
        st.error("MongoDB: gagal terhubung")
