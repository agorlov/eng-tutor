import logging
import requests
import json
from .agent_translator import AgentTranslator
from .agent_session_planner import AgentSessionPlanner
from .simple_gpt import SimpleGPT
from .func_gpt import FuncGPT
from .answer_switcher import AnswerSwitcher
import textwrap
import os

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

Твоя задача поприветствовать пользователя и предложить позаниматься или переводить текст.
Перед началом урока убедись, что тебе известны настройки пользователя. Какой язык для него родной, он обычно на нем пишет,
какой язык он хочет учить, какой у него уровень владения языком.

Если настройки пользователя не известны, то можно заниматься или переводить:

Как только пользователь скажет, что хочет начать урок - передай диалог с помощью команды SWITCH Session Planner.
Как только пользователь скажет, что хочет перевести - передай диалог с помощью команды SWITCH Translator.

You must respond in two ways:
1. With student - write text as usual.
2. To switch to another assistant - write command "SWITCH [Assistant Name]" on the first string of response.
   Write on the next string instructions for this assistant.

Important: Do not mix text for student and command to switch.

### Skill: User Settings

User settings looks like this:
   Native language: Russian
   Studied language: English
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
    def __init__(self, tg, state, user_id):
        self.gpt = None # FuncGPT(system=MAIN_INSTRUCTION)
        self.tg = tg
        self.state = state
        self.user_id = user_id
    
    def run(self, message):
        if self.gpt is None:
            self.init_gpt()

        answer = self.gpt.chat(message)

        answ_sw = AnswerSwitcher(self.state, self.tg, self.user_id)
        answ_sw.switch(answer)

    def save_settings(self, *args, **kwargs):
        print("!!!!SAVE SETTINGS CALLED!!!!")
        print(args[0]['settings'])

        # Формируем путь к файлу настроек пользователя
        file_path = f'data/settings/{self.user_id}.txt'
         
        # Сохраняем строку настроек в файл
        with open(file_path, 'w') as file:
           file.write(args[0]['settings'])
    
        print(f"!Настройки пользователя {self.user_id} сохранены в файле {file_path}")

        return "Настройки пользователя сохранены:\n " + args[0]['settings']


    def settings(self, user_id):
         """
         Reads the contents of a settings file for a given user ID.

         Args:
            user_id: The user ID for whom to read settings.

         Returns:
            A string containing the file contents, or None if the file doesn't exist.
         """

         print(f"!!!!LOAD SETTINGS CALLED!!!! {self.user_id}")

         file_path = os.path.join("data", "settings", f"{user_id}.txt")

         try:
            with open(file_path, "r") as file:
               contents = file.read()
               return contents
         except FileNotFoundError:
            return ""


    def init_gpt(self):
        self.gpt = FuncGPT(system=MAIN_INSTRUCTION)
        self.gpt.context.append({
            "role": "user",
            "content": "My preferences:\n" + self.settings(self.user_id)
        })

        
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
                     "required": [ "settings" ],
                  }
               }
            },
            self.save_settings
      )