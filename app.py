from flask import Flask, render_template, request, send_file
from openai import OpenAI
import os
from fpdf import FPDF
import io

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Modern CV class
class ModernCVPDF(FPDF):
    def header(self):
        # Top banner
        self.set_fill_color(0, 102, 204)  # Blue
        self.rect(0, 0, 210, 20, 'F')

    def name_header(self, name, job_title):
        self.set_y(5)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 18)
        self.cell(0, 10, name, ln=True, align="C")
        self.set_font("Arial", "I", 12)
        self.cell(0, 10, job_title, ln=True, align="C")
        self.ln(10)
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, title, ln=True)
        self.ln(2)

    def section_body(self, body):
        self.set_font("Arial", "", 12)
        for line in body.split("\n"):
            self.multi_cell(0, 7, line)
        self.ln(4)

    def skills_column(self, skills_list):
        self.set_font("Arial", "", 12)
        col_width = 90
        x_start = self.get_x()
        y_start = self.get_y()
        for i, skill in enumerate(skills_list):
            x = x_start + (i % 2) * col_width
            y = y_start + (i // 2) * 7
            self.set_xy(x, y)
            self.cell(col_width, 7, f"• {skill}")
        self.ln((len(skills_list)+1)//2 * 7 + 4)

# Home page
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
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
        - CV text with section titles (Education, Skills, Experience, Cover Letter)
        - Job search advice in Rwanda context
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

    return render_template("index.html", result=result)

# PDF download
@app.route("/download", methods=["POST"])
def download_pdf():
    content = request.form.get("pdf_content")
    pdf = ModernCVPDF()
    pdf.add_page()

    # Extract first two lines as name + job title
    lines = content.split("\n")
    if len(lines) >= 2:
        pdf.name_header(lines[0], lines[1])
        content_body = "\n".join(lines[2:])
    else:
        content_body = content

    # Split content into sections
    sections = content_body.split("\n\n")
    for sec in sections:
        sec_lines = sec.strip().split("\n")
        if len(sec_lines) == 0:
            continue
        title = sec_lines[0]
        body = "\n".join(sec_lines[1:]) if len(sec_lines) > 1 else ""
        if title.lower() == "skills":
            skills_list = [s.strip() for s in body.replace("-", ",").split(",")]
            pdf.section_title(title)
            pdf.skills_column(skills_list)
        else:
            pdf.section_title(title)
            pdf.section_body(body)

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
