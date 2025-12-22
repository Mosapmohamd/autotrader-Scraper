from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Autotrader Scraping API")

URL = "https://www.autotrader.ca/rest/searchresults"

PAYLOAD = {
    "atype": "C",
    "custtype": "P",
    "cy": "CA",
    "damaged_listing": "exclude",
    "desc": 1,
    "lat": 42.98014450073242,
    "lon": -81.23054504394531,
    "offer": ["N", "U"],
    "search_id": "1tr3yb0krmj",
    "size": 20,
    "sort": "age",
    "ustate": ["N", "U"],
    "zip": "N6B3B4 London, ON",
    "zipr": 1000
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.autotrader.ca/"
}

@app.get("/scrape_autotrader")
def scrape_autotrader():
    r = requests.post(
        URL,
        json=PAYLOAD,
        headers=HEADERS,
        timeout=30
    )

    if r.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Autotrader request failed: {r.status_code}"
        )

    data = r.json()
    listings = data.get("listings", [])
    results = []

    for car in listings:
        vehicle = car.get("vehicle", {})
        price = car.get("price", {})
        location = car.get("location", {})

        images = car.get("images") or []
        image = images[0] if images else None

        results.append({
            "title": f"{vehicle.get('modelYear', '')} "
                     f"{vehicle.get('make', '')} "
                     f"{vehicle.get('model', '')}",
            "price": price.get("priceFormatted"),
            "mileage_km": vehicle.get("mileageInKm"),
            "city": location.get("city"),
            "image": image,
            "url": car.get("url")
        })

    return {
        "count": len(results),
        "cars": results
    }
