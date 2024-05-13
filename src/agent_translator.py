import logging
from pprint import pprint

TRANSLATOR_INSTRUCTION = """
# Your Role is Translator

You are genius helper in translating foreign languages, known for your outstanding skills.

## Instructions

If user asks you translate text to any language please translate.
In the answer must be only translated text.

## Limitations

- This bot is designed exclusively for language translation purposes.
- The bot does not handle non-translational queries or tasks outside the scope of language learning and teaching.

"""

class AgentTranslator:
    def __init__(self, gpt):
        self.gpt = gpt
    
    def process_user_message(self, message):

        context = [
            {
                "role": "system", 
                "content": TRANSLATOR_INSTRUCTION
            },
            {
                "role": "user", 
                "content": message
            }
        ]

        response = self.gpt.chat.completions.create(
            messages=context,
            model="gpt-3.5-turbo-0613",
        )

        print("Translateor response: ")
        print(response)
        logging.info(response)

        # Обработка вызовов функций из ответа 
        respmsg = response.choices[0].message.content

        logging.info(f"Translated: {respmsg}")

        return respmsg

