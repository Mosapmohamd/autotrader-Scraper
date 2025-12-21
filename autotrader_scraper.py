from fastapi import FastAPI, HTTPException
import requests
import json
import re
import sqlite3
import warnings

warnings.filterwarnings("ignore")

app = FastAPI(title="Autotrader Scraper API")

DB_NAME = "cars.db"

# =============================
# DATABASE
# =============================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS autotrader (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            city TEXT,
            mileage INTEGER,
            image TEXT,
            url TEXT UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS totalcounts (
            source TEXT PRIMARY KEY,
            count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def insert_car(title, price, city, mileage, image, url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO autotrader
        (title, price, city, mileage, image, url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, price, city, mileage, image, url))
    conn.commit()
    conn.close()

def store_count(source, count):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO totalcounts (source, count)
        VALUES (?, ?)
    """, (source, count))
    conn.commit()
    conn.close()

# =============================
# CONSTANTS
# =============================
URL = "https://www.autotrader.ca/lst"

PARAMS = {
    "atype": "C",
    "custtype": "P",
    "cy": "CA",
    "damaged_listing": "exclude",
    "desc": "1",
    "offer": "U",
    "size": "40",
    "sort": "age",
    "ustate": "N,U",
    "zip": "Spanish, ON",
    "zipr": "1000"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

COOKIES = {
    "culture": "en-CA"
}

# =============================
# API ENDPOINT
# =============================
@app.get("/scrape/autotrader")
def scrape_autotrader():
    init_db()

    response = requests.get(
        URL,
        params=PARAMS,
        headers=HEADERS,
        cookies=COOKIES,
        verify=False,
        timeout=30
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Request failed")

    match = re.search(
        r'<script[^>]+type="application/json"[^>]*>(.*?)</script>',
        response.text,
        re.DOTALL
    )

    if not match:
        raise HTTPException(status_code=500, detail="Embedded JSON not found")

    data = json.loads(match.group(1).replace("&quot;", '"'))
    page_props = data["props"]["pageProps"]

    store_count("AutoTrader", page_props["numberOfResults"])

    cars = page_props["listings"]
    saved = 0

    for car in cars:
        v = car.get("vehicle", {})
        p = car.get("price", {})
        l = car.get("location", {})

        title = f"{v.get('modelYear','')} {v.get('make','')} {v.get('model','')}"
        insert_car(
            title=title,
            price=p.get("priceFormatted"),
            city=l.get("city"),
            mileage=v.get("mileageInKm"),
            image=car.get("images",[None])[0],
            url=car.get("url")
        )
        saved += 1

    return {
        "status": "success",
        "cars_saved": saved,
        "total_results": page_props["numberOfResults"]
    }
