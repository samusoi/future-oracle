def calculate_price_score(price_change: float) -> int:
    """
    Оценивает изменение цены Bitcoin за 24 часа.

    Максимум: +30
    Минимум: -30
    """

    if price_change >= 2:
        return 30

    if price_change >= 0.5:
        return 15

    if price_change > -0.5:
        return 0

    if price_change > -2:
        return -15

    return -30


def calculate_volume_score(volume: float) -> int:
    """
    Оценивает торговый объём Bitcoin.

    Объём влияет на силу сигнала.
    """

    if volume >= 25_000_000_000:
        return 20

    if volume >= 15_000_000_000:
        return 10

    if volume >= 8_000_000_000:
        return 0

    return -10


def calculate_fear_greed_score(value: int) -> int:
    """
    Оценивает индекс Fear & Greed.
    """

    if value <= 24:
        return -15

    if value <= 44:
        return -5

    if value <= 55:
        return 0

    if value <= 74:
        return 10

    return 15


def calculate_prediction(
    price_change: float,
    volume: float,
    fear_greed_value: int
) -> dict:
    """
    Основная модель Future Oracle.

    Использует три сигнала:

    1. Изменение цены
    2. Торговый объём
    3. Fear & Greed

    Максимальный score: +65
    Минимальный score: -55
    """

    # --------------------------------------------------
    # SCORE
    # --------------------------------------------------

    price_score = calculate_price_score(price_change)

    volume_score = calculate_volume_score(volume)

    fear_greed_score = calculate_fear_greed_score(
        fear_greed_value
    )

    total_score = (
        price_score
        + volume_score
        + fear_greed_score
    )

    # --------------------------------------------------
    # DIRECTION
    # --------------------------------------------------

    if total_score >= 45:
        direction = "STRONG_UP"

    elif total_score >= 20:
        direction = "UP"

    elif total_score <= -45:
        direction = "STRONG_DOWN"

    elif total_score <= -20:
        direction = "DOWN"

    else:
        direction = "NEUTRAL"

    # --------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------

    confidence = min(
        95,
        50 + abs(total_score) * 0.7
    )

    confidence = round(confidence)

    # --------------------------------------------------
    # RISK
    # --------------------------------------------------

    if abs(total_score) < 15:
        risk = "VERY_HIGH"

    elif abs(total_score) < 30:
        risk = "HIGH"

    elif abs(total_score) < 45:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    # --------------------------------------------------
    # REASONS
    # --------------------------------------------------

    reasons = []

    # Цена

    if price_score > 0:

        reasons.append(
            f"Bitcoin вырос на "
            f"{price_change:.2f}% за последние 24 часа."
        )

    elif price_score < 0:

        reasons.append(
            f"Bitcoin снизился на "
            f"{abs(price_change):.2f}% за последние 24 часа."
        )

    else:

        reasons.append(
            "Изменение цены Bitcoin находится "
            "около нулевого уровня."
        )

    # Объём

    if volume_score >= 20:

        reasons.append(
            "Торговый объём очень высокий — "
            "рынок демонстрирует сильную активность."
        )

    elif volume_score > 0:

        reasons.append(
            "Торговый объём находится "
            "на повышенном уровне."
        )

    elif volume_score == 0:

        reasons.append(
            "Торговый объём находится "
            "на среднем уровне."
        )

    else:

        reasons.append(
            "Торговый объём относительно низкий."
        )

    # Fear & Greed

    if fear_greed_value <= 24:

        reasons.append(
            f"Fear & Greed = {fear_greed_value}/100 — "
            "экстремальный страх."
        )

    elif fear_greed_value <= 44:

        reasons.append(
            f"Fear & Greed = {fear_greed_value}/100 — "
            "рынок находится в зоне страха."
        )

    elif fear_greed_value <= 55:

        reasons.append(
            f"Fear & Greed = {fear_greed_value}/100 — "
            "нейтральное настроение."
        )

    elif fear_greed_value <= 74:

        reasons.append(
            f"Fear & Greed = {fear_greed_value}/100 — "
            "положительное настроение рынка."
        )

    else:

        reasons.append(
            f"Fear & Greed = {fear_greed_value}/100 — "
            "сильный оптимизм."
        )

    # Итог

    reasons.append(
        f"Итоговый score модели: {total_score}."
    )

    if direction == "STRONG_UP":

        reasons.append(
            "Несколько сигналов одновременно указывают "
            "на сильное движение вверх."
        )

    elif direction == "UP":

        reasons.append(
            "Большинство сигналов указывает "
            "на движение вверх."
        )

    elif direction == "STRONG_DOWN":

        reasons.append(
            "Несколько сигналов одновременно указывают "
            "на сильное движение вниз."
        )

    elif direction == "DOWN":

        reasons.append(
            "Большинство сигналов указывает "
            "на движение вниз."
        )

    else:

        reasons.append(
            "Сигналы недостаточно сильные для "
            "направленного прогноза."
        )

    return {
        "direction": direction,
        "confidence": confidence,
        "risk": risk,
        "score": total_score,

        "price_score": price_score,
        "volume_score": volume_score,
        "fear_greed_score": fear_greed_score,

        "arguments": reasons
    }