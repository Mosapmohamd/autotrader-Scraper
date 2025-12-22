from fastapi import FastAPI, HTTPException
import requests
import json
import re

app = FastAPI(title="Autotrader Scraping API")

URL = "https://www.autotrader.ca/lst"

PARAMS = {
    "atype": "C",
    "custtype": "P",
    "cy": "CA",
    "desc":1,
    "lat":"42.98014450073242",
    "lon":"-81.23054504394531",
    "offer": "N",
    "size": "40",
    "sort": "age",
    "zip": "N6B3B4 London, ON",
    "zipr": "1000"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@app.get("/scrape_autotrader")
def scrape_autotrader():

    r = requests.get(
        URL,
        params=PARAMS,
        headers=HEADERS,
        timeout=30
    )

    if r.status_code != 200:
        raise HTTPException(500, "Request failed")

    match = re.search(
        r'<script[^>]+type="application/json"[^>]*>(.*?)</script>',
        r.text,
        re.DOTALL
    )

    if not match:
        raise HTTPException(500, "JSON not found")

    data = json.loads(match.group(1).replace("&quot;", '"'))
    listings = data["props"]["pageProps"]["listings"]

    results = []

    for car in listings:
        v = car.get("vehicle", {})
        p = car.get("price", {})
        l = car.get("location", {})

        images = car.get("images") or []
        image = images[0] if images else None

        results.append({
            "title": f"{v.get('modelYear','')} {v.get('make','')} {v.get('model','')}",
            "price": p.get("priceFormatted"),
            "mileage_km": v.get("mileageInKm"),
            "city": l.get("city"),
            "image": image,
            "url": car.get("url")
        })

    return {
        "count": len(results),
        "cars": results
    }




