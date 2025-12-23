from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Autotrader API Scraper")

# =============================
# CONFIG
# =============================
AUTOTRADER_API = "https://www.autotrader.ca/api/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

BASE_PARAMS = {
    "dealerId": -1,
    "priceFrom": 0,
    "priceTo": 999999,
    "pageSize": 40,
    "sort": "age",
    "radius": 1000
}

# =============================
# ENDPOINTS
# =============================
@app.get("/")
def root():
    return {
        "service": "Autotrader Scraper",
        "endpoints": [
            "/scrape_autotrader",
            "/health"
        ]
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

        response = requests.get(
            AUTOTRADER_API,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Autotrader API error {response.status_code}"
            )

        data = response.json()
        listings = data.get("listings", [])

        cars = []

        for car in listings:
            cars.append({
                "title": car.get("title"),
                "price": car.get("price"),
                "city": car.get("location"),
                "mileage_km": car.get("mileage"),
                "url": "https://www.autotrader.ca" + car.get("url", ""),
                "image": car.get("imageUrl"),
                "year": car.get("year"),
                "make": car.get("make"),
                "model": car.get("model")
            })

        return {
            "success": True,
            "page": page,
            "count": len(cars),
            "cars": cars
        }

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timeout")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
