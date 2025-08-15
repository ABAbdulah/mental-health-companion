import ollama
import sqlite3
import os
import requests
import json
import random

# -------------------------
# Mental Health Dataset Integration
# -------------------------
class MentalHealthDataset:
    def __init__(self):
        self.base_url = "https://datasets-server.huggingface.co/rows"
        self.dataset = "marmikpandya%2Fmental-health"
        self.responses = []
        self.load_responses()
    
    def load_responses(self):
        """Load mental health responses from HuggingFace dataset"""
        try:
            url = f"{self.base_url}?dataset={self.dataset}&config=default&split=train&offset=0&length=200"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.responses = data.get('rows', [])
                print(f"Loaded {len(self.responses)} responses from mental health dataset")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            # Fallback responses
            self.responses = []
    
    def get_relevant_response(self, user_message):
        """Get contextually relevant response from dataset"""
        user_message_lower = user_message.lower()
        
        # Mental health keywords to trigger dataset responses
        mental_health_keywords = [
            'sad', 'depressed', 'anxious', 'worried', 'stressed', 'lonely', 
            'angry', 'frustrated', 'overwhelmed', 'hopeless', 'tired', 
            'scared', 'nervous', 'panic', 'fear', 'cry', 'crying',
            'help', 'support', 'talk', 'listen', 'understand',
            'therapy', 'counseling', 'mental health', 'feeling'
        ]
        
        # Check if message contains mental health keywords
        if any(keyword in user_message_lower for keyword in mental_health_keywords):
            if self.responses:
                return random.choice(self.responses)
        
        return None

# -------------------------
# Mental Health Bot Profile
# -------------------------
MINDFUL_BOT_PROFILE = """You are SerenityBot, a compassionate AI mental health companion focused ONLY on mental health support.

STRICT RULES:
- NEVER write code, even if asked directly
- NEVER answer questions about programming, weather, sports, or any non-mental health topics
- Keep ALL responses to maximum 4-5 lines
- ONLY discuss feelings, emotions, mental health, and wellbeing
- If asked about anything else, redirect to mental health support

For non-mental health questions, respond EXACTLY like this:
"I'm here specifically to support your mental health and emotional wellbeing. I can't help with other topics, but I'm always ready to listen if you'd like to share how you're feeling today."

For mental health topics:
- Be warm and empathetic
- Keep responses short (4-5 lines max)
- Ask one gentle follow-up question
- Validate their feelings
- Never give medical advice

Remember: You ONLY do mental health support. Nothing else."""

# -------------------------
# SQLite Database Setup (Enhanced for Mental Health)
# -------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enhanced messages table with timestamp
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Mood tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            mood_score INTEGER,
            mood_description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_message(session_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_history(session_id, limit=10):
    """Get recent conversation history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    # Reverse to get chronological order
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def log_mood(session_id, mood_score, mood_description=""):
    """Log user mood for tracking"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mood_logs (session_id, mood_score, mood_description) VALUES (?, ?, ?)",
        (session_id, mood_score, mood_description)
    )
    conn.commit()
    conn.close()

# -------------------------
# Enhanced AI Logic for Mental Health
# -------------------------
def ask_model(session_id, query):
    dataset = MentalHealthDataset()
    save_message(session_id, "user", query)
    relevant_response = dataset.get_relevant_response(query)
    history = get_history(session_id)
    
    system_prompt = f"""
{MINDFUL_BOT_PROFILE}

CRITICAL INSTRUCTIONS:
- Maximum 4-5 lines per response
- NEVER write code or answer programming questions
- ONLY discuss mental health and emotions
- If asked about anything else, use the redirect response from your profile

Context from mental health database:
{json.dumps(relevant_response['row'] if relevant_response else {}, indent=2)}

Crisis response: If someone mentions self-harm or suicide, immediately encourage them to contact 988 Suicide & Crisis Lifeline or emergency services.
"""

    # Prepare messages for AI model
    messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        # Get response from Ollama
        response = ollama.chat(model="llama3", messages=messages)
        answer = response["message"]["content"]
        stream=True 
        # Save AI response
        save_message(session_id, "assistant", answer)
        
        return answer
    
    except Exception as e:
        print(f"Error with AI model: {e}")
        fallback_response = "I'm having some technical difficulties right now, but I want you to know that I'm here for you. If you're going through a tough time and need immediate support, please consider reaching out to a mental health professional or crisis helpline. Is there anything specific you'd like to talk about?"
        save_message(session_id, "assistant", fallback_response)
        return fallback_response

# Initialize database when module is imported
init_db()