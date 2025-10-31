from flask import Flask, render_template, request
from openai import OpenAI
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        # Get form inputs
        name = request.form.get("name")
        education = request.form.get("education")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        job = request.form.get("job")

        # Build prompt for AI
        prompt = f"""
        Create a professional CV for a Rwandan job seeker:

        Name: {name}
        Education: {education}
        Skills: {skills}
        Experience: {experience}
        Job Target: {job}

        Output:
        - CV text
        - Cover letter
        - Job search advice in Rwanda context
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract result
        result = response.choices[0].message.content

    return render_template("index.html", result=result)

if __name__ == "__main__":
    # Render requires host 0.0.0.0 and port 10000
    app.run(host="0.0.0.0", port=10000)
