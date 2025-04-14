# ai/ai_summary.py
import streamlit as st
import asyncio
from pathlib import Path
import openai
import requests
from scan.pipeline import full_cli_equivalent_scan

CHAT_HISTORY_KEY = "ai_chat_history"


def run_ai_summary_ui():
    st.title("\U0001F9E0 AI Repo Summary & Chat")

    st.markdown("Input either an **OpenAI API key** or **Ollama endpoint**, and a GitHub repository URL.")

    col1, col2 = st.columns(2)
    with col1:
        api_key = st.text_input("\U0001F511 OpenAI API Key", type="password")
    with col2:
        ollama_url = st.text_input("\U0001F310 Ollama Endpoint (http://localhost:11434)")

    repo_url = st.text_input("\U0001F4E6 GitHub Repository URL", placeholder="https://github.com/username/repo")

    if st.button("\U0001F680 Analyze Repository") and repo_url and (api_key or ollama_url):
        with st.status("Running docs-only scan...", expanded=True):
            filters = {
                "branch": None,
                "subdir": None,
                "include_patterns": [],
                "exclude_patterns": [],
                "exclude_dirs": [],
                "size_limit": 5_000_000,
                "output_formats": ["md"],
                "output_dir": "/tmp/gittxt_ai_summary",
                "lite": True,
                "zip": False,
                "skip_tree": True,
                "tree_depth": 5,
                "sync": False,
                "docs_only": True,
            }
            result = asyncio.run(full_cli_equivalent_scan(repo_url, filters))
            if result.get("error"):
                st.error(result["error"])
                return

            st.session_state.repo_docs = result
            md_files = result["output_files"]
            context = "\n\n".join(Path(f).read_text() for f in md_files if Path(f).suffix == ".md")

            if api_key:
                summary = generate_summary_with_llm(context, model="gpt-3.5-turbo", api_key=api_key)
            elif ollama_url:
                summary = generate_summary_with_llm(context, model="llama3", ollama_url=ollama_url)

            st.markdown("### \U0001F4DC Repository Summary")
            st.info(summary)

            st.session_state[CHAT_HISTORY_KEY] = [{"role": "system", "content": summary}]

    st.markdown("### \U0001F4AC Chat with the Repo")

    if CHAT_HISTORY_KEY in st.session_state:
        user_input = st.chat_input("Ask about the repo...")

        for msg in st.session_state[CHAT_HISTORY_KEY]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_input:
            st.session_state[CHAT_HISTORY_KEY].append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            if api_key:
                reply = chat_with_llm(st.session_state[CHAT_HISTORY_KEY], api_key=api_key)
            elif ollama_url:
                reply = chat_with_llm(st.session_state[CHAT_HISTORY_KEY], ollama_url=ollama_url)
            else:
                reply = "❌ No valid LLM backend."

            st.session_state[CHAT_HISTORY_KEY].append({"role": "assistant", "content": reply})

            with st.chat_message("assistant"):
                st.markdown(reply)


def generate_summary_with_llm(context, model="gpt-3.5-turbo", api_key=None, ollama_url=None):
    prompt = (
        "You are an expert at analyzing code repositories. Based on the documentation below, "
        "generate a clear summary of the project’s purpose, structure, and key components:\n\n"
        + context
    )

    if api_key:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    elif ollama_url:
        response = requests.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()["message"]["content"].strip()

    return "❌ No valid LLM credentials provided."


def chat_with_llm(history, model="gpt-3.5-turbo", api_key=None, ollama_url=None):
    if api_key:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(model=model, messages=history)
        return response.choices[0].message.content.strip()

    elif ollama_url:
        response = requests.post(f"{ollama_url}/api/chat", json={"model": model, "messages": history})
        return response.json()["message"]["content"].strip()

    return "❌ No valid LLM credentials."
