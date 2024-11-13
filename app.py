from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

from Socratic import *

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "socraticalpaca"
Session(app)

N = 50
last_client_id = 0
session_states = {}


class SessionState:
    def __init__(self, client_id):
        self.client_id = client_id
        self.socrates = SocraticGPT(role="Socrates", n_round=N)
        self.theaetetus = SocraticGPT(role="Theaetetus", n_round=N)
        self.plato = SocraticGPT(role="Plato", n_round=N)
        self.dialog_lead = None
        self.dialog_follower = None
        self.question = None
        self.asked_question = False
        self.in_progress = False
        self.in_progress_sub = False
        self.first_question = True
        self.wait_tony = False
        self.interactive_p = None
        self.all_questions_to_tony = ""


@app.route("/")
def index():
    global last_client_id
    last_client_id += 1
    session["client_id"] = last_client_id
    session_states[last_client_id] = SessionState(last_client_id)
    return render_template("index.html")


@app.route("/active-message")
def active_message():

    global N, last_client_id, session_states

    client_id = int(session["client_id"])
    if client_id > last_client_id:
        print("current session id", client_id)
        print("last_client_id", last_client_id)
        last_client_id = client_id
        session_states[last_client_id] = SessionState(last_client_id)

    session_state = session_states[client_id]

    if session_state.question:
        if not session_state.in_progress:
            session_state.in_progress = True
            session_state.dialog_lead, session_state.dialog_follower = (
                session_state.socrates,
                session_state.theaetetus,
            )
            return jsonify(
                [
                    {
                        "role": "socrates",
                        "response": f"Hi Theaetetus, let's solve this problem together. Please feel free to correct me if I make any logical or mathematical mistakes.\n",
                    }
                ]
            )
        else:
            if (
                session_state.in_progress_sub == False
                and session_state.wait_tony == False
            ):
                session_state.in_progress_sub = True
                msg_list = []
                rep = session_state.dialog_follower.get_response()
                msg_list.append(
                    {
                        "role": session_state.dialog_follower.role.lower(),
                        "response": rep,
                    }
                )
                session_state.dialog_lead.update_history(rep)
                session_state.plato.update_history(
                    f"{session_state.dialog_follower.role}: " + rep
                )

                if (
                    ("@final answer" in rep)
                    or ("bye" in rep)
                    or ("The context length exceeds my limit..." in rep)
                ):
                    session_state.question = None
                    session_state.asked_question = False
                    session_state.in_progress = False
                    session_state.first_question = False
                    session_state.interactive_p = None
                    session_state.socrates.history = []
                    session_state.theaetetus.history = []
                    session_state.plato.history = []

                    if ("@final answer" in rep) or ("bye" in rep):
                        msg_list.append(
                            {
                                "role": "system",
                                "response": "They just gave you their final answer.",
                            }
                        )
                    elif "The context length exceeds my limit..." in rep:
                        msg_list.append(
                            {
                                "role": "system",
                                "response": "The dialog went too long, please try again.",
                            }
                        )
                    print("question:", session_state.question)
                    print("asked_question:", session_state.asked_question)
                    print("in_progress:", session_state.in_progress)
                    print("msg list:")
                    print(msg_list)
                    print("end conversation reset")
                    session_state.in_progress_sub = False

                    return jsonify(msg_list)

                else:
                    pr = session_state.plato.get_proofread()
                    if pr:
                        msg_list.append({"role": "plato", "response": pr})
                        session_state.socrates.add_proofread(pr)
                        session_state.theaetetus.add_proofread(pr)

                    session_state.dialog_lead, session_state.dialog_follower = (
                        session_state.dialog_follower,
                        session_state.dialog_lead,
                    )

                print("question:", session_state.question)
                print("asked_question:", session_state.asked_question)
                print("in_progress:", session_state.in_progress)
                print("msg list:")
                print(msg_list)
                session_state.in_progress_sub = False
                return jsonify(msg_list)

            else:
                print("under processing")
                return jsonify([])

    elif not session_state.asked_question:
        session_state.asked_question = True
        print("question:", session_state.question)
        print("asked_question:", session_state.asked_question)
        print("in_progress:", session_state.in_progress)
        print("ask user's question")
        if session_state.first_question:
            msg = "What's your question?"
        else:
            msg = "Do you have more questions?"
        return jsonify([{"role": "system", "response": msg}])
    else:
        print("question:", session_state.question)
        print("asked_question:", session_state.asked_question)
        print("in_progress:", session_state.in_progress)
        print("no question skip")
        return jsonify([])


@app.route("/chat", methods=["POST"])
def chat():
    global session_states
    client_id = int(session["client_id"])
    session_state = session_states[client_id]

    user_input = request.form["user_input"]
    if session_state.question is None:
        session_state.question = user_input
        session_state.socrates.set_question(session_state.question)
        session_state.theaetetus.set_question(session_state.question)
        session_state.plato.set_question(session_state.question)
        response = generate_response(user_input, mode="question")

    elif session_state.wait_tony:
        feedback = user_input
        session_state.socrates.add_feedback(
            session_state.all_questions_to_tony, feedback
        )
        session_state.theaetetus.add_feedback(
            session_state.all_questions_to_tony, feedback
        )
        session_state.plato.add_feedback(session_state.all_questions_to_tony, feedback)
        session_state.all_questions_to_tony = ""
        session_state.wait_tony = False
        response = generate_response(user_input, mode="feedback")
    else:
        return jsonify([])
    return jsonify([{"role": "system", "response": response}])


def generate_response(user_input, mode="question"):
    if mode == "question":
        return f"You just said: {user_input}\n\nA conversation among (Socrates, Theaetetus, and Plato) will begin shortly..."
    elif mode == "feedback":
        return f"Received your feedback: {user_input}"
    return "Connecting..."


if __name__ == "__main__":
    app.run(debug=True)
