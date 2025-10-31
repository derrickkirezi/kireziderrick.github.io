from flask import Flask, render_template, request
import openai
import os
app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        education = request.form["education"]
        skills = request.form["skills"]
        experience = request.form["experience"]
        job = request.form["job"]

        prompt = f"""
        Create a professional CV for a Rwandan job seeker:

        Name: {name}
        Education: {education}
        Skills: {skills}
        Experience: {experience}
        Job Target: {job}

        Also write:
        - A cover letter in Rwandan context
        - Advice for applying to jobs in Rwanda
        """

        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response["choices"][0]["message"]["content"]

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

