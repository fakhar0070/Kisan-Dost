<<<<<<< HEAD
# Kisan Dost — Farmer's Friend

A terminal AI agronomy agent for Pakistani farmers, built with the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

A farmer types a question in plain Urdu-English ("Multan mein 5 acre pe
Rabi season mein kya lagaun, pani kam hai") and gets a practical answer:
crop recommendation with profit estimate, fertilizer plan in bags with
cost, pest treatment with a safe dosage, mandi price, irrigation timing,
or relevant government schemes.

## Project structure

```
kisan-dost/
├── main.py            # terminal entry point, session + farmer profile
├── agents_config.py    # triage agent + 4 specialist agents (handoffs)
├── tools.py            # 7 function tools (one per capability)
├── guardrails.py        # input guardrail (off-topic/medical) + output guardrail (pesticide safety)
├── models.py            # Pydantic structured-output models
├── data.py              # hardcoded but realistic reference tables
├── requirements.txt
└── .env.example
```

## What each tool does

| Tool | File | What it does |
|---|---|---|
| `crop_advisor` | tools.py | Recommends crops by district/soil/season/water/land size, with yield & profit |
| `pest_doctor` | tools.py | Identifies pest/disease from symptoms, gives safe label-rate treatment |
| `fertilizer_calculator` | tools.py | Converts NPK need into Urea/DAP bags + total cost |
| `mandi_price_lookup` | tools.py | Returns typical wholesale price + sell/hold advice |
| `irrigation_weather_advisor` | tools.py | **Real** Open-Meteo weather API (free, no key) → irrigation timing + frost/heat warnings |
| `profit_estimator` | tools.py | Season budget: cost vs revenue, net margin, break-even yield |
| `govt_support_finder` | tools.py | Surfaces Kisan Card / subsidy / loan schemes by province |

## Agent design

- **Triage Agent** — first point of contact, routes to the right specialist.
- **Agronomy Agent** — `crop_advisor`, `fertilizer_calculator`, `irrigation_weather_advisor`.
- **Pest Doctor Agent** — `pest_doctor`, wrapped with the pesticide-safety output guardrail.
- **Market Agent** — `mandi_price_lookup`, `govt_support_finder`.
- **Finance Agent** — `profit_estimator`.

## Guardrails

- **Input guardrail** (`farming_topic_guardrail`): rejects messages that aren't
  about farming, and rejects requests for human/animal medical advice.
- **Output guardrail** (`pesticide_safety_guardrail`): checks any pesticide
  dosage mentioned in the final answer against safe per-acre caps and blocks
  the response if it would exceed them; also blocks anything resembling
  human-medical dosing advice.

## Sessions & context

A `SQLiteSession` (`kisan_dost.db`) keeps conversation history across turns
so the agent doesn't lose context mid-conversation. A typed `FarmerProfile`
(name, district, province, land size, current crop) is passed as `context`
to every run — type `profile` in the terminal to set it once, and the
agents will use it instead of asking again.

## How to run it

### 1. Set up a virtual environment (recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Copy `.env.example` to `.env` and paste in your key:

```
OPENAI_API_KEY=sk-...
```

No OpenAI credits? The SDK is provider-agnostic — point it at a free
OpenAI-compatible endpoint (e.g. Groq, Gemini) by also setting
`OPENAI_BASE_URL` in `.env`.

### 4. Run it

```bash
python main.py
```

Type `profile` first to save your district/land size/crop so you don't
have to repeat them every message. Type `exit` to quit.

## Example questions to try

- "Multan mein 5 acre pe Rabi season mein kya lagaun, pani kam hai"
- "Cotton ke patte curl ho rahe hain aur neeche safed choti si insect hai, kya karun"
- "10 acre wheat ke liye fertilizer plan aur cost batao"
- "Aaj cotton ka mandi rate kya hai"
- "5 acre cotton, cost 150000, expected yield 20 maund/acre, price 8500 — profit nikalo"
- "Punjab mein fertilizer subsidy scheme kya hai"

## Data sources / bonus integrations

- **Live**: Open-Meteo Weather + Geocoding APIs (free, no key) for
  `irrigation_weather_advisor`.
- **Hardcoded (swap for real data for extra bonus marks)**: crop yields
  loosely based on PBS/FAOSTAT Pakistan figures; fertilizer NPK
  requirements are standard agronomy references; mandi prices are
  illustrative — replace with a live AMIS Punjab scrape for full marks.

## Notes

- Written for Python 3.9+.
- Keep your real `.env` out of git (a `.gitignore` entry for `.env` and
  `kisan_dost.db` is recommended before pushing to GitHub).
=======
# Kisan-Dost
>>>>>>> 268c9861f704de12d18cbc89ef261f6d37fcce75
