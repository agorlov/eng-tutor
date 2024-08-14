import logging
from pprint import pprint

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StateSwitcher:
    def __init__(self, state: dict):
        self.state = state

    async def switch(self, assistant_name, message):
        assistant_name = assistant_name.strip()
        pprint(self.state)
        logger.info("!Assistant: '%s'", assistant_name)
        if assistant_name not in self.state['agents']:
            logger.info("!StateSwitcher: Unknown assistant: %s", assistant_name)
            raise Exception("Unknown assistant: " + assistant_name)

        logger.info("!StateSwitcher: Switching to %s", assistant_name)

        self.state['agent'] = self.state['agents'][assistant_name]

        if message:
            await self.state['agent'].run(message)
