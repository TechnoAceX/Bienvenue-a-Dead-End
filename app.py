from flask import Flask, redirect, render_template, request, session
from ai_response import ai_response, generate_image
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_secret")


@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        session.clear()

        session["name"] = request.form["name"]
        session["genre"] = request.form["genre"]
        session["plot"] = request.form["plot_description"]
        session["target_audience"] = request.form.get("target_audience", "General")
        session["story_length"] = request.form.get("story_length", "short")
        session["writing_style"] = request.form.get("writing_style", "descriptive")
        session["story"] = []
        session["prev_story"] = []
        return redirect("/response")

    return render_template('form.html')


@app.route("/response", methods=["GET", "POST"])
def response_route():
    title, paragraph, choice1, choice2 = ai_response(
        name=session.get("name"),
        genre=session.get("genre"),
        plot=session.get("plot"),
        target_audience=session.get("target_audience"),
        writing_style=session.get("writing_style"),
        prev_story=session.get("prev_story"),
        choice=session.get("choice")
    )

    image_url = generate_image(title)

    session["title"] = title
    session["choice1"] = choice1
    session["choice2"] = choice2

    story = session.get("story", [])
    prev_story = session.get("prev_story", [])

    story.append([title, paragraph, choice1, choice2, image_url])
    prev_story.append(paragraph)

    session["story"] = story
    session["prev_story"] = prev_story

    return redirect("/index")


@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template('index.html', story=session.get("story", []))


@app.route("/choice1", methods=["GET", "POST"])
def choice_one():
    session["choice"] = session.get("choice1")
    return redirect("/response")


@app.route("/choice2", methods=["GET", "POST"])
def choice_two():
    session["choice"] = session.get("choice2")
    return redirect("/response")


@app.route("/undo", methods=["GET", "POST"])
def undo():
    story = session.get("story", [])
    prev_story = session.get("prev_story", [])

    if story:
        story.pop()
    if prev_story:
        prev_story.pop()

    session["story"] = story
    session["prev_story"] = prev_story

    return redirect("/index")


if __name__ == "__main__":
    app.run(debug=True)
