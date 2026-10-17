"""Questions sent to Kev (POST /v1/systemone). Kev answers each one on its own.

Score questions use LEVELS, so Kev returns a score from 0 (first level) to 3 (last level).
"""

LEVELS = ["Not present", "A little", "Clearly present", "Very strong"]

IDEA_QUESTIONS = {
    "stream_of_consciousness": "How much does the passage present a character's thoughts as a flowing stream of consciousness or interior monologue?",
    "fragmentation": "How fragmented or non-linear is the writing (broken sentences, sudden jumps in time, place or speaker)?",
    "alienation": "How strongly does the passage express alienation, isolation or loneliness of the individual in modern life?",
    "loss_of_meaning": "How strongly does the passage express loss of faith, disillusionment, or a sense that life lacks meaning?",
    "subjective_time": "How much does the passage focus on memory, subjective time and inner experience rather than outward plot?",
    "modern_city_and_machines": "How much does the passage focus on the modern city, technology or machines?",
    "formal_experiment": "How strongly does the passage experiment with form or break literary conventions (unusual structure, mixed styles, wordplay, unusual punctuation)?",
}

POLITICS_STRENGTH_QUESTION = "How strongly does the passage engage with political ideas or ideology?"

POLITICS_CHOICE_QUESTION = "Which political idea is most present in the passage?"
POLITICS_OPTIONS = {
    "none": "No clear political idea",
    "socialism_class": "Socialism, communism, class struggle or workers' rights",
    "anarchism": "Anarchism or rejection of all government",
    "feminism": "Women's rights, suffrage or feminism",
    "nationalism_empire": "Nationalism, empire, colonialism or independence movements",
    "anti_war": "Anti-war feeling, pacifism or criticism of militarism",
    "authoritarianism": "Fascism, dictatorship or authoritarian rule",
}


def build_questions():
    questions = {
        qid: {"type": "score", "instructions": text, "criteria": LEVELS}
        for qid, text in IDEA_QUESTIONS.items()
    }
    questions["political_strength"] = {
        "type": "score",
        "instructions": POLITICS_STRENGTH_QUESTION,
        "criteria": LEVELS,
    }
    questions["political_idea"] = {
        "type": "choice",
        "instructions": POLITICS_CHOICE_QUESTION,
        "criteria": POLITICS_OPTIONS,
    }
    return questions
