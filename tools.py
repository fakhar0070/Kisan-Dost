"""
Function tools for Kisan Dost.

Each tool is a single-responsibility, typed @function_tool with a clear
docstring (the SDK turns the docstring + type hints into the schema the
model sees). Every tool returns a Pydantic model from models.py instead
of a raw string, per the "structured outputs" requirement.
"""

import os
from datetime import datetime

from agents import function_tool
import requests

from data import (
    CROP_TABLE, PEST_TABLE, NPK_REQUIREMENT_KG_PER_ACRE, UREA_N_CONTENT,
    DAP_P_CONTENT, BAG_WEIGHT_KG, UREA_PRICE_PER_BAG_PKR, DAP_PRICE_PER_BAG_PKR,
    MANDI_PRICES, GOVT_SCHEMES,
)
from models import (
    CropRecommendation, CropOption, PestDiagnosis, FertilizerPlan,
    MandiPrice, IrrigationAdvice, ProfitEstimate, GovtSupportInfo,
)


# ---------------------------------------------------------------- Tool 1

@function_tool
def crop_advisor(
    district: str,
    soil_type: str,
    season: str,
    water_availability: str,
    land_size_acres: float,
) -> CropRecommendation:
    """Recommend the best crops for a farmer's conditions.

    Args:
        district: Farmer's district, e.g. "Multan".
        soil_type: Soil type, e.g. "sandy", "clay", "loamy".
        season: Growing season, must be "Rabi" or "Kharif".
        water_availability: One of "low", "medium", "high".
        land_size_acres: Size of the land in acres (must be > 0).
    """
    if land_size_acres <= 0:
        raise ValueError("land_size_acres must be a positive number.")

    season_key = season.strip().lower()
    water_key = water_availability.strip().lower()
    if season_key not in CROP_TABLE:
        raise ValueError("season must be 'Rabi' or 'Kharif'.")
    if water_key not in ("low", "medium", "high"):
        raise ValueError("water_availability must be 'low', 'medium', or 'high'.")

    rows = CROP_TABLE[season_key][water_key]
    options = [
        CropOption(
            crop=row["crop"],
            expected_yield_maund_per_acre=row["yield_maund_per_acre"],
            expected_profit_pkr_per_acre=row["profit_pkr_per_acre"],
            water_requirement=row["water"],
            notes=f"{row['notes']} (soil noted: {soil_type})",
        )
        for row in rows
    ]
    total_profit = sum(o.expected_profit_pkr_per_acre for o in options) // len(options)
    summary = (
        f"For {district} in {season.title()} season with {water_key} water on "
        f"{land_size_acres} acres, top picks average roughly {total_profit:,} PKR/acre profit."
    )
    return CropRecommendation(
        district=district, season=season.title(), recommended_crops=options, summary=summary
    )


# ---------------------------------------------------------------- Tool 2

@function_tool
def pest_doctor(crop: str, symptoms: str) -> PestDiagnosis:
    """Identify a likely pest or disease from a farmer's description and
    give a SAFE, label-rate treatment. Never exceeds recommended dosages
    and never gives human-medical advice.

    Args:
        crop: The crop affected, e.g. "cotton".
        symptoms: Free-text description of what the farmer sees, e.g.
            "cotton leaves curling, tiny white insects underneath".
    """
    if not symptoms or not symptoms.strip():
        raise ValueError("symptoms must be a non-empty description.")

    text = symptoms.lower()
    best_match = None
    for row in PEST_TABLE:
        if any(keyword in text for keyword in row["keywords"]):
            best_match = row
            break

    if best_match is None:
        return PestDiagnosis(
            likely_pest_or_disease="Unable to identify from description",
            confidence="low",
            treatment=(
                "Please describe the symptoms more precisely (colour of insect, "
                "part of plant affected, leaf pattern), or consult your nearest "
                "agriculture extension office for an in-person inspection."
            ),
            safe_dosage="N/A",
            warning="No treatment recommended without a confident diagnosis.",
        )

    confidence = "high" if best_match["crop_hint"] == crop.lower() else "medium"
    return PestDiagnosis(
        likely_pest_or_disease=best_match["name"],
        confidence=confidence,
        treatment=best_match["treatment"],
        safe_dosage=best_match["safe_dosage"],
        reapply_after_days=best_match["reapply_after_days"],
        warning=best_match["warning"],
    )


# ---------------------------------------------------------------- Tool 3

@function_tool
def fertilizer_calculator(crop: str, acres: float) -> FertilizerPlan:
    """Compute NPK need for a crop and convert it into bags of Urea/DAP
    with total cost in PKR.

    Args:
        crop: Crop name, e.g. "wheat", "cotton", "rice".
        acres: Land size in acres (must be > 0).
    """
    if acres <= 0:
        raise ValueError("acres must be a positive number.")

    key = crop.strip().lower()
    if key not in NPK_REQUIREMENT_KG_PER_ACRE:
        raise ValueError(
            f"No fertilizer data for '{crop}'. Known crops: "
            f"{', '.join(NPK_REQUIREMENT_KG_PER_ACRE.keys())}"
        )

    need = NPK_REQUIREMENT_KG_PER_ACRE[key]
    total_n_kg = need["n"] * acres
    total_p_kg = need["p"] * acres

    urea_bags = round(total_n_kg / (UREA_N_CONTENT * BAG_WEIGHT_KG), 1)
    dap_bags = round(total_p_kg / (DAP_P_CONTENT * BAG_WEIGHT_KG), 1)

    total_cost = round(urea_bags * UREA_PRICE_PER_BAG_PKR + dap_bags * DAP_PRICE_PER_BAG_PKR)

    return FertilizerPlan(
        crop=crop,
        acres=acres,
        urea_bags=urea_bags,
        dap_bags=dap_bags,
        total_cost_pkr=total_cost,
        note="Split Urea into 2-3 doses across the season; apply full DAP at sowing.",
    )


