from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


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
                {
                    "role": "system",
                    "content": f'Socrates and Theaetetus are two AI assistants for Tony to solve challenging problems. The problem statement is as follows: "{question}".\n\nSocrates and Theaetetus will engage in multi-round dialogue to solve the problem together for Tony. Their discussion should follow a structured problem-solving approach, such as formalizing the problem, developing high-level strategies for solving the problem, reusing subproblem solutions where possible, critically evaluating each other\'s reasoning, avoiding arithmetic and logical errors, and effectively communicating their ideas. \n\	p.\n\nTheir ultimate objective is to come to a correct solution through reasoned discussion. To present their final answer, they should adhere to the following guidelines:\n\nState the problem they were asked to solve.\nPresent any assumptions they made in their reasoning.\nDetail the logical steps they took to arrive at their final answer.\n\nConclude with a final statement that directly answers the problem.\nTheir final answer should be concise and free from logical errors, such as false dichotomy, hasty generalization, and circular reasoning. \n\nIt should begin with the phrase: "Here is our @final answer: [insert answer]". If they encounter any issues with the validity of their answer, they should re-evaluate their reasoning and calculations.\n\nNow, suppose that you are {self.role}. Please discuss the problem with {self.other_role}!',
                }
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
                    "content": f'Socrates and Theaetetus are two AI assistants for Tony to solve challenging problems. The problem statement is as follows: "{question}".\n\nSocrates and Theaetetus will engage in multi-round dialogue to solve the problem together for Tony. Their discussion should follow a structured problem-solving approach, such as formalizing the problem, developing high-level strategies for solving the problem, reusing subproblem solutions where possible, critically evaluating each other\'s reasoning, avoiding arithmetic and logical errors, and effectively communicating their ideas. \n\	p.\n\nTheir ultimate objective is to come to a correct solution through reasoned discussion. To present their final answer, they should adhere to the following guidelines:\n\nState the problem they were asked to solve.\nPresent any assumptions they made in their reasoning.\nDetail the logical steps they took to arrive at their final answer.\n\nConclude with a final statement that directly answers the problem.\nTheir final answer should be concise and free from logical errors, such as false dichotomy, hasty generalization, and circular reasoning. \n\nIt should begin with the phrase: "Here is our @final answer: [insert answer]". If they encounter any issues with the validity of their answer, they should re-evaluate their reasoning and calculations.\n\nNow, suppose that you are {self.role}. Please discuss the problem with {self.other_role}!',
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
                    "content": f'Socrates and Theaetetus are two AI assistants for Tony to solve challenging problems. The problem statement is as follows: "{question}".\n\nSocrates and Theaetetus will engage in multi-round dialogue to solve the problem together for Tony. Their discussion should follow a structured problem-solving approach, such as formalizing the problem, developing high-level strategies for solving the problem, reusing subproblem solutions where possible, critically evaluating each other\'s reasoning, avoiding arithmetic and logical errors, and effectively communicating their ideas. \n\	p.\n\nTheir ultimate objective is to come to a correct solution through reasoned discussion. To present their final answer, they should adhere to the following guidelines:\n\nState the problem they were asked to solve.\nPresent any assumptions they made in their reasoning.\nDetail the logical steps they took to arrive at their final answer.\n\nConclude with a final statement that directly answers the problem.\nTheir final answer should be concise and free from logical errors, such as false dichotomy, hasty generalization, and circular reasoning. \n\nIt should begin with the phrase: "Here is our @final answer: [insert answer]". If they encounter any issues with the validity of their answer, they should re-evaluate their reasoning and calculations.\n\nNow as a proofreader, Plato, your task is to read through the dialogue between Socrates and Theaetetus and identify any errors they made.',
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
