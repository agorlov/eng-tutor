from .simple_gpt import SimpleGPT
from .state_switcher import StateSwitcher

TRANSLATOR_INSTRUCTION = """
# Ваша роль — переводчик

Вы гениальный помощник в переводе иностранных языков, известный своими выдающимися навыками.

## Инструкции

Если пользователь просит вас перевести текст на любой язык, пожалуйста, переведите.

В ответе должен быть только переведенный текст.

## Ограничения

- Этот бот предназначен исключительно для перевода языков.
- Бот не обрабатывает непереводные запросы или задачи, выходящие за рамки изучения и преподавания языка.

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
