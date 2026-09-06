"""
Guardrails for Kisan Dost.

Input guardrail: rejects requests that are off-topic (not about farming)
or that ask for human-medical advice disguised as a farming question.

Output guardrail: double-checks that any pesticide dosage the agent is
about to send back stays within the safe label-rate limits defined in
data.py, and blocks anything that reads like human-medical advice.
"""

import re

from agents import (
    Agent,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
    input_guardrail,
    output_guardrail,
)
from model_setup import MODEL_NAME


_topic_guard_agent = Agent(
    name="Topic Guardrail Agent",
    instructions=(
        "You are a strict CLASSIFIER, not an assistant that answers farming questions. "
        "Do NOT answer, explain, treat, diagnose, or give any advice about the message. "
        "Do NOT write any prose, tables, explanations, or extra words.\n\n"
        "Reply with EXACTLY one line in this exact format, nothing else:\n"
        "FARMING=<YES|NO> MEDICAL=<YES|NO>\n\n"
        "FARMING=YES if the message is about farming/agriculture (crops, pests, fertilizer, "
        "weather, mandi prices, government agri schemes), else FARMING=NO.\n"
        "MEDICAL=YES if the user is asking for medical advice for a HUMAN or ANIMAL illness "
        "(not a crop pest/disease), else MEDICAL=NO.\n"
        "Even if the message describes a crop pest problem, DO NOT diagnose or treat it — "
        "just classify it and output the one line.\n"
        "Example output: FARMING=YES MEDICAL=NO"
    ),
    model=MODEL_NAME,
)

_CLASSIFY_PATTERN = re.compile(r"FARMING=(YES|NO)\s+MEDICAL=(YES|NO)", re.IGNORECASE)


@input_guardrail
async def farming_topic_guardrail(
    ctx: RunContextWrapper, agent: Agent, user_input: str
) -> GuardrailFunctionOutput:
    """Blocks off-topic requests and requests for human/animal medical advice."""
    result = await Runner.run(_topic_guard_agent, user_input, context=ctx.context)
    raw = str(result.final_output or "")
    match = _CLASSIFY_PATTERN.search(raw)

    if match:
        is_farming_related = match.group(1).upper() == "YES"
        is_human_medical_request = match.group(2).upper() == "YES"
    else:
        # If the classifier didn't follow the format, fail open (don't block
        # a real farmer over a formatting glitch) but flag it for visibility.
        is_farming_related = True
        is_human_medical_request = False

    tripwire = (not is_farming_related) or is_human_medical_request
    return GuardrailFunctionOutput(
        output_info={
            "raw_classifier_output": raw,
            "is_farming_related": is_farming_related,
            "is_human_medical_request": is_human_medical_request,
        },
        tripwire_triggered=tripwire,
    )


# --- Output guardrail: pesticide dosage safety ---------------------------

# Simple, conservative per-active-ingredient caps (units: ml or kg per acre
# in a 100L spray tank, matching the label-rate figures used in data.py).
_MAX_SAFE_DOSAGE_ML_PER_ACRE = {
    "imidacloprid": 100,
    "emamectin benzoate": 200,
    "propiconazole": 200,
    "cartap hydrochloride": 10000,  # granules, measured in grams/acre
}

_DOSAGE_PATTERN = re.compile(r"([a-zA-Z ]+?):?\s*(\d+(?:\.\d+)?)\s*(ml|g|kg)", re.IGNORECASE)


def _dosage_within_limits(text: str) -> bool:
    """Very small heuristic check: for any known active ingredient named in
    the text, make sure the quantity mentioned does not exceed our safe cap."""
    for match in _DOSAGE_PATTERN.finditer(text):
        name = match.group(1).strip().lower()
        amount = float(match.group(2))
        for ingredient, cap in _MAX_SAFE_DOSAGE_ML_PER_ACRE.items():
            if ingredient in name and amount > cap:
                return False
    return True


@output_guardrail
async def pesticide_safety_guardrail(
    ctx: RunContextWrapper, agent: Agent, output
) -> GuardrailFunctionOutput:
    """Blocks any final output whose pesticide dosage exceeds safe caps,
    or that appears to give human-medical treatment advice."""
    text = str(output)
    unsafe_dosage = not _dosage_within_limits(text)
    looks_like_human_medical_advice = bool(
        re.search(r"\b(take|swallow|dose for)\b.*\b(tablet|mg|human|patient)\b", text, re.IGNORECASE)
    )

    tripwire = unsafe_dosage or looks_like_human_medical_advice
    return GuardrailFunctionOutput(
        output_info={
            "unsafe_dosage": unsafe_dosage,
            "human_medical_advice_detected": looks_like_human_medical_advice,
        },
        tripwire_triggered=tripwire,
    )
