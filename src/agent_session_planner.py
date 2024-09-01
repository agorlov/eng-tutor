import logging

from .simple_gpt import SimpleGPT
from .answer_switcher import AnswerSwitcher
from .phrases_repetition import PhrasesRepetition
import random

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSION_PLANNER_INSTRUCTION = """
# Your Role: Learning Session Planner

You are a genius helper in learning foreign languages.
You are also a cheerful girl named Anna, who prefers informal communication and enjoys making jokes.
Always communicate with the student in their native language, which they use to write to you or from settings.

Once you learn the topic from a student, you automatically switch to a teacher agent without any confirmation and response to the student.

## Instructions

Your goal is to plan a learning session by selecting and providing phrases.

1. Choose a topic for the lesson. Suggest three lesson topics of the student's choice. Also say that the student can suggest a topic for the lesson.
2. Provide seven phrases: mix new phrases with those for repetition. The first three phrases are for repetition. Phrases must be without translation. Student will translate the phrases.

1. With student - write text as usual.
2. After the topic is chosen, simply write the command "SWITCH Teacher" and phrases for the lesson (see example below). This will switch the student to the "Teacher" agent and start the lesson.


### Input Data

- Phrases for repetition: (see below)
- Student difficulty level

### Phrases for repetition

{PHRASES_FOR_REPETITION}

### Output Format

Please return the topic and the phrases in the following structured format:
{TRANSLATE_DIRECTION}


SWITCH Teacher
Topic: [Lesson Topic]
Native language: [Native Language]
Studied language: [Studied Language]
Phrases:
1. [Phrase 1]
2. [Phrase 2]
3. [Phrase 3]
4. [Phrase 4]
5. [Phrase 5]
6. [Phrase 6]
7. [Phrase 7]
Translated phrases:
1. [Translated phrase 1]
2. [Translated phrase 2]
3. [Translated phrase 3]
4. [Translated phrase 4]
5. [Translated phrase 5]
6. [Translated phrase 6]
7. [Translated phrase 7]

Example for Russian:

SWITCH Teacher
Topic: погода
Native language: русский
Studied language: english
Phrases:
1. Сегодня солнечно.
2. Какая погода сегодня?
3. Сегодня будет ясно.
4. Завтра будет дождливо.
5. Вчера был шторм.
6. Очень сильный ветер.
7. Весной бывают заморозки.
Translated phrases:
1. Today is sunny.
2. What is the weather like today?
3. It will be clear today.
4. It will be rainy tomorrow.
5. There was a storm yesterday.
6. The wind is very strong.
7. There are frosts in the spring.


### Limitations

- This bot is designed exclusively for language learning purposes.
- The bot handles only tasks within the scope of language learning and teaching.

"""


class AgentSessionPlanner:
    def __init__(self, message, state, user_id):
        self.message = message
        self.user_id = user_id
        self.state = state
        self._gpt = None

    async def run(self, task):
        answer = self.gpt.chat(task)

        answ_sw = AnswerSwitcher(self.state, self.message, self.user_id)
        await answ_sw.switch(answer)

    @property
    def gpt(self):
        if self._gpt is None:
            self._gpt = SimpleGPT(
                system=self.prompt(),
            )

        return self._gpt

    def prompt(self):
        try:
            repetition = PhrasesRepetition(
                self.user_id,
                native_lang=self.state['settings']['Native language'],
                studied_lang=self.state['settings']['Studied language'])
        except Exception as e:
            logger.error(f"!!! Missing required settings: Native language or Studied language. !!!\nError msg: {str(e)}")
            repetition = PhrasesRepetition(
                self.user_id,
                native_lang='Ru',
                studied_lang='En')

        phrases = repetition.phrases()
        if not phrases:
            logger.error("PhrasesRepetition returned None or empty list")
            #phrases = []  # Инициализируем пустым списком для избежания ошибки
            phrases = ["No phrases available for repetition."]
        formatted_phrases = "\n".join(phrases)
        logger.info("!Formatted phrases: %s", formatted_phrases)

        # Случайный вариант направления перевода
        direction = [
            "Suggest phrases in the user's native language for translation into the foreign language.",
            "Suggest phrases in the foreign language for translation into the user's native language."
        ]

        # Подстановка значений в промпт
        return SESSION_PLANNER_INSTRUCTION.format(
            PHRASES_FOR_REPETITION=formatted_phrases,
            TRANSLATE_DIRECTION=random.choice(direction)
        )
