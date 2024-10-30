import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from io import BytesIO
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


def create_pdf(email_content):
    if email_content is None:
        email_content = ""

    buffer = BytesIO()

    # Create the PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create a custom style for bullet points
    bullet_style = ParagraphStyle('BulletStyle', parent=styles['Normal'], bulletIndent=20)

    # Splitting the email content into paragraphs
    email_paragraphs = []
    for paragraph in email_content.split('\n\n'):
        if paragraph.startswith("*"):
            # Handle lists by splitting each item and creating a ListFlowable
            items = paragraph.split("*")[1:]  # Split and remove first empty element
            list_items = [ListItem(Paragraph(f"* {item.strip()}", bullet_style)) for item in items]
            email_paragraphs.append(ListFlowable(list_items, bulletType='bullet', bulletFontSize=10))
        else:
            # Add paragraph for non-list items
            email_paragraphs.append(Paragraph(paragraph.strip(), styles['Normal']))

        email_paragraphs.append(Spacer(1, 12))  # Add spacing between paragraphs or list items

    # Build the PDF
    pdf.build(email_paragraphs)

    buffer.seek(0)
    return buffer

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Bhavesh, a business development executive at Alpha.ai. Alpha.ai is an AI & Software Consulting company 
            dedicated to facilitating the seamless integration of business processes through automated tools. Over our 
            experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, process 
            optimization, cost reduction, and heightened overall efficiency. 

            Your job is to write a cold email to the client regarding the job mentioned above describing the capability 
            of Alpha.ai in fulfilling their needs of 500-600 words. Also, add the most relevant ones from the following links to showcase 
            Alpha.ai's portfolio: {link_list}

            Remember you are Bhavesh,BDE,Alpha.ai.
            Do not provide a preamble.

            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        st.text_area("Generated Email", value=res.content, height=300)

        pdf_buffer = create_pdf(res.content)
        st.download_button(
            label="Download Email as PDF",
            data=pdf_buffer,
            file_name="generated_email.pdf",
            mime="application/pdf"
        )

        st.download_button(
            label="Download Email as Markdown",
            data=res.content,
            file_name="generated_email.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))



