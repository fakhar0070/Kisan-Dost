"""
Realistic hardcoded reference data for Kisan Dost.

The hackathon brief explicitly allows hardcoded tables in place of live
APIs/datasets ("realistic hardcoded tables ... are perfectly acceptable").
Numbers below are reasonable approximations for Punjab/Sindh conditions
and are meant to be swapped for the real datasets listed in the brief
(Kaggle crop-recommendation dataset, PBS, FAOSTAT, AMIS Punjab) if you
want the bonus marks.
"""

# --- Crop Advisor -----------------------------------------------------

CROP_TABLE = {
    "rabi": {
        "low": [
            {"crop": "Wheat", "yield_maund_per_acre": 25, "profit_pkr_per_acre": 45000,
             "water": "low", "notes": "Most reliable Rabi crop under water stress."},
            {"crop": "Chickpea (Chana)", "yield_maund_per_acre": 12, "profit_pkr_per_acre": 38000,
             "water": "low", "notes": "Good for sandy soil, needs almost no irrigation."},
        ],
        "medium": [
            {"crop": "Wheat", "yield_maund_per_acre": 32, "profit_pkr_per_acre": 58000,
             "water": "medium", "notes": "Standard package with 2-3 irrigations gives best margin."},
            {"crop": "Mustard (Sarsoon)", "yield_maund_per_acre": 14, "profit_pkr_per_acre": 42000,
             "water": "medium", "notes": "Good rotation crop, edible oil demand is stable."},
        ],
        "high": [
            {"crop": "Potato", "yield_maund_per_acre": 200, "profit_pkr_per_acre": 120000,
             "water": "high", "notes": "High input cost but strong return with assured irrigation."},
            {"crop": "Wheat", "yield_maund_per_acre": 38, "profit_pkr_per_acre": 65000,
             "water": "high", "notes": "Full irrigation package, near-maximum yield."},
        ],
    },
    "kharif": {
        "low": [
            {"crop": "Sorghum (Jowar)", "yield_maund_per_acre": 18, "profit_pkr_per_acre": 30000,
             "water": "low", "notes": "Drought tolerant fodder/grain crop."},
            {"crop": "Mung Bean", "yield_maund_per_acre": 8, "profit_pkr_per_acre": 35000,
             "water": "low", "notes": "Short duration, fixes nitrogen for next crop."},
        ],
        "medium": [
            {"crop": "Cotton", "yield_maund_per_acre": 22, "profit_pkr_per_acre": 55000,
             "water": "medium", "notes": "Watch for whitefly and pink bollworm."},
            {"crop": "Maize", "yield_maund_per_acre": 45, "profit_pkr_per_acre": 60000,
             "water": "medium", "notes": "Good option in Punjab with assured canal turns."},
        ],
        "high": [
            {"crop": "Rice (Basmati)", "yield_maund_per_acre": 35, "profit_pkr_per_acre": 75000,
             "water": "high", "notes": "Needs standing water; strong export price for Basmati."},
            {"crop": "Sugarcane", "yield_maund_per_acre": 800, "profit_pkr_per_acre": 90000,
             "water": "high", "notes": "Long duration (10-12 months), needs mill nearby."},
        ],
    },
}

# --- Pest & Disease Doctor --------------------------------------------
# Keyed by simple keyword match against farmer's free-text symptom description.
# safe_dosage values are deliberately capped at label-recommended rates.

