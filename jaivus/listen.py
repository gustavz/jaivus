import logging
import queue
import time

import numpy as np
import pydub
import speech_recognition as sr
from streamlit_webrtc import WebRtcMode, webrtc_streamer

import jaivus.patch

logger = logging.getLogger(__name__)

QUEUE_SIZE = 1024
SUPPORTED_LISTENER = ["web", "local"]
SUPPORTED_RECOGNIZER = [
    "google",
    "whisper",
    "google_cloud",
    "sphinx",
    "wit",
    "azure",
    "bing",
    "lex",
    "houndify",
    "amazon",
    "ibm",
    "tensorflow",
    "assemblyai",
    "vosk",
]


def get_listener(listener, recognizer, **kwargs):
    assert listener in SUPPORTED_LISTENER
    if listener == "local":
        return LocalListener(recognizer, **kwargs)
    elif listener == "web":
        return WebListener(recognizer, **kwargs)


class Streamer:
    def __init__(self):
        logger.info(f"initializing webrtc streamer")
        self.streamer = webrtc_streamer(
            key="speech-to-text",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=QUEUE_SIZE,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": False, "audio": True},
        )

    @property
    def playing(self):
        return self.streamer.state.playing

    def empty(self):
        self.streamer.audio_receiver._frames_queue = queue.Queue(QUEUE_SIZE)

    def get_frames(self):
        try:
            return self.streamer.audio_receiver.get_frames(timeout=1)
        except queue.Empty:
            time.sleep(0.1)
            return []


class LocalListener:
    def __init__(self, recognizer="google", duration=2, **kwargs):
        assert recognizer in SUPPORTED_RECOGNIZER
        logger.info(f"initializing {recognizer} speech recognition engine")
        self.recognizer = sr.Recognizer()
        self.recognizer_function_name = f"recognize_{recognizer}"
        self.kwargs = kwargs
        self.start_time = time.time()
        self.duration = duration
        if duration is not None:
            with sr.Microphone() as source:
                logger.info(
                    f"wait {duration} seconds to adjust the recognizer to ambient noise"
                )
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)

    @property
    def is_active(self):
        if time.time() - self.start_time > self.duration:
            return True
        return False

    def listen(self, **kwargs):
        with sr.Microphone() as source:
            logger.info("start listening")
            audio = self.recognizer.listen(source)
        logger.info("stop listening")
        return self.recognize(audio)

    def recognize(self, audio):
        try:
            logger.info("start recognizing")
            t = time.time()
            text = getattr(self.recognizer, self.recognizer_function_name)(
                audio, **self.kwargs
            )
            time_parsing = time.time() - t
            logger.info(
                f"recognized: {text} (timing: {round(time_parsing, 3)} seconds)"
            )
            logger.info(f"stop recognizing")
            return text
        except sr.UnknownValueError as e:
            logger.warning(f"recognizer could not understand audio")
        except sr.RequestError as e:
            logger.warning(f"could not request results from recognizer")


class WebListener(LocalListener):
    def __init__(self, recognizer="google", **kwargs):
        super(WebListener, self).__init__(recognizer, duration=None, **kwargs)
        self.streamer = Streamer()

    @property
    def is_active(self):
        return self.streamer.playing

    def recognize_frames(self, audio_frames, sample_rate, sample_width):
        audio = sr.AudioData(audio_frames, sample_rate, sample_width)
        return self.recognize(audio)

    def listen(self, number_of_chunks=10000):
        logger.info("start listening")
        self.streamer.empty()
        sound_chunk = pydub.AudioSegment.empty()
        while True:
            audio_frames = self.streamer.get_frames()

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > number_of_chunks:
                sample_width = audio_frames[0].format.bytes
                sample_rate = audio_frames[0].sample_rate
                sound_chunk = sound_chunk.set_channels(1).set_frame_rate(sample_rate)
                buffer = np.array(sound_chunk.get_array_of_samples())
                logger.info(
                    f"trying to recognize {len(sound_chunk)} chunks with rate:{sample_width} width:{sample_rate}"
                )
                text = self.recognize_frames(buffer, sample_rate, sample_width)
                sound_chunk = pydub.AudioSegment.empty()
                self.streamer.empty()
                if text is not None:
                    logger.info("stop listening")
                    return text
