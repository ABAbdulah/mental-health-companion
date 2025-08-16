import ollama
import sqlite3
import os
import json
import random

# -------------------------
# Mental Health Dataset Integration (FAST - NO EXTERNAL CALLS)
# -------------------------
class MentalHealthDataset:
    def __init__(self):
        self.responses = [
            {"row": {"text": "I understand you're going through a difficult time. It's okay to feel overwhelmed sometimes."}},
            {"row": {"text": "Your feelings are valid, and it takes courage to reach out for support."}},
            {"row": {"text": "Remember that you're not alone in this journey. Many people face similar challenges."}},
            {"row": {"text": "It's important to be gentle with yourself during tough times."}},
            {"row": {"text": "Taking one small step at a time can make a big difference in how you feel."}},
        ]
    
    def get_relevant_response(self, user_message):
        """Get contextually relevant response from dataset"""
        user_message_lower = user_message.lower()
        
        mental_health_keywords = [
            'sad', 'depressed', 'anxious', 'worried', 'stressed', 'lonely', 
            'angry', 'frustrated', 'overwhelmed', 'hopeless', 'tired', 
            'scared', 'nervous', 'panic', 'fear', 'cry', 'crying',
            'help', 'support', 'talk', 'listen', 'understand',
            'therapy', 'counseling', 'mental health', 'feeling'
        ]
        
        if any(keyword in user_message_lower for keyword in mental_health_keywords):
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
# SQLite Database Setup
# -------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
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

def get_history(session_id, limit=6):  # Reduced history for faster processing
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

# -------------------------
# Global dataset instance
# -------------------------
_dataset_instance = None

def get_dataset():
    global _dataset_instance
    if _dataset_instance is None:
        _dataset_instance = MentalHealthDataset()
    return _dataset_instance

# -------------------------
# STREAMING AI Logic (THE FIX)
# -------------------------
def ask_model_stream(session_id, query):
    """STREAMING version that yields chunks as they come"""
    dataset = get_dataset()
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

    messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        # STREAMING OLLAMA CALL - This is the key fix
        full_response = ""
        stream = ollama.chat(
            model="llama3", 
            messages=messages, 
            stream=True  # ENABLE STREAMING
        )
        
        for chunk in stream:
            content = chunk['message']['content']
            full_response += content
            yield content  # Yield each chunk immediately
        
        # Save complete response after streaming
        save_message(session_id, "assistant", full_response)
    
    except Exception as e:
        print(f"Error with AI model: {e}")
        fallback = "I'm having some technical difficulties right now, but I want you to know that I'm here for you."
        save_message(session_id, "assistant", fallback)
        yield fallback

# -------------------------
# Non-streaming version (backward compatibility)
# -------------------------
def ask_model(session_id, query):
    """Non-streaming version"""
    full_response = ""
    for chunk in ask_model_stream(session_id, query):
        full_response += chunk
    return full_response

# Initialize database when module is imported
init_db()