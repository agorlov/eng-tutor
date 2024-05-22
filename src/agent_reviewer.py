import logging
from pprint import pprint
import json

from .simple_gpt import SimpleGPT
from .state_switcher import StateSwitcher

REVIEWER_INSTRUCTION = """
# Role: Reviewer

You are an excellent language teacher.
You are also a cheerful girl - Anna. You prefer to communicate informally and like to joke.

Always communicate with the student in their native language.

Your first task is to save phrases from lesson in respond to list of phrases.
Your second task after you see "Saved" response is to say something to the student and switch to Main agent.


To save phrases please  convert the phrases to json format. And respond by JSON-only.

## Instructions

Read the input phrases and provide the phrases from the lesson in form of json.

In format of json:
[
    { phrase_orig: "Phrase 1", phrase_translated: "Phrase 1", correct: true },
    { phrase_orig: "Phrase 2", phrase_translated: "Phrase 2", correct: false },
    { phrase_orig: "Phrase 3", phrase_translated: "Phrase 3", correct: true },
    { phrase_orig: "Phrase 4", phrase_translated: "Phrase 4", correct: true },
    { phrase_orig: "Phrase 5", phrase_translated: "Phrase 5", correct: false },
    { phrase_orig: "Phrase 6", phrase_translated: "Phrase 6", correct: true },
    { phrase_orig: "Phrase 7", phrase_translated: "Phrase 7", correct: true }
]

Put only json to the answer, because it will be saved in database and it will programmatically be processed.

After that, when you see "Saved" message, now your respond will read your student. Say something about lesson results for the student and give the command "SWITCH Main", to switch to main agent.

## Your Input (example)

Lesson results:
1. Correct: Phrase 1.
2. Error: Phrase 2.
3. Correct: Phrase 3.
4. Correct: Phrase 4.
5. Error: Phrase 5.
6. Correct: Phrase 6.
7. Correct: Phrase 7.

"SWITCH Main" means that dialogue with the student will be switched to the Main agent.

## Limitations
- Don't answer questions that are not related to learning languages or that don't involve translation.

"""

class AgentReviewer:
    def __init__(self, tg, state, user_id):
        self.tg = tg
        self.user_id = user_id
        self.state = state
        self._gpt = None

    def run(self, task):
        answer = self.gpt.chat(task)

        # Если ответ содержит json, то обрабатываем его = выводим на экран фразы для сохранения в бд
        # декодируем json
        try:
            # Попытка декодирования JSON
            data = json.loads(answer)
            
            # Обработка данных после успешного декодирования
            print("!Данные успешно декодированы, сохраняем их в базу данных")
            print(data)
        except json.JSONDecodeError as e:
            # Обработка ошибки декодирования JSON
            print(f"Похоже это не JSON, идем дальше.")

        answer = self.gpt.chat("Saved")
        self.tg.send_message(self.user_id, answer)

        StateSwitcher(self.state).switch("Main", "Teacher agent> The lesson was successfully completed. Suggest the student to take another lesson if he wishes.\n")

    @property
    def gpt(self):
        if self._gpt is None:
            self._gpt = SimpleGPT(
                system=self.prompt(),
            )

        return self._gpt

    def prompt(self):
        # Форматирование списка фраз для подстановки в промпт
        # formatted_phrases = "\n".join(random_phrases)

        # Подстановка значений в промпт
        # return TEACHER_INSTRUCTION.format(
        #     PHRASES_FOR_REPETITION=formatted_phrases
        # )
        return REVIEWER_INSTRUCTION
