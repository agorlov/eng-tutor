from .state_switcher import StateSwitcher

class AnswerSwitcher:
    """
    Переключенный агент, в зависимости от ответа от агента
    """

    def __init__(self, state, tg, user_id):
        self.state = state
        self.tg = tg
        self.switcher = StateSwitcher(state)
        self.user_id = user_id

    def switch(self, answer: str) -> None:
        """
        Если в ответе есть SWITCH [Assistant Name], то переключаемся на другого ассистента,
        а если нет, то отправляем сообщение студенту
        """
        
        if answer.startswith("SWITCH"):
            firstline = answer.splitlines()[0]
            assistant_name = firstline.split(maxsplit=1)[1]
            
            # взять вторую и последующие строки ответа из answer
            task = answer.splitlines()[1:]
            task = '\n'.join(task)
            
            print(f"!Task to {assistant_name}: {task}")

            self.switcher.switch(assistant_name, task)
        else:
            print("!Answer to user: " + answer)
            self.tg.send_message(self.user_id, answer)
                