import streamlit as st
import asyncio
import nest_asyncio
from pathlib import Path
from scan.pipeline import full_cli_equivalent_scan
from ai.llm_handler import (
    get_openai_models,
    get_ollama_models,
    generate_summary_with_llm,
    chat_with_llm,
    stream_chat_response
)
from ai.context_builder import build_context
from ai.chat_exporter import export_chat_as_json, export_chat_as_markdown

nest_asyncio.apply()

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

    context_mode = st.radio("Select Context Mode", ["Docs Only", "Full Files"])
    full_mode = context_mode == "Full Files"
    docs_only = context_mode == "Docs Only"

    selected_model = None
    available_models = []

    if api_key:
        available_models = get_openai_models(api_key)
    elif ollama_url:
        available_models = get_ollama_models(ollama_url)

    if available_models:
        selected_model = st.selectbox("Select LLM Model", available_models)

    if st.button("\U0001F680 Analyze Repository") and repo_url and (api_key or ollama_url):
        context = ""
        used_files = []
        token_est = 0

        with st.status("Running scan...", expanded=True):
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
                "docs_only": docs_only,
            }
            result = asyncio.run(full_cli_equivalent_scan(repo_url, filters))

            if result.get("error"):
                st.error(result["error"])
                return

            st.session_state.repo_docs = result
            files = result["output_files"]
            context, used_files, token_est = build_context(
                files,
                include_txt=False,
                include_json=False,
                full_mode=full_mode
            )
            st.markdown("### Debug: Files from Scan")
            st.write(files)
            st.markdown("### Debug: Context String")
            st.code(context or "❌ Empty Context", language="markdown")


        with st.expander("\U0001F50D Context Preview", expanded=False):
            st.code(context[:1000] or "⚠️ No context extracted", language="markdown")

        if token_est > 8000:
            st.warning(f"⚠️ Total estimated tokens: {token_est}. Some models may truncate.")

        if api_key:
            summary = generate_summary_with_llm(context, model=selected_model or "gpt-3.5-turbo", api_key=api_key)
        elif ollama_url:
            summary = generate_summary_with_llm(context, model=selected_model or "llama3", ollama_url=ollama_url)

        st.markdown("### \U0001F4DC Repository Summary")
        st.info(summary)

        st.markdown("**Files Used:**")
        for f in used_files:
            st.code(f, language="text")

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

            with st.chat_message("assistant"):
                if api_key or ollama_url:
                    stream = stream_chat_response(
                        st.session_state[CHAT_HISTORY_KEY],
                        model=selected_model or "gpt-3.5-turbo",
                        api_key=api_key,
                        ollama_url=ollama_url,
                    )
                    full_response = st.write_stream(stream)
                    st.session_state[CHAT_HISTORY_KEY].append({"role": "assistant", "content": full_response})
                else:
                    st.warning("❌ No valid LLM backend.")

        with st.expander("\U0001F4BE Export Chat History"):
            export_format = st.selectbox("Choose Format", [".json", ".md"])
            if st.button("Export Chat"):
                history = st.session_state[CHAT_HISTORY_KEY]
                if export_format == ".json":
                    filepath = export_chat_as_json(history)
                else:
                    filepath = export_chat_as_markdown(history)
                st.success(f"Exported to: {filepath}")
