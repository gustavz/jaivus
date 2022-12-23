import streamlit as st

from record import SpeechRecognizer
from speak import Speaker
from chat import get_chatbot

# Set the wake word
WAKE_WORD = 'jarvis'

# configure app
config = 'config.json'
recoginizer = 'google'
chatbot = 'openai'

## streamlit app
st.title('JiAIvus')

## sidebar
with st.sidebar:
    st.image('logo.png')

# initialize engines
listen = SpeechRecognizer(recoginizer)
speak = Speaker()
chat = get_chatbot(chatbot, config)

# Wake-up instructions
text = 'Say the wake word to start the conversation:'
st.markdown(text + ' **"' + WAKE_WORD + '"** [ʤɑ́ːvɪs]')
speak.speak(text)

# Wake-up Loop
while True:
    # Record audio until the wake word is spoken
    message = listen.listen()
    if message is not None and WAKE_WORD.lower() in message.lower():
        text = 'Wake word detected. Starting conversation...'
        speak.speak(text)
        st.write('**' + text + '**')
        break

# Conversation Loop
with st.spinner('**Speak now.**'):
    conversation = []
    while True:
        # Record audio until the speaker stops speaking
        command = listen.listen()
        if command is not None:
            # Display the transcribed text
            st.text('You:')
            st.text(command)
            conversation.append(f'You: {command}')
            
            # Get chatbot response and play it
            response = chat.chat(command)
            st.text('Jarvis:')
            st.text(response)
            conversation.append(f'Jarvis: {response}')
            speak.speak(response)
