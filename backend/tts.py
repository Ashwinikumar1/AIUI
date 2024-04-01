import logging
import os
import time
import uuid

import requests
from gtts import gTTS
import edge_tts
from elevenlabs import generate, save
from google.cloud import texttospeech
from pyht import Client as pclient, TTSOptions, Format

# Initialize PlayHT API with your credentials
pclient = pclient("1WWdnyi24egvl9e2uP1UdCqJ9sf2", "d3588261f5d7428c8dff4b54749be1a7")
from util import delete_file

os.environ['GOOGLE_APPLICATION_CREDENTIALS']= ''

LANGUAGE = os.getenv("LANGUAGE", "en")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "EDGETTS")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "2d3e8e9b04b04645a214b548d8ea8980")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Sarah")
EDGETTS_VOICE = os.getenv("EDGETTS_VOICE", "en-US-EricNeural")

from deep_translator import GoogleTranslator  
translator = GoogleTranslator(source='english',target='hindi')  


async def to_speech(text, background_tasks):
    if TTS_PROVIDER == "gTTS":
        return _gtts_to_speech(text, background_tasks)
    elif TTS_PROVIDER == "ELEVENLABS":
        return _elevenlabs_to_speech(text, background_tasks)
    elif TTS_PROVIDER == "STREAMELEMENTS":
        return _streamelements_to_speech(text, background_tasks)
    elif TTS_PROVIDER == "EDGETTS":
        return await _edge_tts_to_speech(text, background_tasks)
    elif TTS_PROVIDER == "googleTTS":
        return await _google_text_to_speech(text,background_tasks)
    elif TTS_PROVIDER == "playHT":
        return await _playht_text_to_speech(text,background_tasks)
    else:
        raise ValueError(f"env var TTS_PROVIDER set to unsupported value: {TTS_PROVIDER}")


async def _edge_tts_to_speech(text, background_tasks):
    start_time = time.time()

    communicate = edge_tts.Communicate(text, EDGETTS_VOICE)
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    await communicate.save(filepath)

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath


def _gtts_to_speech(text, background_tasks):
    start_time = time.time()

    tts = gTTS(text, lang=LANGUAGE)
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    tts.save(filepath)

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath


def _elevenlabs_to_speech(text, background_tasks):
    start_time = time.time()

    audio = generate(
        api_key=ELEVENLABS_API_KEY,
        text=text,
        voice=ELEVENLABS_VOICE,
        model="eleven_monolingual_v1"
    )

    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    save(audio, filepath)

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath

async def _google_text_to_speech(text, background_tasks):
    start_time = time.time()
    
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    translated_text = translator.translate(text) 

    print ("Actual Text is :", text)
    print ("Translated text is :", translated_text)

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=translated_text)

    # Build the voice request, select the language code ("en-US")
    # and the ssml voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code='hi-IN',
        name='hi-IN-Neural2-C',
        ssml_gender=texttospeech.SsmlVoiceGender.MALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(request={"input": synthesis_input, "voice": voice, "audio_config": audio_config})

    # The response's audio_content is binary.
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    with open(filepath, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file ')

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath

async def _playht_text_to_speech(text,background_tasks):
    start_time = time.time()
    options = TTSOptions(
    voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json",
    sample_rate=8000,
    format=Format.FORMAT_MP3,
    speed=0.8,)

        # The response's audio_content is binary.
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    with open(filepath, 'wb') as out:
        # Write the response to the output file.
        for chunk in pclient.tts(text=text, voice_engine="PlayHT2.0-turbo", options=options):
            out.write(chunk)
        print('Audio content written to file ')

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath


def _streamelements_to_speech(text, background_tasks):
    start_time = time.time()

    response = requests.get(f"https://api.streamelements.com/kappa/v2/speech?voice=Salli&text={text}")

    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    with open(filepath, "wb") as f:
        f.write(response.content)

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath
