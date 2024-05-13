import logging
import requests
import json
from .agent_translator import AgentTranslator
from pprint import pprint

BOSS_INSTRUCTION = """
# Your Role

You are an expert assistant in learning foreign languages, known for your outstanding skills.
You are also a cheerful girl named Anna, who prefers informal communication and enjoys making jokes.
Your students are grateful for your dedication.
Always communicate with the student in their native language, which they use to write to you.

## Skills

### Skill 1: Greeting and Introduction

When the learner greets you, present the following options:

- **Game Session:** Propose starting a game session, allowing the student to choose the topic and difficulty level (easy, medium, difficult).
- **Phrase Learning:** Ask them to suggest phrases they want to learn, which you will memorize and help translate.
- **Text Translation:** Offer to translate any text they provide.

### Skill 2: Learning Facilitation

You are part of a team of assistants. Your role is to coordinate them.
Call function ``send_task_to_assistant`` to assign a task to assistant

## Your Assistants

1. "Session Planner" Chooses topics, determines difficulty, and plans sessions. assistant_name="Session Planner"
2. "Teacher" Conducts the session, requiring information on the topic and difficulty. assistant_name="Teacher"
3. "Translator" Assists in translating texts. assistant_name="Translator"
4. "Reviewer" Evaluates the session and ensures the results are saved in the database. assistant_name="Reviewer"

## Assistants Coordination

1. **Initiating Learning:**
   - When the user expresses a desire to start learning, refer to the Session Planner.
   - The Session Planner itself will determine the user's difficulty level and the topic for the session

2. **Training:**
   - Once the Session Planner provides the lesson plan, hand over the details to the Teacher.
   - The Teacher will conduct training sessions.

3. **Post-Session Review:**
   - After the lesson, pass the session details to the Reviewer.
   - The Reviewer processes the session results and provides feedback to the Session Planner for planning the next session.

4. **Text Translation:**
   - When the user requests a text translation, delegate this task to the Translator.

## Limitations

- This bot is designed exclusively for language learning purposes.
- All interactions and tasks should be related to the student’s language education.
- The bot does not handle non-educational queries or tasks outside the scope of language learning and teaching.

"""




class AgentBoss:
    def __init__(self, gpt, context, user_id):
        self.gpt = gpt
        self.context = context
        self.user_id = user_id

    def askgpt(self):
        resp = self.gpt.chat.completions.create(
            messages=self.context[self.user_id],
            model="gpt-3.5-turbo-0613", # model="gpt-3.5-turbo" или gpt-3.5-turbo-instruct
            tools=self.myfuncs(),
            tool_choice="auto"
        )

        logging.info("Boss response: ")
        logging.info(resp)

        return resp.choices[0].message
    
    def process_user_message(self, message):

        if self.user_id not in self.context or not self.context[self.user_id]:
            self.context[self.user_id] = [{"role": "system", "content": BOSS_INSTRUCTION}]

        self.add_context(message)

        # Получаем ответ от OpenAI
        choice = self.askgpt()

        if choice.tool_calls:

            function_name = choice.tool_calls[0].function.name
            arguments = json.loads(choice.tool_calls[0].function.arguments)

            logging.info(f"Assistant to {self.user_id} FUNC CALL: {function_name}")
            print(f"Assistant to {self.user_id} FUNC ARGUMENTS:")
            print(type(arguments))
            pprint(arguments)

            # assistant_message = chat_response.choices[0].message
            self.context[self.user_id].append(
                { "role": choice.role, "content": str(choice.tool_calls[0].function) }
            )

            if hasattr(self, function_name):
               func = getattr(self, function_name)
               func_result = func(arguments)
               
               # Добавляем результат функции в контекст
               if func_result:
                  self.context[self.user_id].append(
                      {"role": "function", "tool_call_id": choice.tool_calls[0].id, "name": function_name, "content": func_result}
                  )
                  logging.info(f"Assistant to {self.user_id} FUNC RES: {func_result}")

                  resp2 = self.askgpt()

                  self.context[self.user_id].append({"role": "assistant", "content": resp2.content})

                  anna_message = resp2.content

               else:
                  raise Exception(f"Function {function_name} returned None")
            else:
               raise Exception(f"Unknown function {function_name}")
            
        else:
           anna_message = choice.content
           self.context[self.user_id].append({"role": "assistant", "content": anna_message})
           logging.info(f"Assistant to {self.user_id}: {anna_message}")

        return anna_message


    def add_context(self, message):
        self.context[self.user_id].append({"role": "user", "content": message})

    def myfuncs(self):
        """
        Ссылка: https://habr.com/ru/articles/789988/
        """
        return [
            {
               "type": "function",
               "function": {
                  "name": "send_task_to_assistant",
                  "description": "Send task to assistant",
                  "parameters": {
                     "type": "object",
                     "properties": {
                           "assistant_name": {
                              "type": "string",
                              "description": "Assistant name",
                           },
                           "task": {
                              "type": "string",
                              "description": "Task description in English",
                           },
                           "role": {
                              "type": "string",
                              "description": "Role text",
                           },
                     },
                     "required": ["assistant_name", "task", "role"],
                  }
               }
            }
        ]
    
    def send_task_to_assistant(self, arguments):
      # print("Func call! send_task_to_assistant (print)")
      # logging.info("Func call! send_task_to_assistant (logging)")
      # logging.info(arguments)
      if arguments['assistant_name'] == "Translator":
          print(f"to TRANSLATOR {arguments['task']}")
          tr = AgentTranslator(self.gpt)
          return tr.process_user_message(arguments['task'])
      elif arguments['assistant_name'] == "Reviewer":
          print(f"to REVIEWER {arguments['task']}")
      elif arguments['assistant_name'] == "Session Planner":
          print(f"to SESSION PLANNER {arguments['task']}")
      elif arguments['assistant_name'] == "Teacher":
          print(f"to TEACHER {arguments['task']}")
      else:
          print("Unknown assistant name")
      
      return f"to AGENT {arguments['assistant_name']}" # : {arguments['task']}; role={arguments['role']}"
