import openai
import requests
import streamlit as st


def get_openai_models(api_key):
    try:
        openai.api_key = api_key
        models = openai.Model.list()
        return [m.id for m in models.data if m.id.startswith("gpt")]
    except Exception as e:
        st.warning(f"OpenAI model listing failed: {e}")
        return []


def get_ollama_models(ollama_url):
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        data = response.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        st.warning(f"Ollama model listing failed: {e}")
        return []


def stream_chat_response(history, model, api_key=None, ollama_url=None):
    if api_key:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=history,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                yield chunk.choices[0].delta.content

    elif ollama_url:
        response = requests.post(
            f"{ollama_url}/api/chat",
            json={"model": model, "messages": history, "stream": True},
            stream=True,
        )
        for line in response.iter_lines():
            if line:
                try:
                    content = line.decode("utf-8")
                    if 'content":"' in content:
                        yield content.split('content":"', 1)[1].split('"')[0]
                except Exception:
                    continue


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
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
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
