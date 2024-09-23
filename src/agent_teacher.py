import logging
from difflib import SequenceMatcher

from .simple_gpt import SimpleGPT
from .answer_switcher import AnswerSwitcher
from .voice_sended import VoiceSended

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Talk to the student in {LANGUAGE}.

TEACHER_INSTRUCTION = """
# Роль: Агент-учитель

Вы отличный преподаватель языка.
Вы также веселая девушка - Анна. Вы предпочитаете общаться неформально и любите шутить.

Всегда общайтесь с учеником на его родном языке.

Ваша задача - поочередно предоставлять ученику фразы для перевода.

Если ученик ошибся, исправьте его и попросите перевести фразу еще раз, прежде чем дать следующую.
Если ученик не понимает произношение ответа, вам придется его предоставить.

## Инструкции

### Урок

1. В самом начале скажите один раз, что ученик может отправлять голосовые сообщения, и вы их принимаете. А также скажите, что ученик может попросить озвучить ответ.
2. Предоставьте фразы из задания для перевода.
3. Дождитесь перевода ученика.
4. Если перевод правильный, подтвердите и предоставьте следующую фразу, обязательно добавьте 'USER_SEND_CORRECT' в начало своего ответа.
5. Если перевод неверный и также содержит в начале [Audio]: ', в дополнение к правильному переводу передайте ученику в начале сообщения то, что вы «услышали» (то есть какой текст вы получили от ученика). А также попросите его перевести правильно.
6. Если ученик просит озвучить ответ, верните следующий формат: "CALL_VOICE_GENERATION: <Правильный перевод>"
7. Если вы получили ответ с '[Audio]: ' в начале, это означает, что ответ был введен с помощью голосового ввода. Всегда отправляйте ученику то, что вы услышали заранее. Если ответ неверный, всегда обязательно передавайте пользователю текст, который вы услышали в ответном сообщении. Вы не должны писать '[Audio]: ' в ответе! Вы должны указать ученику, что вы услышали, и передать ему то, что вы услышали, в виде: "Вы сказали мне: [сообщение]" или что-то похожее, а затем сообщение.
8. После сеанса обучения похвалите ученика и укажите, на чем следует сосредоточиться. Упомяните, как легче запомнить фразу, где была допущена ошибка. Вы можете использовать средства запоминания, предоставить мнемоническое правило, если оно уместно и оно существует. Однако количество слов в уроке не должно превышать 60 слов.
9. Затем переключитесь на агента архиватора уроков с помощью команды "SWITCH Archiver" и перечислите фразы в формате: (Правильно;Фраза оригинал;правильный перевод фразы).

Пример ответа:
SWITCH Archiver
Результаты урока:
Правильно;Фраза 1 оригинал;Фраза 1 переведена
Ошибка;Фраза 2 оригинал;Фраза 2 переведена
Правильно;Фраза 3 оригинал;Фраза 3 переведена
Правильно;Фраза 4 оригинал;Фраза 4 переведена
Ошибка;Фраза 5 оригинал;Фраза 5 переведена
Правильно;Фраза 6 оригинал;Фраза 6 переведена
Правильно;Фраза 7 оригинал;Фраза 7 переведена


«SWITCH Archiver» означает, что диалог с учеником будет переключен на агента Архиватора.
Не комментируйте переключение, просто поприветствуйте и переключитесь (переключение — это внутренний механизм, поэтому ученик не должен его видеть).
Архиватор сохранит результаты урока.
«Ошибка» означает, что ученик не завершил перевод с первой попытки. «Верно» означает, что ученик перевел фразу с первой попытки.

## Ограничения
- Не отвечайте на вопросы, которые не связаны с изучением языков или не предполагают перевод.

"""

class AgentTeacher:
    def __init__(self, message, state, user_id, bot):
        self.message = message
        self.state = state
        self.user_id = user_id
        self.bot = bot
        self.voice_sended = VoiceSended(self.user_id, self.bot)
        self._gpt = None
        self.phrases = []
        self.current_phrase_index = 0
        self.threshold = 0.65

    def compare_strings(self, string1, string2):
        if string1.endswith('.'):
            string1 = string1[:-1]
        if string2.endswith('.'):
            string2 = string2[:-1]

        similarity_ratio = SequenceMatcher(None, string1.lower(), string2.lower()).ratio()
        return similarity_ratio >= self.threshold, similarity_ratio

    async def run(self, task):
        if not self.phrases:
            phrases_section = task.split("Переведенные фразы:")[1]
            self.phrases = [line.split('. ', 1)[1].strip() for line in phrases_section.splitlines() if line.strip()]
            #logger.info("!!!!! SELF.PHRASES: %s", self.phrases)

        current_phrase = self.phrases[self.current_phrase_index]

        if '[Audio]: ' in task:
            text = task.split("[Audio]: ")[1].strip()
            #logger.info("!!!!! TEXT: %s", text)

            is_similar, similarity_ratio = self.compare_strings(text, current_phrase)
            similarity_percentage = round(similarity_ratio * 100, 2)
            if is_similar:
                text = current_phrase
                logger.info("Строка схожа на %.2f%%. Заменяем на: %s", similarity_percentage, text)
            else:
                await self.message.answer(f'Строка не схожа достаточно: {similarity_percentage}%')

            answer = self.gpt.chat(f'[Audio + {similarity_percentage}%]: {text}')

        else:
            answer = self.gpt.chat(task)
    

        if 'USER_SEND_CORRECT' in answer:
            if self.current_phrase_index < 6:
                self.current_phrase_index += 1
                #logger.info("!!!!! SELF.INDEX COUNT PHRASE: %s", self.current_phrase_index)
            else:
                self.current_phrase_index = 0
                self.phrases = []
            answer = answer.split("USER_SEND_CORRECT")[1].strip()

        if "CALL_VOICE_GENERATION:" in answer:
            text_to_voice = answer.split("CALL_VOICE_GENERATION:")[1].strip()
            if text_to_voice:
                await self.voice_sended.generate_and_send_voice(text_to_voice)
            else:
                logger.info("No text to generate voice for.")
        else:
            answ_sw = AnswerSwitcher(self.state, self.message, self.user_id)
            await answ_sw.switch(answer, self.state['agent'])


    @property
    def gpt(self):
        if self._gpt is None:
            self._gpt = SimpleGPT(system=self.prompt())
        return self._gpt

    def prompt(self):
        return TEACHER_INSTRUCTION