"""Streamlit interface for the literary modernism feature detector."""

import html
import os
import re

import streamlit as st

from modernism.file_reader import read_uploaded_file, strip_gutenberg_boilerplate
from modernism.kev_client import (
    DEFAULT_MODEL,
    KEV_API_BASE,
    MODELS,
    KevError,
    analyze_with_kev,
    check_connection,
    pick_excerpt,
)
from modernism import key_store
from modernism.lexicon import CATEGORIES
from modernism.scoring import analyze_text

DISCLAIMER = (
    "This app looks for features often linked with literary modernism (roughly "
    "1890–1940): its vocabulary, its ideas and the political ideas of that era. "
    "A high score means the text shares these features. It does not prove that "
    "the text belongs to the historical Modernist movement, because writers "
    "before and after that period use these features too."
)

CATEGORY_EXPLANATIONS = {
    "vocabulary": "Words connected with new technology, the modern city, psychology and modernist moods.",
    "ideas": "Words connected with alienation, fragmentation, inner life, loss of meaning, war and new forms.",
    "politics": "Words connected with class, feminism, empire, nationalism, war and the state.",
}


def _server_kev_key():
    """Return a valid Kev key configured for the hosted app, if present."""
    try:
        secret_key = st.secrets.get("KEV_DEMO_KEY")
    except Exception:
        secret_key = None

    for key in (secret_key, os.getenv("KEV_DEMO_KEY")):
        if isinstance(key, str):
            key = key.strip()
            if key.startswith("kevdemo_"):
                return key
    return None


def _redact_server_key(value, key):
    """Remove the hosted key from any Kev response before it is saved or shown."""
    if isinstance(value, str):
        return value.replace(key, "[redacted]")
    if isinstance(value, dict):
        return {
            _redact_server_key(name, key): _redact_server_key(item, key)
            for name, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_server_key(item, key) for item in value]
    return value


def _highlight_sentence(sentence, terms):
    """Escape sentence text and mark only matches from the supplied terms."""
    escaped_sentence = html.escape(sentence)
    spans = []
    for term in terms:
        normalized = term.lower().replace("’", "'")
        is_prefix = normalized.endswith("*")
        if is_prefix:
            normalized = normalized[:-1]
        parts = [re.escape(part) for part in normalized.split()]
        suffix = r"[a-z'-]*" if is_prefix else r"\b"
        pattern = re.compile(r"\b" + r"\s+".join(parts) + suffix, re.IGNORECASE)
        for match in pattern.finditer(sentence):
            start = len(html.escape(sentence[: match.start()]))
            end = len(html.escape(sentence[: match.end()]))
            spans.append((start, end))
    marked = escaped_sentence
    previous_end = len(marked)
    for start, end in sorted(set(spans), reverse=True):
        if end > previous_end:
            continue
        marked = marked[:start] + "<mark>" + marked[start:end] + "</mark>" + marked[end:]
        previous_end = start
    return marked


