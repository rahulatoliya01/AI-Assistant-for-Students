
from google import genai
from db_utils import load_knowledge

client = genai.Client(api_key="AIzaSyBtY7boSAneqUvaWre_nHcpMoJLoLtUOB8")

SYSTEM_PROMPT = (
    "You are SVU-MCA Assistant for MCA students of Samrat Vikramaditya University, Ujjain. "
    "Answer clearly using provided university data and student context. "
    "Be friendly, professional, and student-focused."
)

def ask_ai(question, recent_context=""):
    knowledge = load_knowledge()
    knowledge_text = "\n".join([k["title"] + ": " + k["description"] for k in knowledge])
    full_context = SYSTEM_PROMPT + "\n\n" + knowledge_text + "\n\nRecent student context:\n" + recent_context
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_context + "\n\nQuestion: " + question,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}\nYou may have exceeded your API quota."