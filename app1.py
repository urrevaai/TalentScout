import streamlit as st
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import os
from dataclasses import dataclass, asdict
import uuid

# Configure page
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Global text color improvements - WHITE TEXT */
    .stMarkdown, .stText, .stTextInput, .stSelectbox, .stTextArea {
        color: #ffffff !important;
    }
    
    /* Main content area */
    .main .block-container {
        color: #ffffff !important;
        background-color: #1e1e1e !important;
    }
    
    .main-header {
        text-align: center;
        color: #ffffff !important;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .sub-header {
        text-align: center;
        color: #ffffff !important;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #ffffff !important;
    }
    .user-message {
        background-color: #2c3e50 !important;
        border-left: 4px solid #3498db !important;
        color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .assistant-message {
        background-color: #27ae60 !important;
        border-left: 4px solid #2ecc71 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .candidate-info {
        background-color: #e67e22 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f39c12 !important;
        margin: 1rem 0;
        color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .tech-questions {
        background-color: #8e44ad !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #9b59b6 !important;
        margin: 1rem 0;
        color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Streamlit specific overrides */
    .stMarkdown p {
        color: #ffffff !important;
    }
    
    .stMarkdown strong {
        color: #ffffff !important;
    }
    
    .stMarkdown em {
        color: #ffffff !important;
    }
    
    /* Input fields with dark background */
    .stTextInput > div > div > input {
        color: #ffffff !important;
        background-color: #2c3e50 !important;
        border: 1px solid #34495e !important;
    }
    
    .stSelectbox > div > div > div {
        color: #ffffff !important;
        background-color: #2c3e50 !important;
    }
    
    .stTextArea > div > div > textarea {
        color: #ffffff !important;
        background-color: #2c3e50 !important;
        border: 1px solid #34495e !important;
    }
    
    /* Buttons */
    .stButton > button {
        color: #ffffff !important;
        background-color: #3498db !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .stButton > button:hover {
        background-color: #2980b9 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
    
    /* Sidebar */
    .css-1d391kg {
        color: #ffffff !important;
        background-color: #2c3e50 !important;
    }
    
    /* Force white text on all elements */
    * {
        color: #ffffff !important;
    }
    
    /* Exception for buttons */
    .stButton > button {
        color: #ffffff !important;
    }
    
    /* Dark theme for the entire app */
    .stApp {
        background-color: #1e1e1e !important;
    }
    
    /* Form elements */
    .stForm {
        background-color: #2c3e50 !important;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Labels and text */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* Placeholder text */
    .stTextInput > div > div > input::placeholder {
        color: #bdc3c7 !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #bdc3c7 !important;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class CandidateInfo:
    """Data class to store candidate information"""
    session_id: str
    full_name: str = ""
    email: str = ""
    phone: str = ""
    experience_years: str = ""
    desired_positions: str = ""
    current_location: str = ""
    tech_stack: str = ""
    timestamp: str = ""

class HiringAssistant:
    """Main class for the Hiring Assistant chatbot"""
    
    def __init__(self):
        self.conversation_states = {
            'GREETING': 'greeting',
            'COLLECTING_INFO': 'collecting_info',
            'TECH_QUESTIONS': 'tech_questions',
            'COMPLETED': 'completed',
            'ENDED': 'ended'
        }
        
        self.required_fields = [
            'full_name', 'email', 'phone', 'experience_years',
            'desired_positions', 'current_location', 'tech_stack'
        ]
        
        self.exit_keywords = [
            'bye', 'goodbye', 'exit', 'quit', 'end', 'stop',
            'thanks', 'thank you', 'done', 'finish'
        ]
        
        # Initialize session state
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session state variables"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'conversation_state' not in st.session_state:
            st.session_state.conversation_state = self.conversation_states['GREETING']
        
        if 'candidate_info' not in st.session_state:
            st.session_state.candidate_info = CandidateInfo(
                session_id=st.session_state.session_id,
                timestamp=datetime.now().isoformat()
            )
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'current_field' not in st.session_state:
            st.session_state.current_field = 0
        
        if 'technical_questions' not in st.session_state:
            st.session_state.technical_questions = []
        
        if 'answers_collected' not in st.session_state:
            st.session_state.answers_collected = {}
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^[\+]?[1-9][\d]{3,14}$|^[\d]{10}$'
        return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None
    
    def is_exit_keyword(self, user_input: str) -> bool:
        """Check if user wants to exit"""
        return any(keyword in user_input.lower() for keyword in self.exit_keywords)
    
    def generate_greeting(self) -> str:
        """Generate initial greeting message"""
        return """
        🤖 **Welcome to TalentScout AI Hiring Assistant!**
        
        Hello! I'm here to help you with your job application process. I'll gather some essential information about you and ask a few technical questions based on your expertise.
        
        This process typically takes 5-10 minutes and includes:
        - 📋 Basic information collection
        - 💻 Technical stack discussion
        - ❓ Relevant technical questions
        
        Let's get started! May I have your **full name** please?
        
        *(You can type 'exit' or 'bye' anytime to end our conversation)*
        """
    
    def get_field_prompt(self, field_index: int) -> str:
        """Get prompt for specific field collection"""
        prompts = {
            0: "Great! Now, could you please provide your **email address**?",
            1: "Perfect! What's your **phone number**?",
            2: "Thanks! How many **years of experience** do you have in technology?",
            3: "Excellent! What **position(s)** are you interested in applying for?",
            4: "Good to know! What's your **current location** (city, country)?",
            5: """Perfect! Now, please tell me about your **technical stack**. 
            
            Include:
            - Programming languages (e.g., Python, JavaScript, Java)
            - Frameworks (e.g., React, Django, Spring)
            - Databases (e.g., MySQL, MongoDB, PostgreSQL)
            - Tools & Technologies (e.g., Docker, AWS, Git)
            
            Example: "Python, Django, PostgreSQL, Docker, AWS, Git"
            """
        }
        return prompts.get(field_index, "Please provide the requested information.")
    
    def validate_field_input(self, field_name: str, value: str) -> tuple[bool, str]:
        """Validate specific field input"""
        if not value.strip():
            return False, "This field cannot be empty. Please provide the required information."
        
        if field_name == 'email':
            if not self.validate_email(value):
                return False, "Please provide a valid email address (e.g., user@example.com)."
        
        elif field_name == 'phone':
            if not self.validate_phone(value):
                return False, "Please provide a valid phone number (e.g., +1234567890 or 1234567890)."
        
        elif field_name == 'experience_years':
            try:
                years = float(value)
                if years < 0 or years > 50:
                    return False, "Please provide a valid number of years (0-50)."
            except ValueError:
                return False, "Please provide a valid number for years of experience (e.g., 2, 3.5)."
        
        return True, ""
    
    def generate_technical_questions(self, tech_stack: str) -> List[Dict]:
        """Generate technical questions based on tech stack"""
        tech_stack_lower = tech_stack.lower()
        questions = []
        
        # Tech-specific question templates
        tech_questions = {
            'python': [
                "What is the difference between a list and a tuple in Python?",
                "Explain Python's GIL (Global Interpreter Lock) and its implications.",
                "How do you handle exceptions in Python? Provide an example.",
                "What are Python decorators and how do you use them?"
            ],
            'javascript': [
                "Explain the concept of closures in JavaScript with an example.",
                "What is the difference between '==' and '===' in JavaScript?",
                "How does event delegation work in JavaScript?",
                "Explain the difference between 'var', 'let', and 'const'."
            ],
            'java': [
                "What is the difference between abstract classes and interfaces in Java?",
                "Explain Java's garbage collection mechanism.",
                "What are the principles of OOP and how does Java implement them?",
                "How do you handle multithreading in Java?"
            ],
            'react': [
                "What is the difference between state and props in React?",
                "Explain the React component lifecycle methods.",
                "How do React hooks work? Give examples of useState and useEffect.",
                "What is the virtual DOM and how does it improve performance?"
            ],
            'django': [
                "Explain Django's MTV (Model-Template-View) architecture.",
                "How do Django migrations work?",
                "What is Django ORM and how do you perform database queries?",
                "How do you handle authentication and authorization in Django?"
            ],
            'sql': [
                "What is the difference between INNER JOIN and LEFT JOIN?",
                "Explain database normalization and its benefits.",
                "How do you optimize slow SQL queries?",
                "What are database indexes and when should you use them?"
            ],
            'aws': [
                "What are the main differences between EC2, ECS, and Lambda?",
                "How do you secure AWS resources?",
                "Explain the concept of AWS VPC and its components.",
                "What is the difference between S3 storage classes?"
            ],
            'docker': [
                "What is the difference between a Docker image and a container?",
                "How do you optimize Docker images for production?",
                "Explain Docker networking and volume management.",
                "What is Docker Compose and when do you use it?"
            ]
        }
        
        # Select questions based on mentioned technologies
        selected_questions = []
        for tech, tech_q in tech_questions.items():
            if tech in tech_stack_lower:
                selected_questions.extend(tech_q[:2])  # Take 2 questions per tech
        
        # If no specific tech found, use general questions
        if not selected_questions:
            selected_questions = [
                "Describe your experience with software development lifecycle.",
                "How do you approach debugging a complex issue?",
                "What's your experience with version control systems like Git?",
                "How do you stay updated with new technologies?"
            ]
        
        # Limit to 5 questions and format them
        for i, question in enumerate(selected_questions[:5], 1):
            questions.append({
                'id': i,
                'question': question,
                'tech_related': True
            })
        
        return questions
    
    def save_candidate_data(self):
        """Save candidate data (simulated - in production, this would go to a database)"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('candidate_data', exist_ok=True)
            
            # Save to JSON file (simulated database)
            filename = f"candidate_data/candidate_{st.session_state.session_id}.json"
            data = {
                'candidate_info': asdict(st.session_state.candidate_info),
                'technical_questions': st.session_state.technical_questions,
                'answers': st.session_state.answers_collected,
                'chat_history': st.session_state.chat_history[-10:]  # Save last 10 messages
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
            return False
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input based on current conversation state"""
        if not user_input.strip():
            return "I didn't receive any input. Could you please type your response?"
        
        # Check for exit keywords
        if self.is_exit_keyword(user_input):
            st.session_state.conversation_state = self.conversation_states['ENDED']
            return self.generate_goodbye_message()
        
        current_state = st.session_state.conversation_state
        
        if current_state == self.conversation_states['GREETING']:
            return self.handle_greeting_state(user_input)
        elif current_state == self.conversation_states['COLLECTING_INFO']:
            return self.handle_info_collection_state(user_input)
        elif current_state == self.conversation_states['TECH_QUESTIONS']:
            return self.handle_tech_questions_state(user_input)
        else:
            return "I'm not sure how to help with that. Could you please rephrase?"
    
    def handle_greeting_state(self, user_input: str) -> str:
        """Handle the greeting state - collect full name"""
        if len(user_input.strip()) < 2:
            return "Please provide your full name (at least 2 characters)."
        
        st.session_state.candidate_info.full_name = user_input.strip()
        st.session_state.conversation_state = self.conversation_states['COLLECTING_INFO']
        st.session_state.current_field = 0
        
        return f"Nice to meet you, {user_input.strip()}! {self.get_field_prompt(0)}"
    
    def handle_info_collection_state(self, user_input: str) -> str:
        """Handle information collection state"""
        field_names = ['email', 'phone', 'experience_years', 'desired_positions', 'current_location', 'tech_stack']
        current_field_index = st.session_state.current_field
        
        if current_field_index >= len(field_names):
            # All fields collected, move to tech questions
            return self.transition_to_tech_questions()
        
        field_name = field_names[current_field_index]
        
        # Validate input
        is_valid, error_message = self.validate_field_input(field_name, user_input)
        
        if not is_valid:
            return f"❌ {error_message}\n\n{self.get_field_prompt(current_field_index)}"
        
        # Store the valid input
        setattr(st.session_state.candidate_info, field_name, user_input.strip())
        st.session_state.current_field += 1
        
        # Check if we've collected all fields
        if st.session_state.current_field >= len(field_names):
            return self.transition_to_tech_questions()
        
        # Ask for next field
        return f"✅ Got it! {self.get_field_prompt(st.session_state.current_field)}"
    
    def transition_to_tech_questions(self) -> str:
        """Transition to technical questions phase"""
        st.session_state.conversation_state = self.conversation_states['TECH_QUESTIONS']
        
        # Generate technical questions
        tech_stack = st.session_state.candidate_info.tech_stack
        st.session_state.technical_questions = self.generate_technical_questions(tech_stack)
        
        questions_text = "\n".join([
            f"**Q{q['id']}.** {q['question']}" 
            for q in st.session_state.technical_questions
        ])
        
        return f"""
        🎉 **Great! I've collected all your information.**
        
        Based on your tech stack ({tech_stack}), I've prepared some technical questions for you:
        
        {questions_text}
        
        **Please answer these questions one by one. You can take your time!**
        
        Let's start with **Question 1**: {st.session_state.technical_questions[0]['question']}
        """
    
    def handle_tech_questions_state(self, user_input: str) -> str:
        """Handle technical questions state"""
        if not st.session_state.technical_questions:
            return "No technical questions available. Please restart the conversation."
        
        # Determine which question we're currently on
        answered_count = len(st.session_state.answers_collected)
        
        if answered_count >= len(st.session_state.technical_questions):
            # All questions answered
            return self.complete_interview()
        
        # Store the answer
        current_question_id = st.session_state.technical_questions[answered_count]['id']
        st.session_state.answers_collected[f"question_{current_question_id}"] = user_input.strip()
        
        next_question_index = answered_count + 1
        
        if next_question_index >= len(st.session_state.technical_questions):
            # This was the last question
            return self.complete_interview()
        
        # Ask next question
        next_question = st.session_state.technical_questions[next_question_index]
        return f"""
        ✅ **Thank you for your answer!**
        
        **Question {next_question['id']}**: {next_question['question']}
        """
    
    def complete_interview(self) -> str:
        """Complete the interview process"""
        st.session_state.conversation_state = self.conversation_states['COMPLETED']
        
        # Save candidate data
        self.save_candidate_data()
        
        return """
        🎉 **Congratulations! You've completed the initial screening process.**
        
        📋 **What happens next:**
        - Your responses have been recorded and will be reviewed by our recruitment team
        - You should hear back from us within 2-3 business days
        - If your profile matches our requirements, we'll schedule a detailed technical interview
        
        📧 **Contact Information:**
        - Email: hr@talentscout.com
        - Phone: +1-555-TALENT
        
        Thank you for your time and interest in our opportunities!
        
        *(You can type 'bye' to end this conversation)*
        """
    
    def generate_goodbye_message(self) -> str:
        """Generate goodbye message"""
        return """
        👋 **Thank you for using TalentScout AI Hiring Assistant!**
        
        If you didn't complete the full process, don't worry - you can always start again later.
        
        For any questions or concerns, please contact us at:
        📧 hr@talentscout.com
        📞 +1-555-TALENT
        
        Have a great day! 🌟
        """
    
    def get_candidate_summary(self) -> str:
        """Get candidate information summary"""
        info = st.session_state.candidate_info
        
        if not info.full_name:
            return "No candidate information collected yet."
        
        summary = f"""
        **👤 Candidate Information:**
        - **Name:** {info.full_name}
        - **Email:** {info.email or 'Not provided'}
        - **Phone:** {info.phone or 'Not provided'}
        - **Experience:** {info.experience_years or 'Not provided'} years
        - **Desired Position(s):** {info.desired_positions or 'Not provided'}
        - **Location:** {info.current_location or 'Not provided'}
        - **Tech Stack:** {info.tech_stack or 'Not provided'}
        """
        
        return summary

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">🤖 TalentScout AI Hiring Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Recruitment Screening for Technology Professionals</p>', unsafe_allow_html=True)
    
    # Initialize the hiring assistant
    assistant = HiringAssistant()
    
    # Sidebar with candidate information
    with st.sidebar:
        st.markdown("### 📊 Session Information")
        st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**State:** {st.session_state.conversation_state.title()}")
        
        if st.session_state.candidate_info.full_name:
            st.markdown("### 👤 Candidate Info")
            st.markdown(assistant.get_candidate_summary())
        
        if st.session_state.technical_questions:
            st.markdown("### ❓ Technical Questions")
            for i, q in enumerate(st.session_state.technical_questions, 1):
                status = "✅" if f"question_{q['id']}" in st.session_state.answers_collected else "⏳"
                st.markdown(f"{status} Q{i}: {q['question'][:50]}...")
        
        # Reset button
        if st.button("🔄 Start New Session", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main chat interface
    st.markdown("### 💬 Chat Interface")
    
    # Initialize chat with greeting if first time
    if not st.session_state.chat_history and st.session_state.conversation_state == assistant.conversation_states['GREETING']:
        greeting = assistant.generate_greeting()
        st.session_state.chat_history.append(("assistant", greeting))
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for role, message in st.session_state.chat_history:
            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>TalentScout AI:</strong><br>{message}</div>', unsafe_allow_html=True)
    
    # Input area
    if st.session_state.conversation_state != assistant.conversation_states['ENDED']:
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append(("user", user_input))
            
            # Process input and get response
            response = assistant.process_user_input(user_input)
            
            # Add assistant response to history
            st.session_state.chat_history.append(("assistant", response))
            
            # Rerun to update the display
            st.rerun()
    else:
        st.info("💬 Conversation ended. Click 'Start New Session' to begin again.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>🤖 TalentScout AI Hiring Assistant | Powered by Advanced Language Models</p>
        <p>📧 Contact: hr@talentscout.com | 📞 +1-555-TALENT</p>
        <p>🔒 Your data is handled securely and in compliance with privacy standards</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()