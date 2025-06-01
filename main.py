from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
import io
from datetime import datetime

current_year = datetime.now().year

# Load API key from environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("🚨 GOOGLE_API_KEY environment variable not set. Please set it in your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

# Function to extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        try:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            pdf_file = io.BytesIO(bytes_data)
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() or "" # Add "or """ to handle None from extract_text
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None
    return None

# Function to generate response from Gemini AI model
def generate_sop_with_gemini(prompt_details):
    model = genai.GenerativeModel('gemini-1.5-flash-latest') # Using a capable model
    try:
        response = model.generate_content(prompt_details)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while generating the SOP: {e}")
        st.error("This might be due to API key issues, content policy violations, or network problems.")
        st.error("Please check your API key and the content you provided. You can also try again later.")
        return None


# Streamlit App
st.set_page_config(page_title="SOP/Motivation Letter Generator", page_icon="📝", layout="wide")

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;} /* Hide default Streamlit footer */

  .stTextArea textarea {font-size: 1rem !important;}

  .sidebar-container {
    background-color: #f0f2f6; /* Light grey background */
    padding: 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
  }
  .sidebar-title {
    font-family: 'Arial', sans-serif;
    color: #1E88E5; /* Blue title */
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
  }
  .sidebar-text {
    font-family: 'Arial', sans-serif;
    color: #333333;
    font-size: 16px;
    margin-bottom: 15px;
  }

  .custom-footer {
    background-color: #1E88E5; /* Blue footer */
    color: #ffffff;
    padding: 10px 0;
    width: 100%;
    text-align: center;
    font-family: 'Arial', sans-serif;
    font-size: 14px;
    position: fixed;
    bottom: 0;
    left: 0;
    z-index: 999;
  }
  .main-content {
    padding-bottom: 70px; /* Footer height + some margin */
  }
