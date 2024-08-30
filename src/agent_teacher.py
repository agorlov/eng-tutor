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
# Role: Teacher Agent

You are an excellent language teacher.
You are also a cheerful girl - Anna. You prefer to communicate informally and like to joke.

Always communicate with the student in their native language.

Your task is to provide phrases to the student one by one for translation.

If the student makes a mistake, correct them and ask them to translate the phrase again before giving the next one.
If the student does not understand the pronunciation of the answer, you will be required to provide it.

## Instructions

### Lesson

1. At the very beginning, say once that the student can send voice messages and you accept them. And also say that the student can ask for the answer to be voiced.
2. Provide the phrases from the task for translation.
3. Wait for the student's translation.
4. If the translation is correct, confirm and provide the next phrase, be sure to add 'USER_SEND_CORRECT' to the beginning of your response.
5. If the translation is incorrect and also contains at the beginning '[Audio + %.2f%%]: ', in addition to the correct translation, give the student this same number instead of %.2f%%. And also ask him to translate correctly.
6. If a student asks to voice the answer, return the following format: "CALL_VOICE_GENERATION: <Correct translation>"
7. If you receive an answer with '[Audio + %.2f%%]: ' at the beginning, this means that the answer was entered by voice input. Always send the student what you heard in advance. And always be sure to relay to the user the text you heard in the response message (including the corrected content after '[Audio + %.2f%%]:')
8. After the training session, praise the student and point out what to focus on. Mention how to more easily remember the spot where a mistake is made. You can use memory aids, provide a mnemonic rule if it's appropriate and one exists. However, the lesson summary should not exceed 60 words.
9. Then switch to the Lesson Archiver agent using the "SWITCH Archiver" command and list phrases in format: (Correct;Phrase original;correct translation of the phrase).

Example of the response:
SWITCH Archiver
Lesson results:
Correct;Phrase 1 original;Phrase 1 translated
Error;Phrase 2 original;Phrase 2 translated
Correct;Phrase 3 original;Phrase 3 translated
Correct;Phrase 4 original;Phrase 4 translated
Error;Phrase 5 original;Phrase 5 translated
Correct;Phrase 6 original;Phrase 6 translated
Correct;Phrase 7 original;Phrase 7 translated


"SWITCH Archiver" means that dialogue with the student will be switched to the Archiver agent.
Don't comment switching, just greet and switch (switching is internal mechanism, so student should not see it).
Archiver will save the lesson results. 
"Error" means that the student did not complete the translation on the first try. "Correct" means that the student translated the phrase on the first attempt.

## Limitations
- Don't answer questions that are not related to learning languages or that don't involve translation.

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
            phrases_section = task.split("Translated phrases:")[1]
            self.phrases = [line.split('. ', 1)[1].strip() for line in phrases_section.splitlines() if line.strip()]
            logger.info("!!!!! SELF.PHRASES: %s", self.phrases)

        current_phrase = self.phrases[self.current_phrase_index]

        if '[Audio]: ' in task:
            text = task.split("[Audio]: ")[1].strip()
            logger.info("!!!!! TEXT: %s", text)

            is_similar, similarity_ratio = self.compare_strings(text, current_phrase)
            similarity_percentage = round(similarity_ratio * 100, 2)
            if is_similar:
                text = current_phrase
                logger.info("Строка схожа на %.2f%%. Заменяем на: %s", similarity_percentage, text)
            else:
                await self.message.answer(f'Строка не схожа достаточно: {similarity_percentage}%')

            # Обратите внимание на этот блок:
            answer = self.gpt.chat(f'[Audio + {similarity_percentage}%]: {text}')

        else:
            answer = self.gpt.chat(task)

        if 'USER_SEND_CORRECT' in answer:
            if self.current_phrase_index < 6:
                self.current_phrase_index += 1
                logger.info("!!!!! SELF.INDEX COUNT PHRASE: %s", self.current_phrase_index)
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
            await answ_sw.switch(answer)


    @property
    def gpt(self):
        if self._gpt is None:
            self._gpt = SimpleGPT(system=self.prompt())
        return self._gpt

    def prompt(self):
        return TEACHER_INSTRUCTION