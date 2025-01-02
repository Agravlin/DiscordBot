import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
]

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8",
    "de-DE,de;q=0.7",
    "fr-FR,fr;q=0.6",
    "es-ES,es;q=0.5",
]

REFERERS = [
    "https://www.youtube.com/",
    "https://www.google.com/",
    "https://www.youtube.com/results?search_query=music",
    "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]

used_combinations = set()

def generate_random_headers() -> dict[str, str]:
    global used_combinations

    while True:
        user_agent = random.choice(USER_AGENTS)
        accept_language = random.choice(ACCEPT_LANGUAGES)
        referer = random.choice(REFERERS)

        combination = (user_agent, accept_language, referer)

        if combination not in used_combinations:
            used_combinations.add(combination)

            if len(used_combinations) >= len(USER_AGENTS) * len(ACCEPT_LANGUAGES) * len(REFERERS):
                used_combinations.clear()

            return {
                "User-Agent": user_agent,
                "Accept-Language": accept_language,
                "Referer": referer,
            }

if __name__ == "__main__":
    for _ in range(5):
        random_headers = generate_random_headers()
        print(random_headers)
