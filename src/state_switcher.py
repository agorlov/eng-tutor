
class StateSwitcher:
    """
    StateSwitcher - переход к новому состоянию

    @todo возможно лучше назвать AgentSwitched

    Указываем к какому Агенту переключаемся, и опционально передаем для него сообщения.
    Если сообщение есть, то сразу запускаем его.
    """

    def __init__(self, state: dict):
        self.state = state

    def switch(self, assistant_name, message):
        """
        Switch assistant

        Args:
            :param assistant_name:
            :param message:
            :return:
        """
        assistant_name = assistant_name.strip()

        print(f"!Assistant: '{assistant_name}'")
        if assistant_name not in self.state['agents']:
            print("!StateSwitcher: Unknown assistant: " + assistant_name)
            raise Exception("Unknown assistant: " + assistant_name)

        print("!StateSwitcher: Switching to " + assistant_name)

        self.state['agent'] = self.state['agents'][assistant_name]

        if message:
            self.state['agent'].run(message)
