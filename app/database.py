import sqlite3
from datetime import datetime


DATABASE_NAME = "future_oracle.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Рыночные данные
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT NOT NULL,
            price REAL NOT NULL,
            price_change REAL NOT NULL,
            volume REAL NOT NULL,
            fear_greed_value INTEGER NOT NULL,
            fear_greed_classification TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Прогнозы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_data_id INTEGER,
            asset TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk TEXT NOT NULL,
            score INTEGER NOT NULL,
            price_score INTEGER NOT NULL,
            volume_score INTEGER NOT NULL,
            fear_greed_score INTEGER NOT NULL,
            reasons TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (market_data_id)
                REFERENCES market_data(id)
        )
    """)

    # ДОБАВЬ ВОТ ЭТО
    try:
        cursor.execute("""
            ALTER TABLE predictions
            ADD COLUMN volume_score INTEGER NOT NULL DEFAULT 0
        """)
    except sqlite3.OperationalError:
        pass

    # Результаты проверки прогнозов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER NOT NULL,
            predicted_price REAL NOT NULL,
            actual_price REAL NOT NULL,
            actual_change_percent REAL NOT NULL,
            result TEXT NOT NULL,
            checked_at TEXT NOT NULL,
            FOREIGN KEY (prediction_id)
                REFERENCES predictions(id)
        )
    """)

    connection.commit()
    connection.close()


def save_market_data(
    asset,
    price,
    price_change,
    volume,
    fear_greed_value,
    fear_greed_classification
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO market_data (
            asset,
            price,
            price_change,
            volume,
            fear_greed_value,
            fear_greed_classification,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        asset,
        price,
        price_change,
        volume,
        fear_greed_value,
        fear_greed_classification,
        datetime.now().isoformat()
    ))

    market_data_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return market_data_id


def save_prediction(
    market_data_id,
    asset,
    prediction,
    confidence,
    risk,
    score,
    reasons,
    price_score,
    volume_score,
    fear_greed_score
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO predictions (
            market_data_id,
            asset,
            prediction,
            confidence,
            risk,
            score,
            price_score,
            volume_score,
            fear_greed_score,
            reasons,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        market_data_id,
        asset,
        prediction,
        confidence,
        risk,
        score,
        price_score,
        volume_score,
        fear_greed_score,
        "\n".join(reasons),
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()

def get_latest_market_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            asset,
            price,
            price_change,
            volume,
            fear_greed_value,
            fear_greed_classification,
            created_at
        FROM market_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "asset": row[1],
        "price": row[2],
        "price_change": row[3],
        "volume": row[4],
        "fear_greed_value": row[5],
        "fear_greed_classification": row[6],
        "created_at": row[7]
    }


def get_latest_predictions(limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            asset,
            prediction,
            confidence,
            risk,
            score,
            price_score,
            fear_greed_score,
            reasons,
            created_at
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "asset": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "risk": row[4],
            "score": row[5],
            "price_score": row[6],
            "fear_greed_score": row[7],
            "reasons": row[8].split("\n"),
            "created_at": row[9]
        }
        for row in rows
    ]


def get_market_history(limit=50):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            asset,
            price,
            price_change,
            volume,
            fear_greed_value,
            fear_greed_classification,
            created_at
        FROM market_data
        ORDER BY id ASC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "asset": row[1],
            "price": row[2],
            "price_change": row[3],
            "volume": row[4],
            "fear_greed_value": row[5],
            "fear_greed_classification": row[6],
            "created_at": row[7]
        }
        for row in rows
    ]


def get_prediction_history(limit=50):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.market_data_id,
            p.asset,
            p.prediction,
            p.confidence,
            p.risk,
            p.score,
            p.price_score,
            p.fear_greed_score,
            p.created_at,
            m.price,
            m.price_change,
            m.volume,
            m.fear_greed_value
        FROM predictions p
        LEFT JOIN market_data m
            ON p.market_data_id = m.id
        ORDER BY p.id ASC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "market_data_id": row[1],
            "asset": row[2],
            "prediction": row[3],
            "confidence": row[4],
            "risk": row[5],
            "score": row[6],
            "price_score": row[7],
            "fear_greed_score": row[8],
            "created_at": row[9],
            "price": row[10],
            "price_change": row[11],
            "volume": row[12],
            "fear_greed_value": row[13]
        }
        for row in rows
    ]

def evaluate_predictions(
    current_price,
    horizon_minutes=60,
    neutral_threshold=0.5
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.prediction,
            m.price,
            p.created_at
        FROM predictions p
        JOIN market_data m
            ON p.market_data_id = m.id
        LEFT JOIN prediction_results r
            ON p.id = r.prediction_id
        WHERE
            r.id IS NULL
            AND datetime(p.created_at) <= datetime('now', ?)
        ORDER BY p.id ASC
    """, (
        f"-{horizon_minutes} minutes",
    ))

    predictions = cursor.fetchall()

    evaluated = []

    for prediction_id, prediction, predicted_price, created_at in predictions:

        if predicted_price is None or predicted_price == 0:
            continue

        actual_change_percent = (
            (current_price - predicted_price)
            / predicted_price
        ) * 100

        if actual_change_percent > neutral_threshold:
            actual_direction = "UP"

        elif actual_change_percent < -neutral_threshold:
            actual_direction = "DOWN"

        else:
            actual_direction = "NEUTRAL"

        if prediction in ("UP", "STRONG_UP") and actual_direction == "UP":
          result = "CORRECT"

        elif prediction in ("DOWN", "STRONG_DOWN") and actual_direction == "DOWN":
           result = "CORRECT"

        elif prediction == "NEUTRAL" and actual_direction == "NEUTRAL":
            result = "CORRECT"

        else:
            result = "WRONG"

        cursor.execute("""
            INSERT INTO prediction_results (
                prediction_id,
                predicted_price,
                actual_price,
                actual_change_percent,
                result,
                checked_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            prediction_id,
            predicted_price,
            current_price,
            actual_change_percent,
            result,
            datetime.now().isoformat()
        ))

        evaluated.append({
            "prediction_id": prediction_id,
            "prediction": prediction,
            "predicted_price": predicted_price,
            "actual_price": current_price,
            "actual_change_percent": actual_change_percent,
            "actual_direction": actual_direction,
            "result": result
        })

    connection.commit()
    connection.close()

    return evaluated

def get_prediction_accuracy():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN result = 'CORRECT'
                    THEN 1
                    ELSE 0
                END
            ) AS correct,
            SUM(
                CASE
                    WHEN result = 'WRONG'
                    THEN 1
                    ELSE 0
                END
            ) AS wrong
        FROM prediction_results
    """)

    row = cursor.fetchone()

    connection.close()

    total = row[0] or 0
    correct = row[1] or 0
    wrong = row[2] or 0

    if total > 0:
        accuracy = round(
            (correct / total) * 100,
            2
        )
    else:
        accuracy = 0

    return {
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "accuracy": accuracy
    }