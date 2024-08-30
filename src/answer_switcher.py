import logging
from .state_switcher import StateSwitcher

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerSwitcher:
    """
    Переключенный агент, в зависимости от ответа от агента
    """

    def __init__(self, state: dict, message, user_id):
        self.state = state
        self.message = message
        self.switcher = StateSwitcher(state)
        self.user_id = user_id

    async def switch(self, answer: str) -> None:
        """
        Если в ответе есть SWITCH [Assistant Name], то переключаемся на другого ассистента,
        а если нет, то отправляем сообщение студенту
        """

        user_message, switch_message = self.split_message(answer)

        # print("!answer: " + answer)
        # print("!user_message: " + user_message)
        # print("!switch: " + user_message)

        if user_message:
            logger.info("!Answer to user: %s", user_message)
            await self.message.answer(user_message)

        if switch_message:
            firstline = switch_message.splitlines()[0]
            assistant_name = firstline.split(maxsplit=1)[1]

            # взять вторую и последующие строки ответа из answer
            task = switch_message.splitlines()[1:]
            task = '\n'.join(task)

            logger.info("!Task to %s: %s", assistant_name, task)
            await self.switcher.switch(assistant_name, task)

    def split_message(self, str):
        """
        Разделяет строку на две части: user_message и switch_message.

        Args:
            str: Строка, которую нужно разделить.

        Returns:
            Кортеж из двух строк: user_message и switch_message.

        Пример строки
            В точку! 👍 Молодец! Вот все переводы, которые мы сделали:

            SWITCH Reviewer
            Lesson results:
            1. Correct: Goodbye!
            2. Correct: I'm fine.
            3. Error: I'm bored.
            4. Error: Where is the nearest airport?
            5. Error: I lost my luggage.
            6. Correct: Can you recommend a good restaurant?
            7. Correct: Why don't we travel to the moon next holiday? 🚀
        """

        # Проверка на None
        if str is None:
            logger.error("AnswerSwitcher->split_message(None): Received None instead of a text of GPT response")
            return None, None

        switch_message = None

        if "SWITCH" in str:
            parts = str.split("SWITCH", 1)
            user_message = parts[0].strip()
            if user_message == '':
                user_message = None
            switch_message = "SWITCH " + parts[1].strip()
        else:
            user_message = str.strip()

        return user_message, switch_message
