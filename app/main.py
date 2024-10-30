import streamlit as st
from PIL import Image
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="Mailer.Ai", page_icon="📧")

    st.sidebar.title("Settings")
    theme_mode = st.sidebar.radio("Select Theme:", ["Light", "Dark"])
    temperature = st.sidebar.slider("LLM Creativity (Temperature)", 0.0, 1.0, 0.5)

    if theme_mode == "Dark":
        apply_dark_mode()
    else:
        apply_light_mode()

    image_path = "app/resource/gmail.png"
    image = Image.open(image_path)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("📧 Mailer.Ai")
        st.subheader("Generate personalized emails from job descriptions")

        with st.form("url_form"):
            url_input = st.text_input("Enter a Job Description URL:",
                                      help="Paste a job description or company page URL here.")
            submit_button = st.form_submit_button("Submit")

        if submit_button:
            with st.spinner('Extracting job details...'):
                try:
                    loader = WebBaseLoader([url_input])
                    data = loader.load().pop().page_content

                    cleaned_data = clean_text(data)
                    portfolio.load_portfolio()
                    jobs = llm.extract_jobs(cleaned_data)

                    if not jobs:
                        st.warning("No jobs were extracted from the provided URL.")
                    else:
                        job_titles = [job.get('title', 'Unknown Title') for job in jobs]
                        selected_job = st.selectbox("Select a Job to Generate Email For:", job_titles)

                        for job in jobs:
                            if job.get('title', 'Unknown Title') == selected_job:
                                skills = job.get('skills', [])
                                links = portfolio.query_links(skills)

                                st.markdown(f"""
                                <div style="background-color: #f9f9f9; padding: 20px; margin: 10px; border-radius: 10px;">
                                    <h3>Job Title: {job.get('title', 'Unknown Job')}</h3>
                                    <p><b>Required Skills:</b> {', '.join(skills)}</p>
                                </div>
                                """, unsafe_allow_html=True)

                                email = llm.write_mail(job, links)
                                if email is None:
                                    email = ""


                except Exception as e:
                    st.error(f"An error occurred: {e}")

    with col2:
        st.image(image, use_column_width=False, width=50)

    tab1, tab2, tab3 = st.tabs(["Job Details", "Generated Email", "History"])
    with tab1:
        st.write("Display extracted job details here.")
    with tab2:
        st.write("Display the generated email here.")
    with tab3:
        st.write("Display previously generated emails here.")

    st.sidebar.markdown("### 🎵 Add Background Music")
    st.sidebar.markdown('<i class="fa fa-music" style="font-size:24px;color:green;"></i>', unsafe_allow_html=True)

    music_file = st.sidebar.file_uploader("Choose a music file", type=['mp3', 'wav'])
    if music_file:
        st.sidebar.audio(music_file, format='audio/mp3')


def apply_light_mode():
    st.markdown("""
    <style>
    body {
        background-color: #FAFAFA;
        color: #000000;
    }
    .stButton>button, .stTextInput>div>input {
        background-color: #FFFFFF;
        color: black;
        border-radius: 5px;
        border: 1px solid #E0E0E0;
    }
    .stExpander, .stSlider {
        background-color: #f0f0f5;
        color: #000000;
    }
    .stMarkdown, .stCode {
        background-color: #f9f9f9;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_dark_mode():
    st.markdown("""
    <style>
    body {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    .stButton>button, .stTextInput>div>input {
        background-color: #333333;
        color: white;
        border-radius: 5px;
        border: 1px solid #444444;
    }
    .stExpander, .stSlider {
        background-color: #444444;
        color: #FFFFFF;
    }
    .stMarkdown, .stCode {
        background-color: #333333;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()

    create_streamlit_app(chain, portfolio, clean_text)

















