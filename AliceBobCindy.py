from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

with open("prompts/socrates.txt", "r") as file:
    SOCRATES_PROMPT = file.read()
with open("prompts/theaetetus.txt", "r") as file:
    THEAETETUS_PROMPT = file.read()
with open("prompts/plato.txt", "r") as file:
    PLATO_PROMPT = file.read()


class SocraticGPT:
    def __init__(self, role, n_round=10, model="gpt-4o-mini"):
        self.role = role
        self.model = model
        self.n_round = n_round

        if self.role == "Socrates":
            self.other_role = "Theaetetus"
        elif self.role == "Theaetetus":
            self.other_role = "Socrates"

        self.history = []

    def set_question(self, question):
        if self.role == "Socrates":
            self.history.append(
                {"role": "system", "content": SOCRATES_PROMPT + question}
            )
            self.history.append(
                {
                    "role": "assistant",
                    "content": f"Hi Theaetetus, let's solve this problem together. Please feel free to correct me if I make any mistakes.",
                }
            )
        elif self.role == "Theaetetus":
            self.history.append(
                {
                    "role": "system",
                    "content": THEAETETUS_PROMPT + question,
                }
            )
            self.history.append(
                {
                    "role": "user",
                    "content": f"Hi Theaetetus, let's solve this problem together. Please feel free to correct me if I make any mistakes.",
                }
            )
        elif self.role == "Plato":
            self.history.append(
                {
                    "role": "system",
                    "content": PLATO_PROMPT + question,
                }
            )
            self.history.append(
                {
                    "role": "user",
                    "content": f"Socrates: Hi Theaetetus, let's solve this problem together. Please feel free to correct me if I make any mistakes.",
                }
            )

    def get_response(self, temperature=None):
        try:
            if temperature:
                res = client.chat.completions.create(
                    model=self.model, messages=self.history, temperature=temperature
                )
            else:
                res = client.chat.completions.create(
                    model=self.model, messages=self.history
                )

            msg = res.choices[0].message.content

        except Exception as e:
            if "maximum context length" in str(e):
                # Handle the maximum context length error here
                msg = "The context length exceeds my limit... "
            else:
                # Handle other errors here
                msg = f"I enconter an when using my backend model.\n\n Error: {str(e)}"

        self.history.append({"role": "assistant", "content": msg})
        return msg

    def get_proofread(self, temperature=None):
        pf_template = {
            "role": "user",
            "content": 'The above is the conversation between Socrates and Theaetetus. You job is to challenge their anwers. They were likely to have made multiple mistakes. Please correct them. \nRemember to start your answer with "NO" if you think so far their discussion is alright, otherwise start with "Here are my suggestions:"',
        }
        try:
            if temperature:
                res = client.chat.completions.create(
                    model=self.model,
                    messages=self.history + [pf_template],
                    temperature=temperature,
                )
            else:
                res = client.chat.completions.create(
                    model=self.model, messages=self.history + [pf_template]
                )
            msg = res.choices[0].message.content
        except Exception as e:
            if "maximum context length" in str(e):
                # Handle the maximum context length error here
                msg = "The context length exceeds my limit... "
            else:
                # Handle other errors here
                msg = f"I enconter an error when using my backend model.\n\n Error: {str(e)}"

        if msg[:2] in ["NO", "No", "no"]:
            return None
        else:
            self.history.append({"role": "assistant", "content": msg})
            return msg

    def update_history(self, message):
        self.history.append({"role": "user", "content": message})

    def add_python_feedback(self, msg):
        self.history.append(
            {
                "role": "system",
                "content": f'Excuting the Python script. It returns "{msg}"',
            }
        )

    def add_proofread(self, proofread):
        self.history.append(
            {
                "role": "system",
                "content": f"Message from a proofreader Plato to you two: {proofread}",
            }
        )
