import logging
from pprint import pprint
import json

from .simple_gpt import SimpleGPT
from .state_switcher import StateSwitcher
from .phrases_saved import PhrasesSaved
from .user_score import UserScore

ARCHIVER_INSTRUCTION = """
# Role: Archiver

Your task is to save phrases from lesson in respond to list of phrases.
To save phrases please convert them to json format. And respond by JSON-only.

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

## Your Input, example

Lesson results:
Correct;Phrase 1 original;Phrase 1 translated
Error;Phrase 2 original;Phrase 2 translated
Correct;Phrase 3 original;Phrase 3 translated
Correct;Phrase 4 original;Phrase 4 translated
Error;Phrase 5 original;Phrase 5 translated
Correct;Phrase 6 original;Phrase 6 translated
Correct;Phrase 7 original;Phrase 7 translated


## Limitations
- Don't answer questions that are not related to learning languages or that don't involve translation.
- If Ok, answer only in json format.
- In case of ERROR, answer like this template: ERROR: [Error message]

"""

class AgentArchiver:
    def __init__(self, tg, state, user_id):
        self.tg = tg
        self.user_id = user_id
        self.state = state
        self.score = UserScore(user_id)
        self._gpt = None

    def run(self, task):
        answer = self.gpt.chat(
            task + 
            "\n\nOutput the information in structured JSON format without using markdown code blocks."
        )

        # Если ответ содержит json, то обрабатываем его = выводим на экран фразы для сохранения в бд
        # декодируем json
        try:
            # Попытка декодирования JSON
            data = json.loads(answer)

            # Обработка данных после успешного декодирования
            print("!Данные успешно декодированы, сохраняем их в базу данных")
            print(data)            

            PhrasesSaved(
                self.user_id,
                self.state['settings']['Native language'],
                self.state['settings']['Studied language'],
            ).save_phrases(data)
        
        except json.JSONDecodeError as e:
            # Обработка ошибки декодирования JSON
            print(f"Похоже это не JSON, идем дальше.")
            self.tg.send_message(
                self.user_id,
                f"Не удалось сохранить повторенные фразы. Ответ агента Archiver: {answer}"
            )

        correct_count = 0
        for phrase in data:
            if phrase['correct']:
                correct_count += 1                
                
        bonus = correct_count * 5
        self.score.update_score(bonus)
        total_bonuses = self.score.user_score()
        self.tg.send_message(
            self.user_id,
            f"[{correct_count}/7] 👍 +{bonus} XP. Total XP: {total_bonuses}"
        )

        StateSwitcher(self.state).switch("Main", "Teacher agent> The lesson was successfully completed. Suggest the student to take another lesson if he wishes.\n")

    @property
    def gpt(self):
        if self._gpt is None:
            self._gpt = SimpleGPT(
                system=self.prompt(),
            )

        return self._gpt

    def prompt(self):
        return ARCHIVER_INSTRUCTION
