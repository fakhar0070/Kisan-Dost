"""
Kisan Dost — terminal entry point.

Run with:
    python main.py

Type your question in plain Urdu-English, e.g.:
    "Multan mein 5 acre pe Rabi season mein kya lagaun, pani kam hai"

Type 'profile' to see/update your remembered farmer profile.
Type 'exit' or 'quit' to leave.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv()  # picks up OPENAI_API_KEY (and optional OPENAI_BASE_URL) from .env

from agents import Runner, SQLiteSession, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered

from agents_config import triage_agent
from models import FarmerProfile


def build_session_and_profile() -> tuple[SQLiteSession, FarmerProfile]:
    """One SQLite-backed session per run so conversation history persists
    even if the terminal is closed and reopened (file: kisan_dost.db)."""
    session = SQLiteSession(session_id="local-farmer", db_path="kisan_dost.db")
    profile = FarmerProfile()
    return session, profile


def print_banner():
    print("=" * 60)
    print("  KISAN DOST — Aapka Zaraat Ka Dost (AI Agronomy Agent)")
    print("=" * 60)
    print("Apna sawaal likhein (Urdu-English mein). 'exit' likh kar band karein.\n")


async def handle_turn(session: SQLiteSession, profile: FarmerProfile, user_input: str) -> None:
    try:
        result = await Runner.run(
            triage_agent,
            user_input,
            session=session,
            context=profile,
        )
        print(f"\nKisan Dost: {result.final_output}\n")

    except InputGuardrailTripwireTriggered:
        print(
            "\nKisan Dost: Maazrat, yeh sawaal farming se related nahi lagta ya "
            "human/animal medical advice maang raha hai — main sirf zaraat "
            "(khaiti-baari) mein madad kar sakta hoon.\n"
        )
    except OutputGuardrailTripwireTriggered:
        print(
            "\nKisan Dost: Maazrat, jawab safe dosage limit cross kar raha tha isliye "
            "rok diya gaya. Baraye meherbani apne nazdeeki agriculture officer se "
            "dosage confirm karein.\n"
        )


def update_profile_from_prompt(profile: FarmerProfile) -> None:
    print("\nCurrent profile:", profile.model_dump())
    print("Update karna hai? (Enter dabayein skip karne ke liye)")
    name = input("Naam: ").strip()
    district = input("District: ").strip()
    province = input("Province: ").strip()
    land = input("Land size (acres): ").strip()
    crop = input("Current/last crop: ").strip()

    if name:
        profile.name = name
    if district:
        profile.district = district
    if province:
        profile.province = province
    if land:
        try:
            profile.land_size_acres = float(land)
        except ValueError:
            print("Land size number honi chahiye, skip kar diya.")
    if crop:
        profile.current_crop = crop
    print("Profile update ho gaya.\n")


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "ERROR: OPENAI_API_KEY set nahi hai. .env file banayein (.env.example dekhein) "
            "aur apni key daal dein, ya kisi OpenAI-compatible provider (Gemini/Groq) ki "
            "key + OPENAI_BASE_URL set karein."
        )
        sys.exit(1)

    print_banner()
    session, profile = build_session_and_profile()

    while True:
        try:
            user_input = input("Aap: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAllah Hafiz!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Allah Hafiz! Kisan Dost hamesha hazir hai.")
            break
        if user_input.lower() == "profile":
            update_profile_from_prompt(profile)
            continue

        await handle_turn(session, profile, user_input)


if __name__ == "__main__":
    asyncio.run(main())
