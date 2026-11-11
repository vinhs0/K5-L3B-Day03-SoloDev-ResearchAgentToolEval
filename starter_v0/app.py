"""Streamlit UI for the Research Agent.

Run:  streamlit run app.py   ->  http://localhost:8501
Reuses the exact tool loop of chat.py and logs each session to transcripts/*.transcript.json.
"""
from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
EXAMPLES = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Alan Turing là ai?",
    "Cho mình 3 bài mới nhất về Rust trên Hacker News",
    "Tóm tắt 3 tweet mới nhất giúp mình",
    "Bây giờ ở Tokyo là mấy giờ?",
    "Đăng bản tin này lên Telegram giúp mình",
]


@st.cache_resource
def get_provider(name: str):
    return make_provider(name)


def new_session(provider_name: str, version: str) -> None:
    artifact = build_artifact_version(version, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", datetime.now().strftime("%Y%m%dT%H%M%S%f")])
    st.session_state.history = []      # what the model sees (user/assistant text)
    st.session_state.display = []      # what the UI shows (incl. tool calls)
    st.session_state.turn_index = 0
    st.session_state.transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.artifact_version = artifact.artifact_version


# ---------------- sidebar ----------------
with st.sidebar:
    st.title("🔎 Research Agent")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    version = st.text_input("Version label", value="v6")
    model = st.text_input("Model (optional)", value="") or None
    history_window = st.slider("History window (turns)", 1, 10, 5)
    max_rounds = st.slider("Max tool rounds", 1, 8, 4)
    show_tools = st.checkbox("Show tool calls & results", value=True)

    if st.button("🗑️ New conversation", use_container_width=True):
        new_session(provider_name, version)
        st.rerun()

    st.markdown("**Thử nhanh**")
    clicked = None
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
            clicked = ex

    st.divider()
    tools = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    st.caption(f"{len(tools)} tools: " + ", ".join(t["name"] for t in tools))

if "history" not in st.session_state:
    new_session(provider_name, version)

st.header("Research Agent")
st.caption(f"artifact_version: `{st.session_state.artifact_version}` · provider: `{provider_name}`")


def render_tool_events(events: list[dict]) -> None:
    for ev in events:
        with st.expander(f"🔧 {ev['tool']}({json.dumps(ev['args'], ensure_ascii=False)})"):
            st.json(ev["result"])


# ---------------- replay history ----------------
for msg in st.session_state.display:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and show_tools and msg.get("events"):
            render_tool_events(msg["events"])
        st.markdown(msg["content"])

# ---------------- new input ----------------
user_text = st.chat_input("Hỏi agent...") or clicked
if user_text:
    st.session_state.display.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    st.session_state.turn_index += 1
    turn = {"turn_index": st.session_state.turn_index, "started_at": now_iso(), "user": user_text}

    with st.chat_message("assistant"):
        try:
            with st.spinner("Đang suy nghĩ..."):
                result = run_model_tool_loop(
                    provider=get_provider(provider_name),
                    messages=messages,
                    tools=to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")),
                    model=model,
                    max_tool_rounds=max_rounds,
                )
            answer = result["assistant_text"]
            events = result["tool_events"]
            turn.update(result)
            if show_tools and events:
                render_tool_events(events)
            st.markdown(answer)
            st.session_state.history += [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": answer},
            ]
            st.session_state.display.append({"role": "assistant", "content": answer, "events": events})
        except Exception as exc:  # show provider errors instead of crashing the UI
            err = f"{type(exc).__name__}: {exc}"
            turn.update({"status": "provider_error", "error": err})
            st.error(err)

    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
