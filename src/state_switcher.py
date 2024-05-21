from pprint import pprint

class StateSwitcher:

    def __init__(self, state: dict):
        self.state = state

    def switch(self, assistant_name, message):
        assistant_name = assistant_name.strip()
        pprint(self.state)
        print(f"!Assistant: '{assistant_name}'")
        if assistant_name not in self.state['agents']:
            print("!StateSwitcher: Unknown assistant: " + assistant_name)
            raise Exception("Unknown assistant: " + assistant_name)

        print("!StateSwitcher: Switching to " + assistant_name)

        self.state['agent'] = self.state['agents'][assistant_name]

        if message:
            self.state['agent'].run(message)
