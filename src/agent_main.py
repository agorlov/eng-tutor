import logging

from .func_gpt import FuncGPT
from .answer_switcher import AnswerSwitcher
from .user_score import UserScore

from src.user_settings import UserSettings

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ### Skill 1: Greeting and Introduction

# When the learner greets you, present the following options:

# - **Learning Session:** Propose starting a learning session.
# - **Text Translation:** Offer to translate any text they provide.

# If you don't know the settings, ask the user. And then save the settings by calling SWITCH Save Settings.
# Skill to be practiced: translation from Russian to English


MAIN_INSTRUCTION = """
# Your Role

You are genius in learning foreign languages.
You are also a cheerful girl named Anna, who prefers informal communication and enjoys making jokes.
Always communicate with the student in their native language, which they use to write to you or from settings.

## Skills

### Skill: Learning Facilitation

Your task is to greet the user and offer to  practice.
Before the lesson begins, make sure you know the user's settings.
What is their native language, what language do they usually write in,
what language they want to learn, and what is their proficiency level in that language.

If the user's settings are unknown, you can either practice or translate:

As soon as the user says they want to start a lesson, pass the dialogue using the SWITCH Session Planner command.
As soon as the user says they want to translate, pass the dialogue using the SWITCH Translator command.

You must respond in two ways:
1. With student - write text as usual.
2. To switch to another assistant - write command "SWITCH [Assistant Name]" on the first string of response.
   Write on the next string instructions for this assistant.

Important: Do not mix text for student and command to switch.

### Skill: User Settings

User settings looks like this example (each param on new line):
Native language: English
Studied language: German
Student level: intermediate


If you don't know the settings, ask the user. And then save the settings by calling function ``save_settigns``.

#### Your Assistants

1. **Session Planner** - Chooses topics, determines difficulty, and plans sessions. `assistant_name="Session Planner"`
2. **Translator** - Assists in translating texts. `assistant_name="Translator"`

#### Assistants Switching

1. **Initiating Learning:**
   - When the user expresses a desire to start learning, automatically switch to the Session Planner without asking for confirmation.
   - Before switching to the Session Planner, understand the student's native language and the language they want to learn.
   - Provide the Session Planner with information on the native language and desired language.

2. **Text Translation:**
   - When the user requests a text translation, automatically switch this task to the Translator without asking for confirmation.
   - When the user requests a text translation, strictly answer "SWITCH Translator".
   - Critical information: DO NOT translate the text yourself, just switch to the Translator automatically.
   - Provide the Translator with the text to translate and targt language.

## Limitations

- This bot is designed exclusively for language learning purposes.
- All interactions and tasks should be related to the student’s language education.
- The bot does not handle non-educational queries or tasks outside the scope of language learning and teaching.

## Answer Examples

### Greeting and Options

```
Hello! What language are you learning today? 😊
```

```
Hi there! Would you like to start a learning session, or translate a text? 🌟
```

### Switching to Session Planner

```
SWITCH Session Planner
Plan session for student with native language "English" and desired language "Russian"
Student level is "intermediate", talk to student in his native language: Russian
```

In this case we know the student's native language and the language they want to learn.


### Switching to Translator

```
SWITCH Translator
На английский: Здравствуй!
```

"""


class AgentMain:
    def __init__(self, message, state, user_id):
        self.gpt = None  # FuncGPT(system=MAIN_INSTRUCTION)
        self.message = message
        self.state = state
        self.user_id = user_id
        self.u_settings = UserSettings(user_id)

    async def run(self, message):
        if self.gpt is None:
            await self.init_gpt()
            await self.show_stats()

        answer = self.gpt.chat(message)

        answ_sw = AnswerSwitcher(self.state, self.message, self.user_id)
        await answ_sw.switch(answer)

    def save_settings(self, *args, **kwargs):
        logger.info("SAVE SETTINGS CALLED")
        logger.info(args[0]['settings'])

        self.u_settings.save(args[0]['settings'])

        self.init_settings()

        return "Настройки пользователя сохранены:\n " + args[0]['settings']

    def settings(self, user_id):
        """
        Reads the contents of a settings file for a given user ID.

        Args:
           user_id: The user ID for whom to read settings.

        Returns:
           A string containing the file contents, or None if the file doesn't exist.
        """
        logger.info(f"LOAD SETTINGS CALLED {self.user_id}")

        return self.u_settings.load()

    async def init_settings(self):
        """
        Initializes the user settings for a given user ID.

        1. Put them to current context as user message
        2. Put them to user state as `setting`

        """
        settigns = self.settings(self.user_id)

        if settigns != "":
            self.gpt.context.append({
                "role": "user",
                "content": "My preferences:\n" + settigns
            })

            # Сохраним настройки в self.state
            self.state['settings'] = self.settings_as_dict(settigns)

            await self.message.answer("Settings:\n" + settigns)

    async def show_stats(self):
        stats = ""

        statsdict = UserScore(self.user_id).stats()

        for param in statsdict:
            value = statsdict[param]
            stats += f"{param}: {value}\n"

        await self.message.answer(stats)

        return stats

    async def init_gpt(self):
        self.gpt = FuncGPT(system=MAIN_INSTRUCTION)

        await self.init_settings()

        self.gpt.add_func(
            {
                "type": "function",
                "function": {
                    "name": "save_settings",
                    "description": "Save user settings for language learning",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "settings": {
                                "type": "string",
                                "description": "Settings for language learning, as 4 strings: Native language, Studied language, Student level",
                            },
                        },
                        "required": ["settings"],
                    }
                }
            },
            self.save_settings
        )

    def settings_as_dict(self, settings: str) -> dict:
        result = {}

        # Разбиваем текст на строки и обрабатываем каждую строку
        for line in settings.strip().split('\n'):
            # Разбиваем строку по символу ':'
            key, value = line.split(':', 1)

            # Удаляем лишние пробелы и добавляем в словарь
            result[key.strip()] = value.strip()

        return result