PEST_TABLE = [
    {
        "keywords": ["whitefly", "white insect", "sufaid makhi", "sticky leaves", "curling"],
        "crop_hint": "cotton",
        "name": "Whitefly (Bemisia tabaci)",
        "treatment": "Spray Imidacloprid 200SL or Neem oil in early morning/evening.",
        "safe_dosage": "Imidacloprid 200SL: 50 ml per 100 litres water per acre (label max).",
        "reapply_after_days": 10,
        "warning": "Do not exceed label rate. Wear gloves and mask. Keep children/animals away for 24 hours after spray.",
    },
    {
        "keywords": ["pink boll", "bollworm", "sundi", "boll damage", "holes in boll"],
        "crop_hint": "cotton",
        "name": "Pink Bollworm",
        "treatment": "Pheromone traps + Emamectin Benzoate spray if infestation is above threshold.",
        "safe_dosage": "Emamectin Benzoate 1.9EC: 200 ml per acre in 100 litres water (label max).",
        "reapply_after_days": 14,
        "warning": "Rotate chemical group to avoid resistance. Do not spray during flowering when bees are active.",
    },
    {
        "keywords": ["yellow leaves", "rust", "zang", "orange spots"],
        "crop_hint": "wheat",
        "name": "Wheat Yellow Rust",
        "treatment": "Spray Propiconazole 25EC as soon as pustules are seen.",
        "safe_dosage": "Propiconazole 25EC: 200 ml per acre in 100-150 litres water (label max).",
        "reapply_after_days": 15,
        "warning": "Spray in calm weather, avoid before rain. Use resistant variety next season if recurring.",
    },
    {
        "keywords": ["stem borer", "dead heart", "tunnel", "sundi tana"],
        "crop_hint": "rice",
        "name": "Rice Stem Borer",
        "treatment": "Apply Cartap Hydrochloride granules at early tillering stage.",
        "safe_dosage": "Cartap Hydrochloride 4G: 10 kg per acre broadcast in standing water (label max).",
        "reapply_after_days": 20,
        "warning": "Maintain 2-3 inch standing water for the granules to work; do not exceed label dose.",
    },
    {
        "keywords": ["aphid", "chapa", "curling leaves", "black insect"],
        "crop_hint": "any",
        "name": "Aphid infestation",
        "treatment": "Spray Neem oil 2% first; escalate to Imidacloprid only if severe.",
        "safe_dosage": "Neem oil: 30-50 ml per 15 litres water (safe, no waiting period).",
        "reapply_after_days": 7,
        "warning": "Prefer neem oil first — it is safer and cheaper before moving to chemical sprays.",
    },
]

# --- Fertilizer Calculator ---------------------------------------------
# NPK requirement in kg/acre, and bag prices in PKR (approximate, editable).

NPK_REQUIREMENT_KG_PER_ACRE = {
    "wheat": {"n": 50, "p": 25},
    "cotton": {"n": 60, "p": 30},
    "rice": {"n": 55, "p": 20},
    "maize": {"n": 65, "p": 30},
    "sugarcane": {"n": 100, "p": 50},
    "potato": {"n": 80, "p": 60},
    "chickpea (chana)": {"n": 10, "p": 20},
    "mung bean": {"n": 10, "p": 15},
    "mustard (sarsoon)": {"n": 40, "p": 20},
    "sorghum (jowar)": {"n": 45, "p": 20},
    "rice (basmati)": {"n": 55, "p": 20},
}

UREA_N_CONTENT = 0.46       # 46% nitrogen per bag
DAP_P_CONTENT = 0.46        # 46% P2O5 per bag (DAP is 18-46-0)
BAG_WEIGHT_KG = 50
UREA_PRICE_PER_BAG_PKR = 3200
DAP_PRICE_PER_BAG_PKR = 11800

# --- Mandi Price Lookup --------------------------------------------------

MANDI_PRICES = {
    "wheat":               {"market": "Faisalabad Grain Market", "price": 3100, "trend": "stable"},
    "cotton":              {"market": "Multan Cotton Market",     "price": 8500, "trend": "rising"},
    "rice (basmati)":      {"market": "Sheikhupura Rice Market",  "price": 6200, "trend": "rising"},
    "maize":               {"market": "Sahiwal Grain Market",     "price": 2600, "trend": "stable"},
    "potato":              {"market": "Okara Vegetable Market",   "price": 1800, "trend": "falling"},
    "sugarcane":           {"market": "Faisalabad Mill Gate",     "price": 400,  "trend": "stable"},
    "chickpea (chana)":    {"market": "Layyah Grain Market",      "price": 9800, "trend": "rising"},
    "mung bean":           {"market": "Bahawalpur Grain Market",  "price": 12000, "trend": "stable"},
    "mustard (sarsoon)":   {"market": "Multan Oilseed Market",    "price": 6800, "trend": "stable"},
    "sorghum (jowar)":     {"market": "Bahawalpur Grain Market",  "price": 2400, "trend": "stable"},
}

# --- Govt Support Finder --------------------------------------------------

GOVT_SCHEMES = {
    "punjab": [
        "Kisan Card (subsidised inputs, interest-free agri loans up to a set limit)",
        "Punjab CM Kisan Dost Program - subsidised fertilizer bags per season",
        "Punjab Agri Loan Scheme via Bank of Punjab for tractors/tubewells",
    ],
    "sindh": [
        "Sindh Kissan Portal - registration for subsidised seed and DAP",
        "Sindh Agriculture Growth Program - tunnel farming and drip irrigation subsidy",
    ],
    "kpk": [
        "KP Rural Support Program - livestock and seed subsidy",
        "KP Agri Loan Scheme via Bank of Khyber",
    ],
    "balochistan": [
        "Balochistan Agriculture Support Program - solar tubewell subsidy",
        "Federal Kissan Package - subsidised DAP for registered farmers",
    ],
}
