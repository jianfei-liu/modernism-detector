"""Small client for the Kev reading-analysis API."""

import math

import requests

from modernism.kev_questions import (
    IDEA_QUESTIONS,
    LEVELS,
    POLITICS_OPTIONS,
    build_questions,
)

KEV_API_BASE = "https://yohann-60613--kev-demo.modal.run"
MODELS = ["kev-9b", "kev-27b"]
DEFAULT_MODEL = "kev-9b"
_COLD_START_HINT = (
    "Kev may be waking up after a quiet period. Please try again in a few minutes."
)


class KevError(Exception):
    """A readable error returned when Kev cannot be reached or parsed."""


def _request_error(error):
    if isinstance(error, (requests.Timeout, requests.ConnectionError)):
        return KevError(f"Could not connect to Kev. {_COLD_START_HINT}")
    return KevError(f"Could not connect to Kev: {error}")


def _response_detail(response):
    try:
        body = response.json()
    except ValueError:
        body = response.text
    if isinstance(body, dict):
        return body.get("detail", body.get("error", body))
    return body


def _json_response(response, action):
    if not 200 <= response.status_code < 300:
        detail = _response_detail(response)
        raise KevError(f"Kev error {response.status_code}: {detail}")
    try:
        return response.json()
    except ValueError as error:
        raise KevError(f"Kev returned invalid JSON while {action}.") from error


def check_connection(key):
    """Check a Kev key and return (success, raw response JSON or error text)."""
    if not key or not key.startswith("kevdemo_"):
        return False, "Kev keys start with 'kevdemo_'."
    try:
        response = requests.get(
            f"{KEV_API_BASE}/v1/me",
            headers={"authorization": f"Bearer {key}"},
            timeout=30,
        )
    except requests.RequestException as error:
        return False, str(_request_error(error))
    try:
        info = _json_response(response, "checking the connection")
    except KevError as error:
        return False, str(error)
    return True, info


def pick_excerpt(text, position, max_words=1500):
    """Choose a beginning, middle, or ending window of up to max_words."""
    if position not in {"beginning", "middle", "end"}:
        raise ValueError("Position must be beginning, middle, or end.")
    words = text.split()
    window_size = min(len(words), max(0, max_words))
    if position == "beginning":
        start = 0
    elif position == "middle":
        start = max(0, (len(words) - window_size) // 2)
    else:
        start = len(words) - window_size
    return " ".join(words[start : start + window_size])


def _as_number(value, field_name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise KevError(f"Kev returned an invalid {field_name}.")
    number = float(value)
    if not math.isfinite(number):
        raise KevError(f"Kev returned an invalid {field_name}.")
    return number


def _parse_score(answer, question_id):
    if not isinstance(answer, dict) or answer.get("type") != "score":
        raise KevError(f"Kev's answer for '{question_id}' is missing or has the wrong type.")
    required = {"score", "probabilities"}
    if not required.issubset(answer):
        raise KevError(f"Kev's answer for '{question_id}' is missing required fields.")
    score = _as_number(answer["score"], f"score for '{question_id}'")
    if not 0 <= score <= 3:
        raise KevError(f"Kev's score for '{question_id}' must be from 0 to 3.")
    probabilities = answer["probabilities"]
    if not isinstance(probabilities, dict) or not probabilities:
        raise KevError(f"Kev's probabilities for '{question_id}' are missing.")
    legend = answer.get("legend") or {}
    if not isinstance(legend, dict):
        raise KevError(f"Kev's legend for '{question_id}' is invalid.")
    probability_values = {
        level: _as_number(value, f"probability for '{question_id}'")
        for level, value in probabilities.items()
    }
    confidence = answer.get("confidence")
    if confidence is None:
        confidence = max(probability_values.values())
    confidence = _as_number(confidence, f"confidence for '{question_id}'")
    top_key = max(probability_values, key=probability_values.get)
    top_level = legend.get(top_key)
    if top_level is None:
        try:
            level_index = int(top_key)
            top_level = LEVELS[level_index] if 0 <= level_index < len(LEVELS) else str(top_key)
        except (ValueError, TypeError):
            top_level = str(top_key)
    if not isinstance(top_level, str):
        top_level = str(top_level)
    return {
        "percent": round(score / 3 * 100),
        "top_level": top_level,
        "top_probability": probability_values[top_key],
        "confidence": confidence,
    }


def _parse_choice(answer):
    if not isinstance(answer, dict) or answer.get("type") != "choice":
        raise KevError("Kev's answer for 'political_idea' is missing or has the wrong type.")
    if not {"choice", "probabilities"}.issubset(answer):
        raise KevError("Kev's political-idea answer is missing required fields.")
    choice = answer["choice"]
    probabilities = answer["probabilities"]
    if (
        choice not in POLITICS_OPTIONS
        or not isinstance(probabilities, dict)
        or not probabilities
    ):
        raise KevError("Kev returned an unknown political idea or invalid probabilities.")
    if choice not in probabilities:
        raise KevError("Kev's probability for the selected political idea is missing.")
    probability_values = {
        name: _as_number(value, "political-idea probability")
        for name, value in probabilities.items()
    }
    probability = probability_values[choice]
    confidence = answer.get("confidence")
    if confidence is None:
        confidence = max(probability_values.values())
    confidence = _as_number(confidence, "political-idea confidence")
    return {
        "choice": choice,
        "description": POLITICS_OPTIONS[choice],
        "probability": probability,
        "confidence": confidence,
    }


def _parse_results(data):
    if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
        raise KevError("Kev's response is missing the 'answers' object.")
    answers = data["answers"]
    ideas = {
        question_id: _parse_score(answers.get(question_id), question_id)
        for question_id in IDEA_QUESTIONS
    }
    political_strength = _parse_score(
        answers.get("political_strength"), "political_strength"
    )
    political_idea = _parse_choice(answers.get("political_idea"))
    return {
        "ideas": ideas,
        "ideas_score": round(
            sum(result["percent"] for result in ideas.values()) / len(ideas)
        ),
        "politics": {
            "strength": political_strength,
            "idea": political_idea,
        },
    }


def analyze_with_kev(excerpt, key, model):
    """Ask Kev to read one excerpt and return parsed results plus raw JSON."""
    if not key or not key.startswith("kevdemo_"):
        raise KevError("Kev keys start with 'kevdemo_'.")
    if model not in MODELS:
        raise KevError("Choose kev-9b or kev-27b.")
    try:
        response = requests.post(
            f"{KEV_API_BASE}/v1/systemone",
            headers={"authorization": f"Bearer {key}"},
            json={
                "state": excerpt,
                "model": model,
                "questions": build_questions(),
            },
            timeout=300,
        )
    except requests.RequestException as error:
        raise _request_error(error) from error
    raw = _json_response(response, "analyzing the passage")
    results = _parse_results(raw)
    results["raw"] = raw
    return results
