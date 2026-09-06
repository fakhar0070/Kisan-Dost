"""
Agent definitions for Kisan Dost: one triage agent that routes to four
specialist agents. This is the multi-agent handoff structure the
hackathon brief calls the "single biggest complexity differentiator".
"""

from agents import Agent
from model_setup import MODEL_NAME
from tools import (
    crop_advisor,
    fertilizer_calculator,
    irrigation_weather_advisor,
    pest_doctor,
    mandi_price_lookup,
    govt_support_finder,
    profit_estimator,
)
from guardrails import farming_topic_guardrail, pesticide_safety_guardrail

BASE_STYLE = (
    "Reply in simple Urdu-English mix (the way Pakistani farmers actually speak), "
    "keep answers short, practical, and specific with numbers. "
    "Always use the farmer's remembered profile (district, land size, current crop) "
    "from context instead of asking again if it's already known."
)

agronomy_agent = Agent(
    name="Agronomy Agent",
    instructions=(
        f"{BASE_STYLE} You specialise in what to plant, fertilizer plans, and "
        "irrigation/weather timing. Use crop_advisor, fertilizer_calculator, and "
        "irrigation_weather_advisor as needed. Always give concrete numbers."
    ),
    tools=[crop_advisor, fertilizer_calculator, irrigation_weather_advisor],
    model=MODEL_NAME,
)

pest_agent = Agent(
    name="Pest Doctor Agent",
    instructions=(
        f"{BASE_STYLE} You specialise in diagnosing crop pests/diseases from the farmer's "
        "description and giving SAFE, label-rate treatment using pest_doctor. "
        "Never exceed the safe dosage the tool returns. Never give advice for human or "
        "animal illnesses — that is out of scope; tell the farmer to see a doctor/vet instead."
    ),
    tools=[pest_doctor],
    output_guardrails=[pesticide_safety_guardrail],
    model=MODEL_NAME,
)

market_agent = Agent(
    name="Market Agent",
    instructions=(
        f"{BASE_STYLE} You specialise in mandi prices and government support schemes. "
        "Use mandi_price_lookup and govt_support_finder as needed."
    ),
    tools=[mandi_price_lookup, govt_support_finder],
    model=MODEL_NAME,
)

finance_agent = Agent(
    name="Finance Agent",
    instructions=(
        f"{BASE_STYLE} You specialise in season budgets: costs vs revenue, net margin, "
        "and break-even yield. Use profit_estimator. If the farmer hasn't given you "
        "cost/yield/price numbers yet, ask for exactly the missing ones."
    ),
    tools=[profit_estimator],
    model=MODEL_NAME,
)

triage_agent = Agent(
    name="Kisan Dost Triage",
    instructions=(
        f"{BASE_STYLE} You are the first point of contact for a Pakistani farmer. "
        "Understand what they need and call the right specialist tool:\n"
        "- agronomy_agent: what to plant, fertilizer plans, irrigation/weather.\n"
        "- pest_doctor_agent: pest or disease symptoms on a crop.\n"
        "- market_agent: mandi prices, government schemes/subsidies.\n"
        "- finance_agent: profit/budget/break-even questions.\n"
        "If the question spans more than one area, call the most relevant tool(s) "
        "and combine their answers, handling the most urgent part first."
    ),
    tools=[
        agronomy_agent.as_tool(
            tool_name="agronomy_agent",
            tool_description="Ask the Agronomy Agent about what to plant, fertilizer plans, or irrigation/weather timing.",
        ),
        pest_agent.as_tool(
            tool_name="pest_doctor_agent",
            tool_description="Ask the Pest Doctor Agent to diagnose a crop pest/disease and give a safe treatment.",
        ),
        market_agent.as_tool(
            tool_name="market_agent",
            tool_description="Ask the Market Agent about mandi prices or government support schemes.",
        ),
        finance_agent.as_tool(
            tool_name="finance_agent",
            tool_description="Ask the Finance Agent about season budget, profit, or break-even yield.",
        ),
    ],
    input_guardrails=[farming_topic_guardrail],
    model=MODEL_NAME,
)
