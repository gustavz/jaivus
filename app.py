import time
from datetime import datetime

import streamlit as st

from chat import SUPPORTED_CHATBOTS, get_chatbot
from record import SUPPORTED_RECOGNIZER, SpeechRecognizer
from speak import Speaker

# Wake word
WAKE_WORD = "jarvis"

# Config defaults
config = "config.json"
recognizer = "google"
chatbot = "openai"

# Init parameter
run_app = True
conversation = []

# Helper methods
def stop_app():
    global run_app
    run_app = False
    print("stop the app")


## Streamlit app header
st.title("JiAIvus")
st.markdown("Submit your config to start the chat")


## Sidebar
start_app = False
with st.sidebar:
    st.image("logo.png")
    # Config submit form
    with st.form("config"):
        api_key = st.text_input("Enter your API key", type="password", key="api_key")
        session_token = st.text_input(
            "Or enter your session token", type="password", key="session_token"
        )
        recognizer = st.selectbox(
            "Choose a recoginzer", SUPPORTED_RECOGNIZER, key="recognizer"
        )
        chatbot = st.selectbox("Choose chatbot", SUPPORTED_CHATBOTS, key="chatbot")
        submitted = st.form_submit_button("Submit")
        if submitted:
            print("config submitted")
            st.text("config submitted")
            if api_key or session_token:
                config = {"api_key": api_key, "session_token": session_token}
            start_app = True
    if start_app:
        # Stop button
        cols = st.columns([1, 3])
        cols[0].button("Stop", on_click=stop_app)

try:
    if start_app:
        print(f"start the app")
        # Initialize engines
        listen = SpeechRecognizer(recognizer)
        speak = Speaker()
        chat = get_chatbot(chatbot, config)

        # Wake-up instructions
        text = "Say the wake word to start the conversation:"
        st.markdown(text + ' **"' + WAKE_WORD + '"** [ʤɑ́ːvɪs]')
        speak.speak(text)

        # Wake-up Loop
        with st.spinner("**Listening.**"):
            while run_app:
                # Record audio until the wake word is spoken
                message = listen.listen()
                if message is not None and WAKE_WORD.lower() in message.lower():
                    break

        # Transition to conversation loop
        text = "Wake word detected. Starting conversation..."
        speak.speak(text)
        st.write("**" + text + "**")

        # Conversation Loop
        with st.spinner("**Speak now.**"):
            while run_app:
                # Record audio until the speaker stops speaking
                command = listen.listen()
                if command is not None:
                    # Display the transcribed text
                    st.text("You:")
                    st.text(command)
                    conversation.append(f"You: {command}")

                    # Get chatbot response and play it
                    response = chat.chat(command)
                    st.text("Jarvis:")
                    st.text(response)
                    conversation.append(f"Jarvis: {response}")
                    speak.speak(response)

                    with st.sidebar:
                        # Download conversation button
                        file = "\n".join(conversation)
                        file_name = f"jiaivus_conversation_{str(datetime.now())}.txt"
                        cols[1].download_button(
                            "Download conversation", file, file_name
                        )
except Exception as e:
    # Error handling
    print(f"app failed with: {e}")
    st.error(e, icon="🚨")

print("reset the app")
st.stop()
