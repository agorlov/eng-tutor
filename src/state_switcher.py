from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASEURL


class SimpleGPT:

    def __init__(self, system, model="gpt-4o", oai=None):
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

    def chat(self, message):

        self.context.append({"role": "user", "content": message})

        resp = self.oai.chat.completions.create(
            messages=self.context,
            model=self.model
        )

        self.context.append({"role": "assistant", "content": resp.choices[0].message.content})

        return resp.choices[0].message.content

    # вывести контекст для отладки без system, в виде диалога
    def debug(self):
        return "\n".join(
            f"[{msg['role']}]" + msg["content"]
            for msg in self.context[1:]
        )


