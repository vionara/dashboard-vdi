import os
from datetime import datetime, timezone
import io

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine, text

load_dotenv()
st.set_page_config(page_title="Dashboard Populasi & Ekonomi", page_icon="🌍", layout="wide")

DB_PATH = os.getenv("SQLITE_PATH", "database/world_data.db")

# ==================== DATA OTOMATIS ====================
EMBEDDED_CSV = """country_code,country_name,year,population,gdp_per_capita,region,income_group
IDN,Indonesia,2010,246305322.0,3065.68,Asia Tenggara,Menengah
MYS,Malaysia,2010,28655776.0,8899.35,Asia Tenggara,Menengah
SGP,Singapore,2010,5076732.0,47236.68,Asia Tenggara,Tinggi
THA,Thailand,2010,68579447.0,4973.86,Asia Tenggara,Menengah
USA,United States,2010,309378227.0,48642.63,Amerika Utara,Tinggi
IDN,Indonesia,2011,249470032.0,3579.46,Asia Tenggara,Menengah
MYS,Malaysia,2011,29162039.0,10217.11,Asia Tenggara,Menengah
SGP,Singapore,2011,5183688.0,53891.46,Asia Tenggara,Tinggi
THA,Thailand,2011,69007208.0,5373.62,Asia Tenggara,Menengah
USA,United States,2011,311839461.0,50024.88,Amerika Utara,Tinggi
IDN,Indonesia,2012,252643534.0,3634.33,Asia Tenggara,Menengah
MYS,Malaysia,2012,29661448.0,10659.85,Asia Tenggara,Menengah
SGP,Singapore,2012,5312437.0,55547.46,Asia Tenggara,Tinggi
THA,Thailand,2012,69440939.0,5780.05,Asia Tenggara,Menengah
USA,United States,2012,314207914.0,51784.42,Amerika Utara,Tinggi
IDN,Indonesia,2013,255829675.0,3564.33,Asia Tenggara,Menengah
MYS,Malaysia,2013,30149015.0,10866.50,Asia Tenggara,Menengah
SGP,Singapore,2013,5399162.0,57007.82,Asia Tenggara,Tinggi
THA,Thailand,2013,69857904.0,6078.69,Asia Tenggara,Menengah
USA,United States,2013,316499882.0,53291.13,Amerika Utara,Tinggi
IDN,Indonesia,2014,259021975.0,3436.57,Asia Tenggara,Menengah
MYS,Malaysia,2014,30606479.0,11183.67,Asia Tenggara,Menengah
SGP,Singapore,2014,5469724.0,57564.87,Asia Tenggara,Tinggi
THA,Thailand,2014,70258071.0,5861.54,Asia Tenggara,Menengah
USA,United States,2014,318854492.0,55123.85,Amerika Utara,Tinggi
IDN,Indonesia,2015,262220184.0,3284.18,Asia Tenggara,Menengah
MYS,Malaysia,2015,31068834.0,9643.14,Asia Tenggara,Menengah
SGP,Singapore,2015,5535002.0,55646.61,Asia Tenggara,Tinggi
THA,Thailand,2015,70626946.0,5740.91,Asia Tenggara,Menengah
USA,United States,2015,321287440.0,56762.73,Amerika Utara,Tinggi
IDN,Indonesia,2016,265424561.0,3515.65,Asia Tenggara,Menengah
MYS,Malaysia,2016,31526438.0,9508.24,Asia Tenggara,Menengah
SGP,Singapore,2016,5607283.0,56894.27,Asia Tenggara,Tinggi
THA,Thailand,2016,70968138.0,5894.94,Asia Tenggara,Menengah
USA,United States,2016,323674602.0,57866.74,Amerika Utara,Tinggi
IDN,Indonesia,2017,268623639.0,3787.53,Asia Tenggara,Menengah
MYS,Malaysia,2017,31975806.0,10258.74,Asia Tenggara,Menengah
SGP,Singapore,2017,5612253.0,61176.08,Asia Tenggara,Tinggi
THA,Thailand,2017,71278020.0,6492.33,Asia Tenggara,Menengah
USA,United States,2017,325719178.0,59907.75,Amerika Utara,Tinggi
IDN,Indonesia,2018,271790408.0,3837.58,Asia Tenggara,Menengah
MYS,Malaysia,2018,32399271.0,11373.23,Asia Tenggara,Menengah
SGP,Singapore,2018,5638676.0,66835.85,Asia Tenggara,Tinggi
THA,Thailand,2018,71557635.0,7168.04,Asia Tenggara,Menengah
USA,United States,2018,327435774.0,62823.31,Amerika Utara,Tinggi
IDN,Indonesia,2019,274859011.0,4073.59,Asia Tenggara,Menengah
MYS,Malaysia,2019,32801374.0,11414.83,Asia Tenggara,Menengah
SGP,Singapore,2019,5703569.0,65831.14,Asia Tenggara,Tinggi
THA,Thailand,2019,71801279.0,7714.89,Asia Tenggara,Menengah
USA,United States,2019,329064917.0,65120.39,Amerika Utara,Tinggi
IDN,Indonesia,2020,277534122.0,3803.96,Asia Tenggara,Menengah
MYS,Malaysia,2020,33199393.0,10412.33,Asia Tenggara,Menengah
SGP,Singapore,2020,5685807.0,61276.01,Asia Tenggara,Tinggi
THA,Thailand,2020,71997328.0,7089.79,Asia Tenggara,Menengah
USA,United States,2020,331511512.0,63528.63,Amerika Utara,Tinggi
IDN,Indonesia,2021,279965000.0,4256.32,Asia Tenggara,Menengah
MYS,Malaysia,2021,33573874.0,11371.97,Asia Tenggara,Menengah
SGP,Singapore,2021,5453566.0,77710.05,Asia Tenggara,Tinggi
THA,Thailand,2021,72120000.0,6908.76,Asia Tenggara,Menengah
USA,United States,2021,332031554.0,70219.47,Amerika Utara,Tinggi
IDN,Indonesia,2022,282477584.0,4690.65,Asia Tenggara,Menengah
MYS,Malaysia,2022,33938221.0,12362.88,Asia Tenggara,Menengah
SGP,Singapore,2022,5637008.0,88446.99,Asia Tenggara,Tinggi
THA,Thailand,2022,72210000.0,7494.46,Asia Tenggara,Menengah
USA,United States,2022,333287557.0,76329.58,Amerika Utara,Tinggi
IDN,Indonesia,2023,284988000.0,4940.54,Asia Tenggara,Menengah
MYS,Malaysia,2023,34308525.0,11993.18,Asia Tenggara,Menengah
SGP,Singapore,2023,5917600.0,84734.00,Asia Tenggara,Tinggi
THA,Thailand,2023,72280000.0,7171.75,Asia Tenggara,Menengah
USA,United States,2023,334914895.0,81695.19,Amerika Utara,Tinggi
"""

