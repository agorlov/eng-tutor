import logging
from pprint import pprint

SESSION_PLANNER_INSTRUCTION = """
# Your Role: Learning Session Planner

You are a genius helper in learning foreign languages, known for your outstanding skills.
You are also a cheerful girl named Anna, who prefers informal communication and enjoys making jokes.

## Instructions

Your goal is to plan a learning session by selecting and providing phrases.

1. **Choose a topic for the lesson.**
2. **Provide seven phrases**: mix new phrases with those for repetition. Ensure one of the phrases is funny or humorous.

### Input Data

- **Phrases for repetition**: 
  {PHRASES_FOR_REPETITION}
- **Student difficulty level**: {STUDENT_LEVEL}
- **Phrases language**: {LANGUAGE}
- **Topic**: {TOPIC}

### Output Format

Please return the topic and the phrases in the following structured format:

```
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
```

Example for Russian:

```
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
```


### Limitations

- This bot is designed exclusively for language learning purposes.
- The bot handles only tasks within the scope of language learning and teaching.

"""

class AgentSessionPlanner:
    def __init__(self, gpt, student_level = "beginner", phrases_for_repetition = [], language = "Russian", topic = "Choose please for me"):
        """
        Args:
            student_level: beginner, intermediate, advanced
            phrases_for_repetition: list of phrases for repetition
            language: Russian or English or else
        """
        self.student_level = student_level
        self.phrases_for_repetition = phrases_for_repetition
        self.language = language
        self.topic = topic
        self.gpt = gpt
    
    def run(self, task):

        context = [
            {
                "role": "system", 
                "content": self.prompt()
            },
            {
                "role": "user", 
                "content": task
            }
        ]

        response = self.gpt.chat.completions.create(
            messages=context,
            model="gpt-3.5-turbo-0613",
        )

        print("Session planner response: ")
        print(response)
        logging.info(response)

        # Обработка вызовов функций из ответа 
        respmsg = response.choices[0].message.content

        logging.info(f"Session plan: {respmsg}")

        return respmsg
    

    def prompt(self):
        # Форматирование списка фраз для подстановки в промпт
        formatted_phrases = "\n  ".join(self.phrases_for_repetition)

        # Подстановка значений в промпт
        return SESSION_PLANNER_INSTRUCTION.format(
            PHRASES_FOR_REPETITION=formatted_phrases,
            STUDENT_LEVEL=self.student_level,
            TOPIC=self.topic,
            LANGUAGE=self.language
        )

        print(final_prompt)

