from fastapi import FastAPI, HTTPException
import requests
import warnings

warnings.filterwarnings("ignore")

app = FastAPI(title="Autotrader Scraping API")

# =============================
# CONFIGURATION
# =============================
URL = "https://www.autotrader.ca/api/search"

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
# ROOT
# =============================
@app.get("/")
def read_root():
    return {
        "message": "Autotrader Scraping API",
        "endpoints": {
            "/scrape_autotrader": "GET - Scrape Autotrader listings",
            "/health": "GET - Health check"
        }
    }

# =============================
# SCRAPER
# =============================
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
            URL,
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
        total_results = data.get("totalResults")

        cars = []

        for car in listings:
            cars.append({
                "title": car.get("title"),
                "price": car.get("price"),
                "city": car.get("location"),
                "mileage_km": car.get("mileage"),
                "image": car.get("imageUrl"),
                "url": "https://www.autotrader.ca" + car.get("url", ""),
                "description": car.get("description"),
                "make": car.get("make"),
                "model": car.get("model"),
                "year": car.get("year")
            })

        return {
            "success": True,
            "total_results": total_results,
            "scraped_count": len(cars),
            "source": "AutoTrader",
            "cars": cars
        }

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# =============================
# HEALTH CHECK
# =============================
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "autotrader_scraper"}