# Bikin database SQLite otomatis saat itu juga
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
if not os.path.exists(DB_PATH):
    engine_init = create_engine(f"sqlite:///{DB_PATH}")
    df_raw = pd.read_csv(io.StringIO(EMBEDDED_CSV.strip()))
    cols = ["country_code", "country_name", "year", "population", "gdp_per_capita"]
    df_raw[cols].to_sql("indicators", engine_init, if_exists="replace", index=False)

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

    db = get_mongo_collection()
    if db is None:
        # Fallback metadata jika tanpa MongoDB
        metadata_dict = {
            "IDN": ("Asia Tenggara", "Menengah"),
            "MYS": ("Asia Tenggara", "Menengah"),
            "SGP": ("Asia Tenggara", "Tinggi"),
            "THA": ("Asia Tenggara", "Menengah"),
            "USA": ("Amerika Utara", "Tinggi"),
        }
        data["region"] = data["country_code"].map(lambda x: metadata_dict.get(x, ("Lainnya", ""))[0])
        data["income_group"] = data["country_code"].map(lambda x: metadata_dict.get(x, ("", "Tidak tersedia"))[1])
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
                {"country_code":"USA","region":"Amerika Utara","income_group":"Tinggi"},
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
        pass

st.title("🌍 Dashboard Analisis Populasi dan Ekonomi Dunia")
st.caption("Integrasi SQLite + MongoDB | Python, Pandas, Plotly, dan Streamlit")

try:
    df = load_data()
except Exception as exc:
    st.error("Gagal membaca database.")
    st.exception(exc)
    st.stop()

if df.empty:
    st.warning("Belum ada data.")
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
