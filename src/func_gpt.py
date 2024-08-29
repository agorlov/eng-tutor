import logging
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASEURL
import json

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuncGPT:

    def __init__(self, system, model="gpt-4o-mini", oai=None):
        """
        Simple GPT client.

        Args:
            system: system prompt
            model: "gpt-3.5-turbo-0613", "gpt-3.5-turbo"  gpt-3.5-turbo-instruct
            oai: OpenAI instance
        """

        self.model = model
        self.context = [
            {"role": "system", "content": system}
        ]

        if oai is None:
            self.oai = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASEURL)
        else:
            self.oai = oai

        self.funcs_desc = []
        self.funcs = {}

    def chat(self, message):
        if message and isinstance(message, str):
            self.context.append({"role": "user", "content": message})
        else:
            logger.error(f"Invalid user message: {message}")
            return "Invalid message content."

        resp = self.oai.chat.completions.create(
            messages=self.context,
            model=self.model,
            tools=self.funcs_desc,
            tool_choice="auto"
        )

        if resp.choices[0].message.tool_calls:
            func_name = resp.choices[0].message.tool_calls[0].function.name
            if func_name not in self.funcs:
                raise Exception(f"Unknown function: {func_name}")

            args = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
            func = self.funcs[func_name]
            func_result = func(args)

            if func_result and isinstance(func_result, str):
                self.context.append({"role": "function", "name": func_name, "content": func_result})

            follow_up = self.oai.chat.completions.create(
                messages=self.context,
                model=self.model,
                tools=self.funcs_desc,
                tool_choice="auto"
            )

            final_output = follow_up.choices[0].message.content
            if final_output and isinstance(final_output, str):
                self.context.append({"role": "assistant", "content": final_output})
            else:
                logger.error("FuncGPT: Received invalid response from assistant.")
                return "Invalid assistant response."

            return final_output

        assistant_content = resp.choices[0].message.content
        if assistant_content and isinstance(assistant_content, str):
            self.context.append({"role": "assistant", "content": assistant_content})

        return assistant_content

    # вывести контекст для отладки без system, в виде диалога
    def debug(self):
        return "\n".join(
            f"[{msg['role']}]" + msg["content"]
            for msg in self.context[1:]
        )

    def add_func(self, descr, func):
        logger.info("!!!add_func!!!")
        """
        Add function to the list of functions.

        Args:
            descr: function description
            func: function

        descr example:
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
        """

        self.funcs_desc.append(descr)

        if not callable(func):
            raise TypeError(f"Function {func} is not callable")

        self.funcs[descr['function']['name']] = func
