import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv


# ----------------------
# Load Environment Variables
# ----------------------
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
openai.api_key = os.getenv("OPENAI_API_KEY")

WEBSITE_URL = os.getenv("WEBSITE_URL")

# ----------------------
# Functions and Rest of the Script
# ----------------------

PDF_PATH = "./aibytec data2.pdf"

# Function to send email
def send_email(name, email, contact_no, area_of_interest):
    subject = "New User Profile Submission"
    body = f"""
    New Student Profile Submitted:

    Name: {name}
    Email: {email}
    Contact No.: {contact_no}
    Area of Interest: {area_of_interest}
    """
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to extract PDF text
def extract_pdf_text(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"Error scraping website: {e}"

# Function to generate OpenAI response
def chat_with_ai(user_question, website_text, pdf_text, chat_history):
    combined_context = f"Website Content:\n{website_text}\n\nPDF Content:\n{pdf_text}"
    messages = [{"role": "system", "content": "You are a helpful assistant. Use the provided content."}]
    for entry in chat_history:
        messages.append({"role": "user", "content": entry['user']})
        messages.append({"role": "assistant", "content": entry['bot']})
    messages.append({"role": "user", "content": f"{combined_context}\n\nQuestion: {user_question}"})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=False
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating response: {e}"

# ----------------------
# Streamlit UI and App Logic
# ----------------------

st.set_page_config(page_title="Student Profile & AI Chatbot", layout="wide")

# Session State Initialization
if "page" not in st.session_state:
    st.session_state['page'] = 'form'
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []

st.session_state['chat_history'].append({"user": "Connect me to the real person or Support team", "bot": "To reach out to the administrator of Aibytec for specific inquiries, you can submit your message through the "Contact" form on their website. Here is the link to access the contact page directly: https://api.whatsapp.com/send/?phone=923312154519&text=Hey%21+I+need+help..&type=phone_number&app_absent=0 "})
# ----------------------
# PAGE 1: User Info Form
# ----------------------
if st.session_state['page'] == 'form':
    st.markdown('<p style="font-size: 21px;"><b>Hi! Welcome to AIByTec</b></p>', unsafe_allow_html=True)
    
    with st.form(key="user_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        contact_no = st.text_input("Contact No.")
        area_of_interest = st.text_input("Area of Interest")

        # Add custom CSS for alignment
        st.markdown("""
            <style>
            .button-container {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .custom-button {
                padding: 10px 20px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # # Use HTML to wrap buttons in the container
        # st.markdown("""
        #     <div class="button-container">
        #         <button class="custom-button">Submit</button>
        #         <button class="custom-button" style="margin-left: 10px;">Cancel</button>
        #     </div>
        # """, unsafe_allow_html=True)

        with st.container():
            # Create three columns for alignment
            col1, col2, col3 = st.columns([1, 1, 1])  # Adjust proportions as needed
            
            # Place the button in the desired column
            with col1:
                submitted = st.form_submit_button("Proceed to Chat ")
            
            with col2:
                continue_chat = st.form_submit_button(" Skip and Join Chat")
            
            with col3:
                st.write("")  # Empty to balance alignment
                    
        if submitted:
            if name and email and contact_no and area_of_interest:
                send_email(name, email, contact_no, area_of_interest)
                st.session_state['page'] = 'chat'
                st.rerun()
            else:
                st.warning("Please fill out all fields.")
        
        # If user clicks "Continue Chat with AIByTec"
        if continue_chat:
            st.session_state['page'] = 'chat'
            st.rerun()

# ----------------------
# PAGE 2: Chatbot Interface
# ----------------------
elif st.session_state['page'] == 'chat':
    # Display chat history without headings
    for entry in st.session_state['chat_history']:
        # User Message
        st.markdown(
            f"""
            <div style="
                background-color: #78bae4; 
                padding: 10px; 
                border-radius: 10px; 
                margin-bottom: 10px;
                width: fit-content;
                max-width: 80%;
            ">
                {entry['user']}
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Assistant Message
        st.markdown(
            f"""
            <div style="
                background-color:  #D3D3D3; 
                padding: 10px; 
                border-radius: 10px; 
                margin-bottom: 10px;
                margin-left: auto;
                width: fit-content;
                max-width: 80%;
            ">
                {entry['bot']}
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Load PDF and Website content once
    pdf_text = extract_pdf_text(PDF_PATH) if os.path.exists(PDF_PATH) else "PDF file not found."
    website_text = scrape_website(WEBSITE_URL)

    # Fixed input bar at bottom
    user_input = st.chat_input("Type your question here...", key="user_input_fixed")

    if user_input:
        # Display bot's response
        with st.spinner("Generating response..."):
            bot_response = chat_with_ai(user_input, website_text, pdf_text, st.session_state['chat_history'])
        
        # Append user query and bot response to chat history
        st.session_state['chat_history'].append({"user": user_input, "bot": bot_response})
        
        # Re-run to display updated chat history
        st.rerun()