def _show_word_list_results(result):
    st.subheader("Word-list results")
    st.write(f"**Word count:** {result['word_count']:,}")
    if result["word_count"] < 500:
        st.warning(
            "Word-list scores are less reliable for short texts, especially those under 500 words."
        )

    categories = result["categories"]
    metric_columns = st.columns(4)
    metric_labels = [
        ("Vocabulary", "vocabulary"),
        ("Ideas", "ideas"),
        ("Political ideology", "politics"),
    ]
    for column, (label, category) in zip(metric_columns, metric_labels):
        column.metric(label, f"{categories[category].score}/100")
    metric_columns[3].metric("Overall", f"{result['overall']}/100")
    st.caption(
        "What the scores mean: 0 means these terms appear about as rarely as in "
        "19th-century novels such as Pride and Prejudice or Great Expectations. "
        "100 means they appear as often as, or more than, in the strongest "
        "modernist works we tested (for example The Waste Land, Jacob's Room). "
        "Word lists only count words, so they can't tell how a word is used."
    )

    for category, category_themes in CATEGORIES.items():
        category_result = categories[category]
        with st.expander(f"{category.title()} details"):
            st.write(CATEGORY_EXPLANATIONS[category])
            st.write("**Theme counts**")
            st.table(
                [
                    {"Theme": theme, "Count": category_result.theme_counts[theme]}
                    for theme in category_themes
                ]
            )
            st.write("**Top terms**")
            if category_result.top_terms:
                st.write(
                    ", ".join(
                        f"{term[:-1]}…: {count}" if term.endswith("*")
                        else f"{term}: {count}"
                        for term, count in category_result.top_terms
                    )
                )
            else:
                st.write("No listed terms were found.")
            st.write("**Example sentences**")
            if category_result.example_sentences:
                for example in category_result.example_sentences:
                    st.markdown(
                        f"- {_highlight_sentence(example['sentence'], example['terms'])}",
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No example sentences were found.")


def _show_kev_results(result):
    st.subheader("Kev's reading of one passage (about 1,500 words)")
    st.caption(
        "Each percentage is Kev's average answer on a 4-step scale "
        "(Not present → Very strong), so 0% means 'not present' and "
        "100% means 'very strong'."
    )
    for question_id, answer in result["ideas"].items():
        label = question_id.replace("_", " ").title()
        st.write(f"**{label}: {answer['percent']}%**")
        st.progress(answer["percent"] / 100)
        st.caption(
            f"Most likely level: {answer['top_level']} "
            f"({answer['top_probability']:.0%} chance)"
        )
    st.write(f"**Ideas score:** {result['ideas_score']}%")

    politics = result["politics"]
    st.write("**Political idea**")
    st.write(
        f"{politics['idea']['description']} "
        f"({politics['idea']['probability']:.0%} chance)"
    )
    strength = politics["strength"]
    st.write(f"**Political strength:** {strength['percent']}%")
    st.progress(strength["percent"] / 100)
    st.caption(
        f"Most likely level: {strength['top_level']} "
        f"({strength['top_probability']:.0%} chance)"
    )
    with st.expander("Show Kev's raw response JSON"):
        st.json(result["raw"])


def main():
    st.set_page_config(page_title="Modernism Feature Detector", page_icon="📚")
    server_key = _server_kev_key()
    hosted_mode = server_key is not None
    desktop_mode = os.getenv("MODERNISM_DESKTOP") == "1"
    if hosted_mode:
        for state_key in (
            "kev_key_input",
            "remember_kev_key",
            "kev_connection_key",
            "kev_connection_info",
            "kev_connection_error",
            "forget_saved_key_requested",
        ):
            st.session_state.pop(state_key, None)
    elif desktop_mode:
        if st.session_state.pop("forget_saved_key_requested", False):
            key_store.forget_key()
            st.session_state["kev_key_input"] = ""
            st.session_state["remember_kev_key"] = False
            st.session_state["kev_connection_key"] = ""
            st.session_state["kev_connection_ok"] = False
            st.session_state.pop("kev_connection_info", None)
            st.session_state.pop("kev_connection_error", None)

        if "kev_key_input" not in st.session_state:
            st.session_state["kev_key_input"] = key_store.load_key()
        if "remember_kev_key" not in st.session_state:
            st.session_state["remember_kev_key"] = bool(key_store.load_key())
    else:
        st.session_state.pop("remember_kev_key", None)
        st.session_state.pop("forget_saved_key_requested", None)
        if "kev_key_input" not in st.session_state:
            st.session_state["kev_key_input"] = ""

    st.title("Modernism Feature Detector")
    st.info(DISCLAIMER)

    with st.sidebar:
        st.header("Kev (AI analysis)")
        if hosted_mode:
            st.caption("Kev is connected for everyone on this site — no key needed.")
            key = server_key
        elif desktop_mode:
            key = st.text_input(
                "Kev key",
                type="password",
                key="kev_key_input",
            )
            remember_key = st.checkbox(
                "Remember my key on this computer",
                key="remember_kev_key",
            )
            st.caption("Saved only on this computer, outside the app folder.")
            if remember_key and key.startswith("kevdemo_"):
                key_store.save_key(key)
            elif not remember_key:
                key_store.forget_key()
            if st.button("Forget saved key"):
                st.session_state["forget_saved_key_requested"] = True
                st.rerun()
        else:
            key = st.text_input(
                "Kev key",
                type="password",
                key="kev_key_input",
            )
            st.caption(
                "Your key is only kept in this browser tab and is never saved on the server."
            )

        model = st.selectbox(
            "Kev model",
            MODELS,
            index=MODELS.index(DEFAULT_MODEL),
        )
        check_button = st.button("Check connection")
        position = st.radio(
            "Passage position",
            ["Beginning", "Middle", "End"],
            horizontal=True,
        )

        if check_button:
            if hosted_mode:
                try:
                    connection_ok, _ = check_connection(server_key)
                except Exception:
                    connection_ok = False
                if connection_ok:
                    st.success("Kev connection successful.")
                else:
                    st.error(
                        "Kev connection failed. Please check the server-side key."
                    )
            else:
                if not key:
                    st.session_state["kev_connection_key"] = ""
                    st.session_state["kev_connection_ok"] = False
                    st.session_state["kev_connection_error"] = "Please enter a Kev key."
                else:
                    ok, info = check_connection(key)
                    st.session_state["kev_connection_key"] = key
                    st.session_state["kev_connection_ok"] = ok
                    if ok:
                        st.session_state["kev_connection_info"] = info
                        st.session_state.pop("kev_connection_error", None)
                    else:
                        st.session_state["kev_connection_error"] = info
                        st.session_state.pop("kev_connection_info", None)

        if hosted_mode:
            kev_ready = True
        else:
            key_was_checked = (
                st.session_state.get("kev_connection_key") == key and bool(key)
            )
            connected = key_was_checked and st.session_state.get(
                "kev_connection_ok", False
            )
            kev_ready = key.startswith("kevdemo_") and not (
                key_was_checked and not st.session_state.get("kev_connection_ok")
            )
            if not key:
                st.warning("Kev not connected")
                st.markdown(
                    f"Get a personal key from the Kev workshop site: "
                    f"[Request a key]({KEV_API_BASE}), then paste it here."
                )
            elif connected:
                st.success("Kev connection successful.")
                with st.expander("Show /v1/me response JSON"):
                    st.json(st.session_state["kev_connection_info"])
            elif key_was_checked:
                st.error(
                    st.session_state.get(
                        "kev_connection_error", "Kev connection failed."
                    )
                )
            elif key.startswith("kevdemo_"):
                st.info("Kev key entered (not checked yet)")
            else:
                st.warning("Kev keys start with 'kevdemo_'.")

    paste_tab, upload_tab = st.tabs(["Paste text", "Upload file"])
    with paste_tab:
        pasted_text = st.text_area(
            "Paste an English text to analyze",
            height=250,
            key="pasted_text",
        )
    with upload_tab:
        uploaded_file = st.file_uploader(
            "Choose a .txt or .pdf file",
            type=["txt", "pdf"],
        )

    if st.button("Analyze", type="primary"):
        try:
            if uploaded_file is not None:
                source_text = read_uploaded_file(
                    uploaded_file.name, uploaded_file.getvalue()
                )
            else:
                source_text = pasted_text
            text = strip_gutenberg_boilerplate(source_text)
            word_results = analyze_text(text)
            analysis = {
                "text": text,
                "word_list": word_results,
                "kev": None,
                "kev_error": None,
            }
            if kev_ready:
                excerpt = pick_excerpt(text, position.lower())
                try:
                    with st.spinner(
                        "Kev may take 3–4 minutes to wake up after a quiet period..."
                    ):
                        kev_result = analyze_with_kev(excerpt, key, model)
                    analysis["kev"] = (
                        _redact_server_key(kev_result, server_key)
                        if hosted_mode
                        else kev_result
                    )
                except KevError as error:
                    analysis["kev_error"] = (
                        "Kev could not analyze this passage. Please try again later."
                        if hosted_mode
                        else str(error)
                    )
                except Exception:
                    if not hosted_mode:
                        raise
                    analysis["kev_error"] = (
                        "Kev could not analyze this passage. Please try again later."
                    )
            st.session_state["analysis"] = analysis
        except ValueError as error:
            st.error(str(error))
    st.caption(
        "If you have both pasted text and uploaded a file, the uploaded file is analyzed."
    )

    analysis = st.session_state.get("analysis")
    if analysis:
        _show_word_list_results(analysis["word_list"])
        if not kev_ready:
            st.info("Kev not connected — showing word-list results only.")
        elif analysis["kev_error"]:
            st.error(analysis["kev_error"])
        elif analysis["kev"]:
            _show_kev_results(analysis["kev"])


if __name__ == "__main__":
    main()
