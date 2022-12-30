import json
import logging

import openai
from pyChatGPT import ChatGPT
from revChatGPT.ChatGPT import Chatbot

logger = logging.getLogger(__name__)

SUPPORTED_CHATBOTS = ["openai", "pychatgpt", "revchatgpt"]


def get_chatbot(bot="openai", config="config.json"):
    assert bot in SUPPORTED_CHATBOTS
    if bot == "openai":
        return OpenAIBot(config)
    elif bot == "pychatgpt":
        return PyChatGPTBot(config)
    elif bot == "revchatgpt":
        return RevPyChatGPTBot(config)


class OpenAIBot:
    def __init__(self, config="config.json"):
        if isinstance(config, str):
            config = json.load(open(config))
        openai.api_key = config["api_key"]

    def chat(self, prompt, engine="text-davinci-003"):
        logger.info("start chat")
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        logger.info(f"response: {response}")
        return response["choices"][0]["text"]


class PyChatGPTBot:
    def __init__(self, config="config.json"):
        config = json.load(open(config))
        self.bot = ChatGPT(config["session_token"])
        self.bot.reset_conversation()

    def chat(self, prompt):
        logger.info("start chat")
        response = self.bot.send_message(prompt)
        logger.info(f"response: {response}")
        return response["message"]


class RevPyChatGPTBot:
    def __init__(self, config="config.json"):
        config = json.load(open(config))
        self.bot = Chatbot(config)
        self.bot.reset_chat()
        self.bot.refresh_session()

    def chat(self, prompt):
        logger.info("start chat")
        response = self.bot.ask(prompt)
        logger.info(f"response: {response}")
        return response["message"]