# ---------------------------------------------------------------- Tool 4

@function_tool
def mandi_price_lookup(crop: str) -> MandiPrice:
    """Return current/typical wholesale mandi price for a crop.

    Args:
        crop: Crop name, e.g. "wheat", "cotton".
    """
    key = crop.strip().lower()
    if key not in MANDI_PRICES:
        raise ValueError(
            f"No mandi price data for '{crop}'. Known crops: {', '.join(MANDI_PRICES.keys())}"
        )
    row = MANDI_PRICES[key]
    advice = {
        "rising": "Price is trending up — consider holding stock a little longer if storage allows.",
        "falling": "Price is trending down — sell soon rather than waiting.",
        "stable": "Price is stable — sell at your convenience.",
    }[row["trend"]]

    return MandiPrice(
        crop=crop, market=row["market"], price_pkr_per_maund=row["price"],
        trend=row["trend"], advice=advice,
    )


# ---------------------------------------------------------------- Tool 5

@function_tool
def irrigation_weather_advisor(district: str, crop_stage: str) -> IrrigationAdvice:
    """Advise irrigation timing and flag frost/heatwave risk using live
    weather data (Open-Meteo, free, no API key needed). Falls back to a
    generic recommendation if the network/API is unavailable.

    Args:
        district: District or city name, e.g. "Multan".
        crop_stage: Growth stage, e.g. "sowing", "flowering", "grain filling".
    """
    if not district.strip():
        raise ValueError("district must not be empty.")

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": district, "count": 1, "country": "PK"},
            timeout=5,
        ).json()
        if not geo.get("results"):
            raise ValueError("location not found")
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": 3,
                "timezone": "auto",
            },
            timeout=5,
        ).json()

        daily = weather["daily"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        rain = daily["precipitation_sum"]

        forecast_summary = (
            f"Next 3 days in {district}: highs {max_temps}°C, lows {min_temps}°C, "
            f"rainfall {rain} mm."
        )

        warning = None
        if min(min_temps) <= 4:
            warning = "Frost risk detected — consider light irrigation at night to protect crop."
        elif max(max_temps) >= 42:
            warning = "Heatwave risk detected — irrigate early morning/evening, avoid midday stress."

        if sum(rain) > 10:
            irrigation_rec = "Meaningful rain expected — you can skip the next scheduled irrigation."
        else:
            irrigation_rec = f"Little to no rain expected — proceed with normal irrigation for the {crop_stage} stage."

        return IrrigationAdvice(
            district=district, crop_stage=crop_stage, forecast_summary=forecast_summary,
            irrigation_recommendation=irrigation_rec, frost_or_heat_warning=warning,
        )

    except Exception:
        return IrrigationAdvice(
            district=district,
            crop_stage=crop_stage,
            forecast_summary="Live weather data unavailable right now (no internet or API error).",
            irrigation_recommendation=(
                f"As a general rule for the {crop_stage} stage, irrigate every 7-10 days "
                "in normal conditions; check soil moisture at 3-4 inch depth before applying."
            ),
            frost_or_heat_warning=None,
        )


# ---------------------------------------------------------------- Tool 6

@function_tool
def profit_estimator(
    crop: str,
    acres: float,
    total_cost_pkr: int,
    expected_yield_maund_per_acre: float,
    price_pkr_per_maund: int,
) -> ProfitEstimate:
    """Full-season budget: input costs vs expected revenue, net margin,
    and break-even yield.

    Args:
        crop: Crop name.
        acres: Land size in acres (must be > 0).
        total_cost_pkr: Total input cost for the whole season in PKR (must be >= 0).
        expected_yield_maund_per_acre: Expected yield in maunds per acre.
        price_pkr_per_maund: Expected selling price per maund in PKR.
    """
    if acres <= 0:
        raise ValueError("acres must be a positive number.")
    if total_cost_pkr < 0 or price_pkr_per_maund < 0 or expected_yield_maund_per_acre < 0:
        raise ValueError("cost, price, and yield must not be negative.")

    total_yield_maund = expected_yield_maund_per_acre * acres
    expected_revenue = round(total_yield_maund * price_pkr_per_maund)
    net_margin = expected_revenue - total_cost_pkr

    break_even_yield = (
        round(total_cost_pkr / (price_pkr_per_maund * acres), 2)
        if price_pkr_per_maund > 0 and acres > 0
        else 0.0
    )

    return ProfitEstimate(
        crop=crop, acres=acres, total_cost_pkr=total_cost_pkr,
        expected_revenue_pkr=expected_revenue, net_margin_pkr=net_margin,
        break_even_yield_maund_per_acre=break_even_yield,
    )


# ---------------------------------------------------------------- Tool 7

@function_tool
def govt_support_finder(province: str, need: str) -> GovtSupportInfo:
    """Surface relevant government schemes (Kisan Card, subsidised
    fertilizer, agri loans) for a farmer's province and stated need.

    Args:
        province: One of "Punjab", "Sindh", "KPK", "Balochistan".
        need: What the farmer needs help with, e.g. "fertilizer subsidy", "loan".
    """
    key = province.strip().lower()
    if key not in GOVT_SCHEMES:
        raise ValueError("province must be one of: Punjab, Sindh, KPK, Balochistan.")

    return GovtSupportInfo(
        province=province.title(),
        relevant_schemes=GOVT_SCHEMES[key],
        how_to_apply=(
            f"Visit your nearest Agriculture Department office in {province} with your CNIC and "
            "land ownership/tenancy documents, or register online on the provincial Kisan portal "
            f"if you're specifically looking for: {need}."
        ),
    )
