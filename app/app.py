from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

from app.database import (
    init_database,
    save_market_data,
    save_prediction,
    get_latest_market_data,
    get_latest_predictions,
    get_market_history,
    get_prediction_history,
    evaluate_predictions,
    get_prediction_accuracy,
        
)
from app.predictor import calculate_prediction


app = FastAPI()

# Инициализируем базу данных
init_database()

# Шаблоны HTML
templates = Jinja2Templates(directory="templates")


# --------------------------------------------------
# Главная страница
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# --------------------------------------------------
# API прогноза
# --------------------------------------------------

@app.get("/api/prediction")
async def prediction():

    # ==================================================
    # ИСТОЧНИК №1 — COINGECKO
    # ==================================================

    crypto_url = "https://api.coingecko.com/api/v3/simple/price"

    crypto_params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_24hr_vol": "true"
    }

    crypto_response = requests.get(
        crypto_url,
        params=crypto_params,
        timeout=10
    )

    crypto_response.raise_for_status()

    crypto_data = crypto_response.json()

    bitcoin = crypto_data["bitcoin"]

    price = bitcoin["usd"]
    price_change = bitcoin["usd_24h_change"]
    volume = bitcoin["usd_24h_vol"]

# ==================================================
# ПРОВЕРЯЕМ СТАРЫЕ ПРОГНОЗЫ
# ==================================================

    evaluate_predictions(
    current_price=price,
    horizon_minutes=60
)

    # ==================================================
    # ИСТОЧНИК №2 — FEAR & GREED INDEX
    # ==================================================

    fear_greed_url = "https://api.alternative.me/fng/"

    fear_greed_response = requests.get(
        fear_greed_url,
        timeout=10
    )

    fear_greed_response.raise_for_status()

    fear_greed_data = fear_greed_response.json()

    market_mood = fear_greed_data["data"][0]

    fear_greed_value = int(market_mood["value"])

    fear_greed_classification = (
        market_mood["value_classification"]
    )


    # ==================================================
    # РАССЧИТЫВАЕМ ПРОГНОЗ
    # ==================================================

    prediction_result = calculate_prediction(
    price_change=price_change,
    volume=volume,
    fear_greed_value=fear_greed_value
)


    # ==================================================
    # СОХРАНЯЕМ ДАННЫЕ В БАЗУ
    # ==================================================

    market_data_id = save_market_data(
    asset="Bitcoin",
    price=price,
    price_change=price_change,
    volume=volume,
    fear_greed_value=fear_greed_value,
    fear_greed_classification=fear_greed_classification
)

    save_prediction(
    market_data_id=market_data_id,
    asset="Bitcoin",
    prediction=prediction_result["direction"],
    confidence=prediction_result["confidence"],
    risk=prediction_result["risk"],
    score=prediction_result["score"],
    reasons=prediction_result["arguments"],
    price_score=prediction_result["price_score"],
    volume_score=prediction_result["volume_score"],
    fear_greed_score=prediction_result["fear_greed_score"]
)



    # ==================================================
    # ВОЗВРАЩАЕМ РЕЗУЛЬТАТ
    # ==================================================

    return {
        "asset": "Bitcoin",

        "prediction": prediction_result["direction"],

        "confidence": prediction_result["confidence"],

        "risk": prediction_result["risk"],

        "score": prediction_result["score"],

        "reasons": prediction_result["arguments"],

        "data": {
            "price_usd": price,

            "change_24h_percent": price_change,

            "volume_24h_usd": volume,

            "fear_greed_value": fear_greed_value,

            "fear_greed_classification": fear_greed_classification
        },

        "scoring": {
            "price_score": prediction_result["price_score"],

            "fear_greed_score": (
                prediction_result["fear_greed_score"]
            )
        }
    }


# --------------------------------------------------
# API истории рынка
# --------------------------------------------------


@app.get("/api/history")
async def history():

    predictions = get_latest_predictions(limit=20)

    return {
        "count": len(predictions),
        "predictions": predictions
    }


# --------------------------------------------------
# API данных для графиков
# --------------------------------------------------

@app.get("/api/history/predictions")
async def history_predictions():

    prediction_history = get_prediction_history(limit=50)

    data = []

    for item in prediction_history:

        data.append({
            "price": item["price"],
            "fear_greed_value": item["fear_greed_value"],
            "score": item["score"],
            "created_at": item["created_at"]
        })

    return {
        "count": len(data),
        "data": data
    }
# --------------------------------------------------
# API точности модели
# --------------------------------------------------

@app.get("/api/accuracy")
async def accuracy():

    result = get_prediction_accuracy()

    return result