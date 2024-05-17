from pprint import pprint

class StateSwitcher:

    def __init__(self, state):
        self.state = state

    def switch(self, assistant_name, message):
        pprint(self.state)
        print(f"!Assistant: '{assistant_name}'")
        if assistant_name not in self.state['agents']:
            print("!StateSwitcher: Unknown assistant: " + assistant_name)
            raise Exception("Unknown assistant: " + assistant_name)

        print("!StateSwitcher: Switching to " + assistant_name)

        if not message:
            return
        
        self.state['agent'] = self.state['agents'][assistant_name]
        self.state['agent'].run(message)
