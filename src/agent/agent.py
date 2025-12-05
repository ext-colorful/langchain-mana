from dataclasses import dataclass
import os
from urllib.parse import quote_plus

from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from agent.utils.db_utils import SecureDatabaseToolkit

db_toolkit = SecureDatabaseToolkit(
    database_uri="postgresql://postgres:qNxLn%407nNy3Czx%40@sbp-ryxlih7k8b5udx72.supabase.opentrust.net:5432/mana",
    pool_size=10
)

SYSTEM_PROMPT = """You are a careful Postgres analyst.

Rules:
- Think step-by-step.
- When you need data, call the tool `execute_sql` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows of output unless the user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Prefer explicit column lists; avoid SELECT *.
"""

agent = create_agent(
    model="openai:gpt-3.5-turbo",
    tools=db_toolkit.tools,
    system_prompt=SYSTEM_PROMPT,
)