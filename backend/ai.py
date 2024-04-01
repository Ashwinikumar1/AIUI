import base64
import json
import logging
import os
import time

import openai
import asyncio

from groq import AsyncGroq
import os
os.environ["GROQ_API_KEY"] = "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"
# Instantiation of Groq Client
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"),)

AI_COMPLETION_MODEL = os.getenv("AI_COMPLETION_MODEL", "gpt-3.5-turbo")
LANGUAGE = os.getenv("LANGUAGE", "en")
INITIAL_PROMPT = f"You are CIARA AI - a helpful assistant. Please provide answers to my queries in concise form max 2-3 sentences. Always provide your responses in the language that corresponds to the ISO-639-1 code: {LANGUAGE}."

groq_model_name = "mixtral-8x7b-32768"

async def get_completion(user_prompt, conversation_thus_far):
    if _is_empty(user_prompt):
        raise ValueError("empty user prompt received")

    start_time = time.time()
    messages = [
        {
            "role": "system",
            "content": INITIAL_PROMPT
        }
    ]

    # messages.extend(json.loads(base64.b64decode(conversation_thus_far)))
    messages.append({"role": "user", "content": user_prompt})

    logging.debug("calling %s", AI_COMPLETION_MODEL)
    res = await client.chat.completions.create(
        messages=messages,
        model=groq_model_name,
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    logging.info("response received from %s %s %s %s", AI_COMPLETION_MODEL, "in", time.time() - start_time, "seconds")

    completion = res.choices[0].message.content
    logging.info('%s %s %s', AI_COMPLETION_MODEL, "response:", completion)

    return completion


def _is_empty(user_prompt: str):
    return not user_prompt or user_prompt.isspace()
