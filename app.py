from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
import uuid
import os
import openai

app = Flask(__name__)

# Simple local SQLite DB for demo
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///conversations.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Secret key for sessions
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

db = SQLAlchemy(app)

# Set your OpenAI API key in the environment before running
openai.api_key = os.environ.get("OPENAI_API_KEY")


class Conversation(db.Model):
    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=True)

    # Character profile fields
    name = db.Column(db.String(255), nullable=True)
    job = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    family_status = db.Column(db.String(255), nullable=True)
    relationship = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    sex = db.Column(db.String(255), nullable=True)
    introvert_extrovert = db.Column(db.String(255), nullable=True)
    tech_averse = db.Column(db.String(255), nullable=True)
    self_centered = db.Column(db.String(255), nullable=True)
    loyal = db.Column(db.String(255), nullable=True)
    skeptic_trustful = db.Column(db.String(255), nullable=True)
    add_char = db.Column(db.Text, nullable=True)


@app.before_first_request
def create_tables():
    db.create_all()


def log_conversation(
    session_id,
    user_message,
    ai_response,
    name=None,
    job=None,
    age=None,
    location=None,
    family_status=None,
    relationship=None,
    description=None,
    sex=None,
    introvert_extrovert=None,
    tech_averse=None,
    self_centered=None,
    loyal=None,
    skeptic_trustful=None,
    add_char=None,
):
    convo = Conversation(
        session_id=session_id,
        user_message=user_message,
        ai_response=ai_response,
        name=name,
        job=job,
        age=age,
        location=location,
        family_status=family_status,
        relationship=relationship,
        description=description,
        sex=sex,
        introvert_extrovert=introvert_extrovert,
        tech_averse=tech_averse,
        self_centered=self_centered,
        loyal=loyal,
        skeptic_trustful=skeptic_trustful,
        add_char=add_char,
    )
    db.session.add(convo)
    db.session.commit()


def load_conversation_history(session_id):
    history = Conversation.query.filter_by(session_id=session_id).all()
    messages = []
    for convo in history:
        # Store previous turns so the model keeps character context
        messages.append({"role": "user", "content": convo.user_message})
        if convo.ai_response:
            messages.append({"role": "assistant", "content": convo.ai_response})
    return messages


@app.before_request
def make_session_permanent():
    session.permanent = True
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())


@app.route("/")
def index():
    # You can also directly render custom_chat.html here if you want
    return render_template("custom_chat.html")


@app.route("/custom_chat")
def custom_chat():
    return render_template("custom_chat.html")


@app.route("/generate_conversation", methods=["POST"])
def generate_conversation():
    session_id = session["session_id"]

    data = request.json or {}

    # Character profile from the form
    name = data.get("name")
    job = data.get("job")
    age = data.get("age")
    location = data.get("location")
    familyStatus = data.get("familyStatus")
    relationship = data.get("relationship")
    description = data.get("description")
    sex = data.get("sex")
    introvertExtrovert = data.get("introvertExtrovert")
    techAverse = data.get("techAverse")
    selfCentered = data.get("selfCentered")
    loyal = data.get("loyal")
    skepticTrustful = data.get("skepticTrustful")
    add_char = data.get("addtionalChracteristics", "")
    userInput = data.get("userInput", "")

    if not userInput:
        return jsonify({"error": "No user input provided"}), 400

    # Build character prompt
    system_prompt = f"""
    You are a fictional character in a story.
    Your name is {name} and your age is {age}.
    Your job is {job}, your sex is {sex}, and you live in {location}.
    Your family status is {familyStatus} and your relationship status is {relationship}.

    Here is more description about you:
    {description}

    Personality sliders (0 to 100):
    Extrovert level: {introvertExtrovert} (0 means extremely introvert, 100 means extremely extrovert).
    Nerdy level: {techAverse} (0 means very tech averse, 100 means very tech savvy).
    Loyal level: {loyal} (0 means very fickle, 100 means extremely loyal).
    Self centered level: {selfCentered} (0 means very empathetic, 100 means very self centered).
    Trustful level: {skepticTrustful} (0 means very skeptical, 100 means very trusting).

    Additional characteristics:
    {add_char}

    You are having a natural conversation with the user as this character.
    Stay consistent with the traits above. If the user asks something outside your knowledge,
    you can make reasonable details up as long as they do not conflict with this profile.
    """

    # Load previous turns for this session
    history_messages = load_conversation_history(session_id)

    messages = [{"role": "system", "content": system_prompt}] + history_messages + [
        {"role": "user", "content": userInput}
    ]

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Log this turn
    log_conversation(
        session_id=session_id,
        user_message=userInput,
        ai_response=ai_response,
        name=name,
        job=job,
        age=age,
        location=location,
        family_status=familyStatus,
        relationship=relationship,
        description=description,
        sex=sex,
        introvert_extrovert=introvertExtrovert,
        tech_averse=techAverse,
        self_centered=selfCentered,
        loyal=loyal,
        skeptic_trustful=skepticTrustful,
        add_char=add_char,
    )

    return jsonify({"conversation": ai_response})


if __name__ == "__main__":
    app.run(debug=True)
