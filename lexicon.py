"""Word lists used to spot literary modernism (roughly 1890-1940).

Each category has a few themes, and each theme has a list of terms.
A term ending in "*" matches any word that starts with it
(for example "alienat*" matches "alienation" and "alienated").
Terms with spaces are matched as whole phrases.
"""

VOCABULARY = {
    "Machines and new technology": [
        "machine*", "machinery", "motor*", "automobile*", "aeroplane*", "airplane*", "telephone*", "telegra*", "gramophone*", "phonograph*", "cinema*", "electric*", "dynamo*", "wireless", "typewriter*", "camera*", "radio", "tram", "trams", "tramcar*", "omnibus*",
    ],
    "The modern city": [
        "metropol*", "skyscraper*", "traffic", "factory", "factories", "suburb*", "cosmopolit*", "neon", "billboard*", "advertisement*", "department store*",
    ],
    "The mind and new psychology": [
        "subconscious*", "psyche", "psycholog*", "neuros*", "neurotic*", "hysteri*", "ego", "libido", "obsess*", "reverie*", "introspect*",
    ],
    "Modernist mood words": [
        "ennui", "flux", "flicker*", "fleeting", "ephemeral", "epiphan*", "vortex", "kaleidoscop*", "dissonan*", "jazz", "staccato", "monotonous", "monotony", "automaton*", "sterile",
    ],
}

IDEAS = {
    "Alienation and isolation": [
        "alienat*", "estrang*", "anonym*", "outsider*",
    ],
    "Fragmentation and chaos": [
        "fragment*", "shatter*", "chaos", "chaotic", "disintegrat*", "splinter*", "incoherent*", "disjoint*",
    ],
    "Time, memory and the inner life": [
        "stream of consciousness", "inner life", "duration", "subjectiv*",
    ],
    "Loss of faith and meaning": [
        "meaningless*", "futil*", "void", "nothingness", "abyss", "nihil*", "waste land", "wasteland", "disillusion*", "god is dead", "emptiness",
    ],
    "War and trauma": [
        "trench*", "shell-shock*", "shell shock*", "shellshock*", "armistice", "machine-gun*", "machine gun*", "barbed wire", "gas mask*", "casualt*", "the great war",
    ],
    "Breaking with tradition": [
        "make it new", "avant-garde", "bohemian*", "victorian*", "old-fashioned",
    ],
}

POLITICS = {
    "Socialism and class struggle": [
        "socialis*", "communis*", "marxis*", "bolshevi*", "proletari*", "bourgeois*", "capitalis*", "working class", "working-class", "class struggle", "trade union*", "labour party", "strikers", "exploitation",
    ],
    "Anarchism": [
        "anarchis*", "anarchy", "anarchic*", "nihilist*", "dynamiter*",
    ],
    "Women's rights and feminism": [
        "suffrag*", "feminis*", "votes for women", "women's rights", "new woman", "emancipat*", "a room of one's own",
    ],
    "Nationalism, empire and fascism": [
        "nationalis*", "imperialis*", "colonial*", "colonies", "fascis*", "home rule", "sinn fein", "fatherland", "propaganda",
    ],
    "War, peace and the state": [
        "pacifis*", "militaris*", "conscript*", "democra*", "dictator*", "totalitarian*",
    ],
}

CATEGORIES = {
    "vocabulary": VOCABULARY,
    "ideas": IDEAS,
    "politics": POLITICS,
}
