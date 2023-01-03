import os
import logging
import time

import base64

import streamlit as st
from gtts import gTTS
import pyttsx3
from io import BytesIO
import uuid


logger = logging.getLogger(__name__)

SUPPORTED_SPEAKER = ["gtts", "pyttsx3"]


def get_speaker(speaker, **kwargs):
    assert speaker in SUPPORTED_SPEAKER
    if speaker == "pyttsx3":
        return Pyttsx3Speaker(**kwargs)
    if speaker == "gtts":
        return GttsSpeaker(**kwargs)


def play_audio_bytes(data):
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio controls autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    with st.sidebar:
        container = st.empty()
        container.markdown(
            md,
            unsafe_allow_html=True,
        )
    return container


def autoplay_audio(audio_file):
    if isinstance(audio_file, BytesIO):
        data = audio_file.getbuffer().tobytes()
        return play_audio_bytes(data)
    if isinstance(audio_file, str):
        with open(audio_file, "rb") as f:
            data = f.read()
            return play_audio_bytes(data)


def sleep_text(text, rate=120):
    words = len(text.split(" "))
    duration = words / rate * 60 + 1
    logger.info(f"sleeping {round(duration,3)} seconds while speaking {words} words")
    time.sleep(duration)


class GttsSpeaker:
    def __init__(self, **kwargs):
        logger.info(f"initializing gtts audio engine")

    def speak(self, text):
        try:
            logger.info("start speaking")
            sound_file = BytesIO()
            tts = gTTS(text, lang="en")
            tts.write_to_fp(sound_file)
            container = autoplay_audio(sound_file)
            sleep_text(text)
            container.empty()
            logger.info("stop speaking")
        except Exception as e:
            logger.warning(f"gtts audio engine failed with: {e}")


class Pyttsx3Speaker:
    def __init__(self, **kwargs):
        logger.info(f"initializing pyttsx3 audio engine with properties {kwargs}")
        self.kwargs = kwargs
        self._init_engine()

    def _init_engine(self):
        self.engine = None
        self.engine = pyttsx3.init()
        for key, value in self.kwargs.items():
            self.engine.setProperty(key, value)
        self.rate = self.engine.getProperty("rate")

    def speak(self, text, save_to_file=True):
        try:
            logger.info("start speaking")
            try:
                audio_file = f"audio_{uuid.uuid4()}.mp3"
                self.engine.save_to_file(text, audio_file)
                self.engine.runAndWait()
                container = autoplay_audio(audio_file)
                sleep_text(text, self.rate)
                container.empty()
                os.remove(audio_file)
            except FileNotFoundError as e:
                logger.warning(e)
                self.engine.say(text)
                self.engine.runAndWait()
                sleep_text(text, self.rate)
            logger.info("stop speaking")
        except RuntimeError as e:
            logger.warning(f'pyttsx3 audio runtime error "{e}" -> restart audio engine')
            self.engine.stop()
            self.engine.endLoop()
            self._init_engine()
            self.speak(text, save_to_file)
