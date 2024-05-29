from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASEURL
import json

from .func_gpt import FuncGPT
from .state_switcher import StateSwitcher

class SwitchGPT:
    """
    GPT client, witch switching agents function inside
    """

    def __init__(self, system, state, model = "gpt-4o", oai = None, func_gpt = None):
        """
        Simple GPT client.

        Args:
            system: system prompt (requred)
            state: user state and his context and his agents (required)
            model: "gpt-3.5-turbo-0613", "gpt-3.5-turbo"  gpt-3.5-turbo-instruct            
            oai: OpenAI instance
        """

        self.switcher = StateSwitcher(state)

        if func_gpt is None:
            self.orig = FuncGPT(system=system, model=model, oai=oai)
            # @todo bad idea to call methods from constructor 
            self.add_switch_func()
        else:
            self.orig = func_gpt

    def chat(self, message):
        print("!SwitchGPT: " + message)
        return self.orig.chat(message)
    
    # вывести контекст для отладки без system, в виде диалога
    def debug(self):
        return self.orig.debug()
    
    @property
    def context(self):
        return self.orig.context
    
    def add_func(self, descr, func):
        return self.orig.add_func(descr, func)
    
    def add_switch_func(self):
        self.orig.add_func(
            descr = {
                "type": "function",
                "function": {
                    "name": "switch_agent",
                    "description": "Switch agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Agent name",
                            },
                            "task": {
                                "type": "string",
                                "description": "Task or comment for Session Planner Agent"
                            }
                        },
                        "required": ["agent_name", "task"],
                    }
                }
            },
            func = self.switch_func
        )
    
    def switch_func(self, *args, **kwargs):
        print("!!!!SWITCH FUNC CALLED!!!!")

        agent_name = args[0]['agent_name']
        task = args[0]['task']
        
        print(f"!Task to {agent_name}: {task}")
       
        self.switcher.switch(agent_name, task)

    


    
