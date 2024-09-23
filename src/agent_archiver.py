import logging
import json

from .simple_gpt import SimpleGPT
from .state_switcher import StateSwitcher
from .phrases_saved import PhrasesSaved
from .user_score import UserScore

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARCHIVER_INSTRUCTION = """
# Роль: Архиватор

Ваша задача — сохранить фразы из урока в ответ на список фраз.
Чтобы сохранить фразы, преобразуйте их в формат json. И отвечайте только JSON (JSON-only).

## Инструкции

В формате json:
[
{ фраза_orig: "Фраза 1", фраза_translated: "Фраза 1", правильно: true },
{ фраза_orig: "Фраза 2", фраза_translated: "Фраза 2", правильно: false },
{ фраза_orig: "Фраза 3", фраза_translated: "Фраза 3", правильно: true },
{ фраза_orig: "Фраза 4", фраза_translated: "Фраза 4", правильно: true },
{ фраза_orig: "Фраза 5", фраза_translated: "Фраза 5", правильно: false },
{ фраза_orig: "Фраза 6", фраза_translated: "Фраза 6", правильно: true },
{ фраза_orig: "Фраза 7", фраза_translated: "Фраза 7", правильно: true }
]

Поместите в ответ, потому что он будет сохранен в базе данных и будет обработан программно.

## Ваш ввод, пример

Результаты урока:
Верно;Фраза 1 оригинал;Фраза 1 переведена
Ошибка;Фраза 2 оригинал;Фраза 2 переведена
Верно;Фраза 3 оригинал;Фраза 3 переведена
Верно;Фраза 4 оригинал;Фраза 4 переведена
Ошибка;Фраза 5 оригинал;Фраза 5 переведена
Верно;Фраза 6 оригинал;Фраза 6 переведена
Верно;Фраза 7 оригинал;Фраза 7 переведена

## Ограничения
- Не отвечайте на вопросы, которые не связаны с изучением языков или не требуют перевода.
- Если все в порядке, отвечайте только в формате json.
- В случае ОШИБКИ ответьте следующим образом: ОШИБКА: [Сообщение об ошибке]

"""

class AgentArchiver:
    def __init__(self, message, state, user_id):
        self.message = message
        self.user_id = user_id
        self.state = state
        self.score = UserScore(user_id)
        self._gpt = None

    async def run(self, task):
        answer = self.gpt.chat(task)

        # Если ответ содержит json, то обрабатываем его = выводим на экран фразы для сохранения в бд
        # декодируем json
        try:
            # Попытка декодирования JSON
            data = json.loads(answer)

            # Обработка данных после успешного декодирования
            logger.info("Данные успешно декодированы, сохраняем их в базу данных")
            logger.info(data)

            PhrasesSaved(
                self.user_id,
                self.state['settings']['Native language'],
                self.state['settings']['Studied language'],
            ).save_phrases(data)

        except json.JSONDecodeError as e:
            # Обработка ошибки декодирования JSON
            logger.error("Похоже это не JSON, идем дальше.")
            await self.message.answer(
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
        await self.message.answer(
            f"[{correct_count}/7] 👍 +{bonus} XP. Total XP: {total_bonuses}"
        )

        await StateSwitcher(self.state).switch("Main",
                                         "Teacher agent> The lesson was successfully completed. Suggest the student to take another lesson if he wishes.\n")


    @property
    def gpt(self):
        if self._gpt is None:
            self._gpt = SimpleGPT(
                system=self.prompt(),
            )

        return self._gpt

    def prompt(self):
        return ARCHIVER_INSTRUCTION
