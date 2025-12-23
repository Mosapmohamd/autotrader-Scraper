from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Autotrader Scraping API")

URL = "https://www.autotrader.ca/legacy/api/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.autotrader.ca/",
    "Origin": "https://www.autotrader.ca"
}

BASE_PARAMS = {
    "dealerId": -1,
    "priceFrom": 0,
    "priceTo": 999999,
    "pageSize": 40,
    "sort": "age",
    "radius": 1000
}

@app.get("/scrape_autotrader")
def scrape_autotrader(
    postal_code: str = "N5X0E2",
    page: int = 1
):
    try:
        params = BASE_PARAMS.copy()
        params.update({
            "postalCode": postal_code,
            "page": page
        })

        r = requests.get(
            URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        if r.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Autotrader API error {r.status_code}"
            )

        data = r.json()
        listings = data.get("listings", [])

        cars = []

        for car in listings:
            cars.append({
                "title": car.get("title"),
                "price": car.get("price"),
                "city": car.get("location"),
                "mileage_km": car.get("mileage"),
                "image": car.get("imageUrl"),
                "url": "https://www.autotrader.ca" + car.get("url", ""),
                "year": car.get("year"),
                "make": car.get("make"),
                "model": car.get("model")
            })

        return {
            "success": True,
            "count": len(cars),
            "cars": cars
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
