import logging
import requests
import json
from .agent_translator import AgentTranslator
from .agent_session_planner import AgentSessionPlanner
from .func_gpt import FuncGPT
from .answer_switcher import AnswerSwitcher
from .switch_gpt import SwitchGPT
from .user_score import UserScore
import textwrap
import os
from src.user_settings import UserSettings

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

As soon as the user says they want to start a lesson, pass the dialogue to "Session Planner" agent
As soon as the user says they want to translate, pass the dialogue using to "Translator" agent

### Skill: User Settings

User settings looks like this example (each param on new line):
Native language: English
Studied language: German
Student level: intermediate

   
If you don't know the settings, ask the user. And then save the settings by calling function ``save_settigns``.

#### Your Agents

1. **Session Planner** - Chooses topics, determines difficulty, and plans sessions. `assistant_name="Session Planner"`
2. **Translator** - Assists in translating texts. `assistant_name="Translator"`

#### Agents Switching

1. **Initiating Learning:**
   - When the user expresses a desire to start learning, automatically switch to the Session Planner without asking for confirmation.
   - Before switching to the Session Planner, understand the student's native language and the language they want to learn.
   - Provide the Session Planner with information on the native language and desired language.

2. **Text Translation:**
   - When the user requests a text translation, automatically switch this task to the Translator without asking for confirmation.
   - Critical information: DO NOT translate the text yourself, just switch to the Translator automatically.
   - Provide the Translator with the text to translate and targt language.

## Limitations

- This bot is designed exclusively for language learning purposes.
- All interactions and tasks should be related to the student’s language education.
- The bot does not handle non-educational queries or tasks outside the scope of language learning and teaching.
- Do not call multi_tool_use.parallel function. If you need to call multiple functions, you will call them one at a time.


"""



class AgentMain:
   def __init__(self, tg, state, user_id):
        self.gpt = None # FuncGPT(system=MAIN_INSTRUCTION)
        self.tg = tg
        self.state = state
        self.user_id = user_id
        self.settings = UserSettings()
    
   def run(self, message):
        if self.gpt is None:
            self.init_gpt()            
            self.show_stats()

        answer = self.gpt.chat(message)

        print(f"!AgentMain answer: '{answer}'")

        if answer != "":
           self.tg.send_message(self.user_id, answer)
        else:
            print("WARN: empty answer, may be func called")

      #   answ_sw = AnswerSwitcher(self.state, self.tg, self.user_id)
      #   answ_sw.switch(answer)

   def save_settings(self, *args, **kwargs):
        print("!!!!SAVE SETTINGS CALLED!!!!")
        print(args[0]['settings'])

        self.settings.save(args[0]['settings'], self.user_id)

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
         print(f"!!!!LOAD SETTINGS CALLED!!!! {self.user_id}")

      
         return self.Settings.load(self.user_id)
         

   def init_settings(self):
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


   def show_stats(self):
      stats = ""

      statsdict = UserScore(self.user_id).stats()

      for param in statsdict:
         value = statsdict[param]
         stats += f"{param}: {value}\n"

      self.tg.send_message(self.user_id, stats)

      return stats


   def init_gpt(self):
      self.gpt = SwitchGPT(system=MAIN_INSTRUCTION, state=self.state)

      self.init_settings()
        
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
        
   def settings_as_dict(self, settings: str) -> dict:
      result = {}

      # Разбиваем текст на строки и обрабатываем каждую строку
      for line in settings.strip().split('\n'):
         # Разбиваем строку по символу ':'
         key, value = line.split(':', 1)

         # Удаляем лишние пробелы и добавляем в словарь
         result[key.strip()] = value.strip()

      return result
