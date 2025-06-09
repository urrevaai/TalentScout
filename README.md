# 🤖 TalentScout AI Hiring Assistant

An intelligent AI-powered hiring assistant built with Streamlit that helps streamline the candidate screening process through automated technical interviews.

## 🚀 Features

- **Smart Candidate Profiling**: Collects essential candidate information
- **Technical Question Generation**: Pre-built questions based on candidate's tech stack
- **Interactive Chat Interface**: Natural conversation flow with the AI assistant
- **Data Validation**: Email and phone number validation
- **Session Management**: Persistent conversation state
- **Local Data Storage**: Saves candidate data to JSON files

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection (for Streamlit)

## 🛠️ Installation & Setup

### 1. **Required Files**
You only need these 2 files to run the application:
```
cht/
├── app1.py              # Main application file
└── requirements.txt     # Python dependencies
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Run the Application**
```bash
streamlit run app1.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📱 How to Use

1. **Start the Conversation**: The AI assistant will greet you and ask for your full name
2. **Provide Information**: Answer questions about your experience, desired position, and tech stack
3. **Technical Questions**: The AI will present relevant technical questions based on your expertise
4. **Complete Interview**: Answer the questions and receive a summary
5. **Data Saved**: Candidate information is automatically saved to local files

## 🏗️ Project Structure

```
cht/
├── app1.py              # Main application (self-contained)
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── models/             # Auto-created directory
└── candidate_data/     # Auto-created directory for saved data
    └── candidate_[session_id].json  # Individual candidate files
```

## 🔧 How It Works

### **Self-Contained Application**
- **No external APIs required** - All functionality is built-in
- **Local data storage** - Saves candidate data to JSON files
- **Pre-built questions** - Technical questions are generated from predefined templates
- **Offline capable** - Works without internet (except for initial Streamlit loading)

### **Data Flow**
1. User interacts with the chat interface
2. Information is validated and stored in session
3. Technical questions are generated based on tech stack
4. All data is saved to `candidate_data/` folder
5. Each session creates a unique JSON file

## 🎯 Key Features Explained

### **Smart Question Generation**
The application analyzes the candidate's tech stack and presents relevant technical questions from a predefined database of questions.

### **Data Validation**
- Email format validation
- Phone number validation
- Experience year validation
- Required field validation

### **Session Management**
- Persistent conversation state
- Automatic session ID generation
- Chat history tracking

## 🆘 Troubleshooting

### **Common Issues**

1. **Streamlit Not Starting**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

2. **Import Errors**
   - Reinstall dependencies: `pip install --upgrade -r requirements.txt`

3. **Port Already in Use**
   - Use a different port: `streamlit run app1.py --server.port 8502`

### **Getting Help**
If you encounter any issues, please check the error messages in the terminal or browser console for specific details.

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues and enhancement requests! 