</style>
""", unsafe_allow_html=True)

# --- Sidebar for Inputs ---
with st.sidebar.container():
    st.markdown('<div class="sidebar-title">Your Application Details</div>', unsafe_allow_html=True)

    target_program = st.text_input("🎯 Target Program (e.g., M.Sc. in Data Science)", key="program")
    target_university = st.text_input("🏛️ Target University (e.g., University of California, Berkeley)", key="university")

    st.markdown("---")
    st.markdown('<p class="sidebar-text">Tell us about yourself:</p>', unsafe_allow_html=True)

    academic_interests = st.text_area("📚 Subjects / Areas of Academic Interest (comma-separated or detailed)", height=100, key="interests",
                                      help="E.g., Machine Learning, AI Ethics, Natural Language Processing, Quantum Computing")
    job_experience = st.text_area("💼 Relevant Job/Internship Experience (describe roles, achievements)", height=150, key="experience",
                                  help="Include company, role, duration, and key responsibilities or projects.")

    has_publications = st.radio("📄 Do you have paper publications?", ("No", "Yes"), key="pub_radio")
    publications_details = ""
    if has_publications == "Yes":
        publications_details = st.text_area("Details of Publications (titles, journals, links if any)", height=100, key="pub_details")

    key_skills = st.text_area("💪 Key Skills & Strengths (technical and soft)", height=100, key="skills",
                              help="E.g., Python, R, Critical Thinking, Teamwork, Problem Solving")
    future_goals = st.text_area("🚀 Future Goals / Career Aspirations (short-term and long-term)", height=100, key="goals",
                                help="What do you hope to achieve after completing this program?")
    why_program_uni = st.text_area("❓ Why this specific program and university? (optional, but helpful)", height=100, key="why_this",
                                   help="Mention specific faculty, research labs, courses, or university culture that attracts you.")

    st.markdown("---")
    uploaded_cv = st.file_uploader("📄 Upload your CV (Optional, PDF only)", type=["pdf"], key="cv")

    st.markdown("---")
    generate_button = st.button("✨ Generate SOP/Motivation Letter", use_container_width=True, type="primary")


# --- Main Content Area ---
st.title("🤖 AI-Powered SOP/Motivation Letter Generator")
st.markdown("<div class='main-content'>", unsafe_allow_html=True) # For footer spacing

if 'generated_sop' not in st.session_state:
    st.session_state.generated_sop = ""

if generate_button:
    # Validation
    if not target_program or not target_university:
        st.error("🚨 Please provide the Target Program and Target University.")
    elif not academic_interests and not job_experience and not uploaded_cv:
        st.warning("⚠️ Please provide at least some information about your interests, experience, or upload a CV for better results.")
    else:
        with st.spinner("🧠 Crafting your letter... This might take a moment..."):
            cv_text = ""
            if uploaded_cv:
                cv_text = extract_text_from_pdf(uploaded_cv)
                if cv_text is None: # Error occurred during PDF extraction
                    st.error("Could not process the uploaded CV. Please try another file or proceed without it.")
                    cv_text = "" # Reset to empty string

            # Constructing the detailed prompt for Gemini
            prompt_lines = [
                "You are an expert academic advisor specializing in crafting compelling, personalized, and well-structured Statements of Purpose (SOPs) or Motivation Letters for students applying for higher studies abroad.",
                "Your task is to generate an SOP based on the following information provided by the candidate.",
                "The tone should be professional, enthusiastic, confident, yet humble and genuine.",
                "Your tone should be formal and academic,indian types accent and make it like human written that no one can detect it .",
                "The letter should flow logically, avoid clichés, and be highly specific to the candidate's profile and the target program/university.",
                "Structure the SOP with clear paragraphs: Introduction, Academic Background/Interests, Professional Experience (if any), Research/Publications (if any), Why this Specific Program and University, Future Goals, and Conclusion.",
                "\n--- CANDIDATE'S INFORMATION ---"
            ]
            prompt_lines.append(f"Target Program: {target_program}")
            prompt_lines.append(f"Target University: {target_university}")
            if academic_interests:
                prompt_lines.append(f"Academic Interests/Subjects: {academic_interests}")
            if job_experience:
                prompt_lines.append(f"Job/Internship Experience: {job_experience}")
            if has_publications == "Yes" and publications_details:
                prompt_lines.append(f"Paper Publications: {publications_details}")
            else:
                 prompt_lines.append(f"Paper Publications: None mentioned.")
            if key_skills:
                prompt_lines.append(f"Key Skills & Strengths: {key_skills}")
            if future_goals:
                prompt_lines.append(f"Future Goals/Career Aspirations: {future_goals}")
            if why_program_uni:
                prompt_lines.append(f"Specific reasons for choosing this program/university: {why_program_uni}")

            if cv_text:
                prompt_lines.append("\n--- ADDITIONAL CONTEXT FROM CV ---")
                prompt_lines.append(cv_text[:3000]) # Limit CV text to avoid overly long prompts
                prompt_lines.append("--- END OF CV CONTEXT ---")

            prompt_lines.extend([
                "\n--- INSTRUCTIONS FOR GENERATION ---",
                "1. Introduction: Start with a strong hook. Clearly state the purpose: applying for the specific program at the specific university. Briefly convey passion for the field.",
                "2. Academic Background: Elaborate on academic interests. Mention relevant coursework, projects, or academic achievements that demonstrate aptitude and passion. Connect these to the target program.",
                "3. Professional Experience: Discuss relevant job roles, responsibilities, skills gained (technical and soft), and significant achievements. Quantify achievements where possible. Show how this experience prepares them for the program and aligns with future goals.",
                "4. Research/Publications: If applicable, detail research involvement, methodologies, findings, and any publications. Explain their significance and relevance to the target program.",
                "5. Why this Program & University: This is crucial. Explain specific reasons for choosing THIS program at THIS university. Mention specific courses, faculty members whose research aligns with their interests, research labs, unique program features, or university culture/values. Show genuine interest and research.",
                "6. Future Goals: Clearly articulate short-term (immediately after a Master's/PhD) and long-term career aspirations. Explain how this specific program is essential for achieving these goals.",
                "7. Conclusion: Summarize key strengths and suitability. Reiterate enthusiasm for the opportunity. End with a polite and confident closing.",
                "VERY IMPORTANT: Ensure the letter is approximately 800-1200 words. Maintain a formal and academic tone throughout. Personalize heavily based on the provided details. Avoid generic statements.",
                "Do NOT use placeholders like '[Candidate's Name]' or '[University Name]' unless explicitly provided in the candidate's information as such. Use the provided program and university names directly.",
                "Output ONLY the Statement of Purpose/Motivation Letter text. Do not include any preamble or your own comments before or after the letter itself."
            ])

            final_prompt = "\n".join(prompt_lines)

            # For debugging the prompt:
            # st.subheader("Debug: Generated Prompt")
            # st.text_area("Prompt sent to AI:", final_prompt, height=300)

            generated_text = generate_sop_with_gemini(final_prompt)

            if generated_text:
                st.session_state.generated_sop = generated_text
                st.success("✅ SOP/Motivation Letter Generated Successfully!")
            else:
                st.session_state.generated_sop = "Failed to generate SOP. Please check errors above and try again."


if st.session_state.generated_sop:
    st.subheader("✍️ Generated SOP/Motivation Letter:")
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; background-color: #000; color: #fff;">
    {st.session_state.generated_sop.replace("\n", "<br>")}
    </div>
    """, unsafe_allow_html=True)
    st.download_button(
        label="📥 Download SOP as Text File",
        data=st.session_state.generated_sop,
        file_name=f"SOP_{target_program.replace(' ', '_')[:20]}.txt" if target_program else "SOP_Generated.txt",
        mime="text/plain"
    )
    st.info("ℹ️ Please review and edit this draft carefully. Personalize it further to truly reflect your voice and experiences.")

st.markdown("</div>", unsafe_allow_html=True) # Close main-content div

# Custom Footer
st.markdown(f"""
<div class="custom-footer">
  <p>© {current_year} AI SOP Generator. | Created by SHARUPYA BARUA </p>

</div>
""", unsafe_allow_html=True)
