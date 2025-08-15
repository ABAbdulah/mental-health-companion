import ollama
import sqlite3
import os

# -------------------------
# Abdullah's profile (baked in)
# -------------------------
ABDULLAH_PROFILE = """Abdullah Tahir is a Computer Science graduate from the National University of Computer and Emerging Sciences (FAST), Islamabad, originally from Faisalabad, Pakistan. He moved to Islamabad in 2021 to pursue his bachelor’s degree and has loved the city ever since.

He is currently working as a Frontend Engineer at Micro Agility, where he has built projects in React with TypeScript, implemented Zod for writing validation schemas, and translated pixel-perfect Figma designs into fully functional React applications. He developed a custom rich text editor for the company's JobsinGTA platform and has worked extensively with useRef, React hooks, and useEffect, along with other advanced React concepts.

Abdullah’s Final Year Project (FYP), ARch360, was an AR-powered Android application designed to bridge the gap between customers, construction specialists, and architects. The application allows laymen to import FBX format files from their architects and visualize homes or commercial buildings in augmented reality before construction begins. This ensures that clients can clearly communicate their design requirements, potentially saving millions by preventing miscommunication and costly human errors.

Previously, Abdullah completed a 6+ month remote internship as a Software Engineer at FAIR (Football and AI Research), a UK-based startup, where he worked on backend APIs, player data mapping tasks between FotMob and Opta, and various database-driven features using FastAPI and MongoDB.

Over the past few years, Abdullah has worked on multiple projects, including:
- Meta Store.pk
- After Realism
- Divlynx – his personal/company website built with React.js and custom CSS
- E-commerce admin APIs using FastAPI and MongoDB
- AR wall color customization features in Unity

He has 1+ year of experience in React.js and is skilled in Python, C++, JavaScript, TypeScript, MERN stack, TensorFlow, Pandas, SciPy, Scikit-learn, and OpenCV. He has used Resend API with Next.js for sending emails via contact forms and deployed projects on Cloudflare Pages.

Abdullah is passionate about Generative AI and AI model inference, having explored Hugging Face for text-to-image generation and LLaMA model deployment on local GPUs. He has also started building AI chatbot projects to showcase his growing expertise as he transitions from frontend development to an AI Engineer role.

He is open to challenges and actively seeking opportunities to prove his skills in AI engineering. Alongside this, Abdullah offers his services as both a Full Stack Developer and AI Engineer on Upwork.

His personal interests include game development, front-end development, nature, and astronomy. He also has a strong entrepreneurial drive — targeting businesses in Australia and the US for website development, creating and selling Notion templates (one template reached over 11k views), and planning to launch an old-money fashion brand in the future."""

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
            content TEXT
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

def get_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id=? ORDER BY id",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

# -------------------------
# AI Logic
# -------------------------
def ask_model(session_id, query):
    # Save user message
    save_message(session_id, "user", query)
    # Retrieve full conversation
    history = get_history(session_id)
    # Build system prompt
    system_prompt = f"""
You are a helpful assistant.
Here is information about Abdullah Tahir:
{ABDULLAH_PROFILE}

Rules:
- If greeted, greet politely.
- If asked about Abdullah, answer briefly and to the point.
- If asked about Abdullah's work, provide details about his projects and skills.
- If asked about AI, mention his interest in Generative AI and model inference.
- If asked about programming, provide relevant information from his profile.
- If asked about his education, mention his Computer Science degree from FAST.
- If asked about his internship, describe his role at FAIR.
- If asked about his FYP, explain the ARch360 project.
- If asked about his personal interests, mention game development, front-end development, nature, and astronomy.
- If asked about his entrepreneurial ventures, mention his Upwork services and Notion templates.
- don't use any outside knowledge.
- if asked about programming, world events, or anything outside the context, give the refusal message above.
- if asked to write code , dont write code, just say "I am not able to write code at the moment."
- If unsure, say: Contact Abdullah on WhatsApp at +923187070410 or email him at ababdullah216@gmail.com.
"""

    # Combine into message format
    messages = [{"role": "system", "content": system_prompt}] + history

    # Get AI response
    response = ollama.chat(model="llama3", messages=messages)
    answer = response["message"]["content"]

    # Save AI response
    save_message(session_id, "assistant", answer)

    return answer

# Initialize database at import
init_db()
