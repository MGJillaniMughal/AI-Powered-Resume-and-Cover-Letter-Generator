import streamlit as st
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain.llms import OpenAI
from fpdf import FPDF
import io

# Load environment variables
load_dotenv()

# Initialize OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set it in your environment variables.")
openai_llm = OpenAI(model="gpt-3.5-turbo",openai_api_key=OPENAI_API_KEY)

# Streamlit app setup
st.set_page_config(page_title="AI-Powered Resume and Cover Letter Generator", layout="wide")
st.markdown("""
# 📝 AI-Powered Cover Letter and Resume Generator
Developed My Jillani SoftTech 😎            
Generate a professional cover letter or resume with AI assistance.
""")

# Create a custom PDF class that includes the DejaVu font
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Add Unicode font (DejaVu)
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.set_font('DejaVu', '', 12)

# Function to create a PDF document
def create_pdf(text, title):
    pdf = PDF()
    pdf.add_page()
    pdf.multi_cell(0, 10, text)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)
    return pdf_output


# Function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        return "".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Function to generate cover letter
def generate_cover_letter(prompt, temperature=0.99):
    try:
        response = openai_llm(prompt, temperature=temperature, max_tokens=1024)
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to generate resume
def generate_resume(prompt):
    try:
        resume_response = openai_llm(prompt, temperature=0.99, max_tokens=1024)
        return resume_response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Collect inputs for cover letter
def collect_cover_letter_inputs():
    with st.form('input_form'):
        res_format = st.radio("Do you want to upload or paste your resume?", ('Upload', 'Paste'))
        res_text = ""
        if res_format == 'Upload':
            res_file = st.file_uploader('📁 Upload your resume in pdf format')
            if res_file:
                res_text = extract_text_from_pdf(res_file)
        else:
            res_text = st.text_area('Pasted resume elements')

        job_desc = st.text_input('Pasted job description')
        user_name = st.text_input('Your name')
        company = st.text_input('Company name')
        manager = st.text_input('Hiring manager')
        role = st.text_input('Job title/role')
        referral = st.text_input('How did you find out about this opportunity?')
        ai_temp = st.slider('AI Temperature (0.0-1.0)', min_value=0.0, max_value=1.0, value=0.99)

        submitted = st.form_submit_button("Generate Cover Letter")

        if submitted and res_text:
            prompt = f"""
            You will need to generate a cover letter based on specific resume and a job description.
            My resume text: {res_text}
            The job description is: {job_desc}
            The candidate's name to include on the cover letter: {user_name}
            The job title/role: {role}
            The hiring manager is: {manager}
            How you heard about the opportunity: {referral}
            The company to which you are generating the cover letter for: {company}
            The cover letter should have three content paragraphs.
            In the first paragraph, focus on who you are, what position you are interested in, where you heard about it, and summarize what you have to offer.
            In the second paragraph, focus on why the candidate is a great fit, drawing parallels between the resume experience and the job description qualifications.
            In the third paragraph, restate your interest in the organization and/or job, summarize what you have to offer, and thank the reader.
            Use {user_name} as the candidate.
            Generate a specific cover letter based on the above.
            """
            return {'submitted': True, 'prompt': prompt, 'ai_temp': ai_temp}
        else:
            return {'submitted': False}

# Collect inputs for resume
def collect_resume_inputs():
    with st.form('resume_form'):
        # Personal Information
        st.subheader("Personal Information")
        name = st.text_input('Your Name', placeholder="John Doe")
        email = st.text_input('Email Address', placeholder="john.doe@example.com")
        phone = st.text_input('Phone Number', placeholder="+1234567890")
        linkedin = st.text_input('LinkedIn Profile URL', placeholder="https://linkedin.com/in/johndoe")
        portfolio = st.text_input('Portfolio URL (if applicable)', placeholder="https://yourportfolio.com")

        # Professional Summary
        st.subheader("Professional Summary")
        summary = st.text_area('A brief overview of your professional background and career goals')

        # Work Experience
        st.subheader("Work Experience")
        experience = st.text_area('Detail your professional experience, starting with the most recent position')

        # Education
        st.subheader("Education")
        education = st.text_area('List your academic qualifications, starting with the most recent')

        # Skills
        st.subheader("Skills")
        skills = st.text_area('List your professional skills')

        # Certifications and Awards
        st.subheader("Certifications and Awards")
        certifications = st.text_area('Include any relevant certifications or awards')

        # Additional Sections
        st.subheader("Additional Information")
        languages = st.text_area('Languages (Indicate proficiency level)')
        interests = st.text_area('Interests/Hobbies (Optional)')
        
        # Submit Button
        resume_submitted = st.form_submit_button("Generate Resume")

        if resume_submitted:
            resume_prompt = f"""
            Create a detailed professional resume for {name} with the following information:
            1. Personal Information:
               - Name: {name}
               - Email: {email}
               - Phone: {phone}
               - LinkedIn: {linkedin}
               - Portfolio: {portfolio}
            2. Professional Summary:
               {summary}
            3. Work Experience:
               {experience}
            4. Education:
               {education}
            5. Skills:
               {skills}
            6. Certifications and Awards:
               {certifications}
            7. Languages:
               {languages}
            8. Interests/Hobbies:
               {interests}
            """
            return {'submitted': True, 'prompt': resume_prompt}
        else:
            return {'submitted': False}

# def create_pdf(text, title):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(0, 10, text)
#     pdf_output = io.BytesIO()
#     pdf.output(pdf_output, 'F')
#     pdf_output.seek(0)
#     return pdf_output

# Updated function to display and provide download options for the generated text
def display_and_download(text, file_label):
    st.write(text)

    # Download as Text File
    st.download_button(f'Download {file_label} as TXT', text, file_name=f"{file_label}.txt")

    # Download as PDF
    pdf = create_pdf(text, file_label)
    st.download_button(f'Download {file_label} as PDF', pdf, file_name=f"{file_label}.pdf", mime="application/pdf")

# Main app logic
def main():
    tab1, tab2 = st.tabs(["Cover Letter Generator", "Resume Generator"])

    with tab1:
        st.markdown("### Generate Your Cover Letter")
        user_input = collect_cover_letter_inputs()
        if user_input['submitted']:
            cover_letter = generate_cover_letter(user_input['prompt'], user_input['ai_temp'])
            if cover_letter:
                display_and_download(cover_letter, "Cover Letter")

    with tab2:
        st.markdown("### Generate Your Resume")
        user_input = collect_resume_inputs()
        if user_input['submitted']:
            resume = generate_resume(user_input['prompt'])
            if resume:
                display_and_download(resume, "Resume")

if __name__ == "__main__":
    main()
