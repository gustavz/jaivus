import logging
from datetime import datetime

import streamlit as st
import streamlit_toggle as tog


from chat import SUPPORTED_CHATBOTS, get_chatbot
from listen import SUPPORTED_RECOGNIZER, SUPPORTED_LISTENER, get_listener
from speak import SUPPORTED_SPEAKER, get_speaker

logger = logging.getLogger(__name__)

# Init streamlit session and stateful parameters
SESSION = st.session_state
if "api_key" not in SESSION:
    SESSION["api_key"] = None
if "session_token" not in SESSION:
    SESSION["session_token"] = None
if "advanced_settings" not in SESSION:
    SESSION["advanced_settings"] = False
if "start_app" not in SESSION:
    SESSION["start_app"] = False
if "run_app" not in SESSION:
    SESSION["run_app"] = True
if "recognizer" not in SESSION:
    SESSION["recognizer"] = "google"
if "chatbot" not in SESSION:
    SESSION["chatbot"] = "openai"
if "speaker" not in SESSION:
    SESSION["speaker"] = "pyttsx3"
if "listener" not in SESSION:
    SESSION["listener"] = "web"
if "config" not in SESSION:
    SESSION["config"] = "config.json"
if "conversation" not in SESSION:
    SESSION["conversation"] = []


# Config defaults
WAKE_WORD = "jarvis"


# Helper methods
def stop_app():
    SESSION["start_app"] = False
    SESSION["run_app"] = False
    SESSION["conversation"] = []
    logger.info("stop the app")


## Streamlit app header
st.set_page_config(
    page_title="jAIvus",
    page_icon="🧞",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.title("🧞 jAIvus")
status_indicator = st.empty()
status_indicator.write("Submit your config to start the app")


# Sidebar
with st.sidebar:
    st.image("logo.png")

    # Config form
    with st.form("config_form"):
        SESSION["api_key"] = st.text_input("Enter your API key", type="password")
        if SESSION["advanced_settings"]:
            SESSION["session_token"] = st.text_input(
                "Enter your session token", type="password"
            )
            SESSION["recognizer"] = st.selectbox(
                "Choose a recoginzer", SUPPORTED_RECOGNIZER
            )
            SESSION["chatbot"] = st.selectbox("Choose chatbot", SUPPORTED_CHATBOTS)
            SESSION["speaker"] = st.selectbox("Choose speaker", SUPPORTED_SPEAKER)
            SESSION["listener"] = st.selectbox("Choose listener", SUPPORTED_LISTENER)

        # Submit button
        submitted = st.form_submit_button("Submit")
        if submitted:
            logger.info("config submitted")
            st.text("config submitted")
            if SESSION["api_key"] or SESSION["session_token"]:
                SESSION["config"] = {
                    "api_key": SESSION["api_key"],
                    "session_token": SESSION["session_token"],
                }
            SESSION["start_app"] = True
            SESSION["run_app"] = True

    if SESSION["start_app"]:
        # Reset button
        cols = st.columns([1, 3])
        cols[0].button("Reset", on_click=stop_app)
    else:
        # Advanced Settings toggle
        advanced_settings = tog.st_toggle_switch(
            label="Advanced Settings",
            key="advanced_settings",
        )

# Main screen
try:
    if SESSION["start_app"]:
        # Activate microphone
        status_indicator.write("Select audio source and press 'Start'")
        listen = get_listener(SESSION["listener"], SESSION["recognizer"])

    if SESSION["start_app"] and listen.is_active:
        logger.info(f"start the app with config {SESSION['config']}")
        # Initialize engines
        speak = get_speaker(SESSION["speaker"])
        chat = get_chatbot(SESSION["chatbot"], SESSION["config"])

        # Wake-up instructions
        text = "Say the wake word to start the conversation:"
        status_indicator.write(text + ' **"' + WAKE_WORD + '"** [ʤɑ́ːvɪs]')
        speak.speak(text)

        # Wake-up Loop
        with st.spinner("**Listening.**"):
            while SESSION["run_app"]:
                # Record audio until the wake word is spoken
                message = listen.listen()
                if message is not None and WAKE_WORD.lower() in message.lower():
                    break

        # Transition to conversation loop
        text = "Wake word detected. Starting conversation..."
        speak.speak(text)
        status_indicator.write("**" + text + "**")

        # Conversation Loop
        with st.spinner("**Speak now.**"):
            while SESSION["run_app"]:
                # Record audio until the speaker stops speaking
                command = listen.listen()
                if command is not None:
                    # Display the transcribed text
                    st.text("You:")
                    st.text(command)
                    SESSION["conversation"].append(f"You: {command}")

                    # Get chatbot response and play it
                    response = chat.chat(command)
                    st.text("Jarvis:")
                    st.text(response)
                    SESSION["conversation"].append(f"Jarvis: {response}")
                    speak.speak(response)

                    with st.sidebar:
                        # Download conversation button
                        file = "\n".join(SESSION["conversation"])
                        file_name = f"jaivus_conversation_{str(datetime.now())}.txt"
                        cols[1].download_button(
                            "Download conversation", file, file_name
                        )

except Exception as e:
    # Error handling
    logger.warning(f"app failed with: {e}")
    st.error(e, icon="🚨")

logger.info("reset the app")
st.stop()
