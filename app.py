from flask import Flask, render_template, request, send_file
from openai import OpenAI
import os
from fpdf import FPDF
import io

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    pdf_file = None

    if request.method == "POST":
        name = request.form.get("name")
        education = request.form.get("education")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        job = request.form.get("job")

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

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", '', 12)
        for line in result.split("\n"):
            pdf.multi_cell(0, 8, line)
        # Save PDF to in-memory buffer
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        # Save buffer in session-like variable (simplest for demo)
        pdf_file = pdf_buffer

        # Save temporary file path if you prefer file download
        # pdf.output("cv.pdf")

    return render_template("index.html", result=result, pdf_file=pdf_file)

@app.route("/download", methods=["POST"])
def download_pdf():
    content = request.form.get("pdf_content")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", '', 12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 8, line)
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="CV.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
