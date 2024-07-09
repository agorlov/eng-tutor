from .simple_gpt import SimpleGPT
from .state_switcher import StateSwitcher

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
    def __init__(self, message, state, user_id):
        self.message = message
        self.user_id = user_id
        self.state = state

    async def run(self, message):
        gpt = SimpleGPT(system=TRANSLATOR_INSTRUCTION)
        await self.message.answer(gpt.chat(message))

        await StateSwitcher(self.state).switch("Main", "")
