import base64
import json
import logging
import os
import time
import requests

import openai

AI_COMPLETION_MODEL = os.getenv("AI_COMPLETION_MODEL", "gpt-3.5-turbo")
LANGUAGE = os.getenv("LANGUAGE", "en")
INITIAL_PROMPT = f"You are AIUI - a helpful assistant with a voice interface. Keep your responses very succinct and limited to a single sentence since the user is interacting with you through a voice interface. Always provide your responses in the language that corresponds to the ISO-639-1 code: {LANGUAGE}."


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
    messages.extend(_get_additional_initial_messages())
    messages.extend(json.loads(base64.b64decode(conversation_thus_far)))
    messages.append({"role": "user", "content": user_prompt})

    logging.debug("calling %s", AI_COMPLETION_MODEL)
    res = await openai.ChatCompletion.acreate(model=AI_COMPLETION_MODEL, messages=messages, timeout=15)
    logging.info("response received from %s %s %s %s", AI_COMPLETION_MODEL, "in", time.time() - start_time, "seconds")

    completion = res['choices'][0]['message']['content']
    logging.info('%s %s %s', AI_COMPLETION_MODEL, "response:", completion)

    return completion


async def get_local_completion(user_prompt):
    logging.info("calling the local model")

    data = {
        "message": f'### Instruction: {INITIAL_PROMPT} ### User: {user_prompt} ### Response:'
    }

    start_time = time.time()
    response = requests.post('http://host.docker.internal:8001/test', json=data)
    logging.info("response received from %s %s %s %s", "LOCAL_AI_MODEL", "in", time.time() - start_time, "seconds")

    logging.info("done calling the local model")
    return response.text


def _is_empty(user_prompt: str):
    return not user_prompt or user_prompt.isspace()


def _get_additional_initial_messages():
    match AI_COMPLETION_MODEL:
        case "gpt-3.5-turbo":
            return [
                {
                    "role": "user",
                    "content": INITIAL_PROMPT
                }
            ]
        case _:
            return []
