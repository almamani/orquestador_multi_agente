import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

if not os.getenv("OPENAI_API_KEY", "").strip():
    raise ValueError(
        "Falta OPENAI_API_KEY. Configurala en el archivo .env."
    )

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)