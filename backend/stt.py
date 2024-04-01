import logging
import os
import shutil
import time
import uuid

from google.cloud import speech

import ffmpeg

from util import delete_file

from deep_translator import GoogleTranslator  
translator = GoogleTranslator(source='hindi',target='english')   
#translate_text = translator.translate('सुप्रभात कैसे हो तुम आज')


LANGUAGE = os.getenv("LANGUAGE", "hi-IN")
os.environ['GOOGLE_APPLICATION_CREDENTIALS']= '/app/quixotic-vent-417118-ddb0ddff9df2.json'

async def transcribe(audio):
    start_time = time.time()
    initial_filepath = f"/tmp/{uuid.uuid4()}{audio.filename}"

    with open(initial_filepath, "wb+") as file_object:
        shutil.copyfileobj(audio.file, file_object)

    converted_filepath = f"/tmp/ffmpeg-{uuid.uuid4()}{audio.filename}"

    logging.debug("running through ffmpeg")
    (
        ffmpeg
        .input(initial_filepath)
        .output(converted_filepath, loglevel="error")
        .run()
    )
    logging.debug("ffmpeg done")

    delete_file(initial_filepath)

    client = speech.SpeechClient()

    with open(converted_filepath, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        language_code=LANGUAGE,
    )


    logging.debug("calling Google Cloud Speech API")
    response = client.recognize(config=config, audio=audio)
    logging.info("STT response received from Google Cloud Speech in %s seconds", time.time() - start_time)

    # Extract transcript from the response
    transcript = ""
    for result in response.results:
        transcript += translator.translate(result.alternatives[0].transcript) + " "

    logging.info('Transcript: %s', transcript)

    delete_file(converted_filepath)

    return transcript
