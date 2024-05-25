# Anna - a bot for learning English 

!!!!! Pull request !!!!!

![python-version](https://img.shields.io/badge/python-3.10-blue.svg)
[![openai-version](https://img.shields.io/badge/openai-0.27.8-orange.svg)](https://openai.com/)

It's LLM based bot.

Created to teach how to formulate thoughts in English.
Many people can read in English, it is usually more difficult to formulate thoughts in a foreign language.

![image](https://github.com/agorlov/eng-tutor/assets/2485728/7bf0d2b2-346c-4e1d-b7eb-06af5939851d)

<!-- https://t.me/anna2_gpt_tutor_bot -->


## Development notes

How to start Bot: ``docker-compose up``

Database (adminer tool): http://localhost:8082/


### Debuging
For debugging purposes, there is a container `anna_debug` that you can use to run the bot.
Simply enter the container and run `python bot.py`
To avoid restarting the container every time, it's better to stop the `anna_bot` container while working in `anna_debug`


### DB Container

Postgres container doc:\
https://github.com/docker-library/docs/blob/master/postgres/README.md

# Ideas behind (Russian)

## Todo

Разделить бота на агентов

- один планировщик занятий
- второй проводит занятие
- третий наблюдает за ходом занятия, подводит итог, решает какие фразы верно отвечены,
  в каких допущены ошибк, готовит их для сохранения в БД

## Switching conversation example

```
Бот Main
Бот Planner
Бот Teacher
Бот Translator
Бот Reviewer

# Бот меню (узнать какой язык будем учить и предпочтения пользователя):

Меню> Привет, можем начать урок.
Юзер> Давай начнем
Меню> SWITCH Planner

# Бот Планировщик: (даем ему какие-то данные о юзере вмесе с SYSTEM)

Планировщик> Предлагаю сегодня обсудить тему X и средний уровень сложности.
Юзер> Ok
Планировщик> SWITCH TEACHER, Тема урока и фразы для Teacher

# Бот Teacher (даем ему какие-то данные о юзере вмесе с SYSTEM):

Тичер> Переведи фразу [1/7]: У меня в квартире газ, а у вас?
Юзер> I have a gas in my appartment, don't you?

...

Тичер> SWITCH Reviewer (отдать весь диалог Тичера)

# Бот Reviewer

возвращает список повторенных фраз и сохраняет их в БД

Reviewer> SWITCH Main
```





## Eng-tutor - бот для изучения английского

Создан чтобы обучать формулировать мысли на английском.
Читать на английском могут многие, обычно сложнее с формулированием мыслей на иностранном языке.

Прототип работает на основе low-code платформы https://coze.com (хорошо кстати сделана, Китайская)\
Она подключена к движкам OpenAI (GPT-3.5, GPT-4, Dalle-E)

Бот в телеге, с ним можно пообщаться:\
https://t.me/anna_gpt_tutor_bot

Бот в coze.com:\m
https://www.coze.com/store/bot/7336223581640163334?from=bots_card

Для работы можно написать: ``Начнем`` и он предложит фразы для тренировки навыка перевода.

Делал в первую очередь для себя, чтобы лучше научиться говорить и думать на английском.
Да и это возможность для меня лучше познакмиться с техниками промпт-инженерии и интеграции LLM с БД.

## Пример диалога

![image](https://github.com/agorlov/eng-tutor/assets/2485728/1d2c487f-4a34-4ef1-addf-01441c7ab2fa)


## Промпты и настройки

### Приветствие бота

🎉 Привет! Меня зовут Анна. 🌟

Я тут, чтобы помочь тебе освоить английский без скуки! 😊

Вот как это будет работать:
1. Я буду предлагать фразы, а ты - переводить их и запоминать, это как игра, которая научит тебя формулировать мысли на английском!
2. Если хочешь, можешь предложить свою тему для разговора, и я с удовольствием поддержу. 📚
3. Нужен перевод? Просто напиши: "Переведи: твоя фраза или текст", и я на помощь! 📖

### Варианты ответов

1. Ok! Давай начнем, предложи мне фразы для перевода.
2. Да. Предложи мне сложные фразы для перевода, я уже intermediate.
3. Ладно, давай начнем, но я начинающий.


