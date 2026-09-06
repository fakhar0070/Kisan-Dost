"""
Model provider configuration for Kisan Dost.

By default this points at real OpenAI. If OPENAI_BASE_URL is set in .env
(e.g. to Groq's OpenAI-compatible endpoint), we switch the SDK to use the
Chat Completions API instead of the Responses API, since most third-party
OpenAI-compatible providers only support Chat Completions.

Import MODEL_NAME from this module wherever an Agent is created.
"""

import os
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

# Groq client banayein
groq_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"),
)

# Model name (Groq ka valid model)
MODEL_NAME = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=groq_client,
)
