import random
import time

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
CONNECTION_OPTIONS = ["keep-alive", "close"]
CACHE_CONTROL_OPTIONS = ["no-cache", "max-age=0"]
X_FORWARDED_FOR_OPTIONS = [
    "192.168.1.1",
    "203.0.113.5",
    "198.51.100.3",
]
ACCEPT_OPTIONS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "application/json, text/javascript, */*;q=0.01",
]
ACCEPT_ENCODING_OPTIONS = ["gzip, deflate, br", "gzip, deflate"]
UPGRADE_INSECURE_REQUESTS_OPTIONS = ["1"]

used_combinations = set()

def calculate_combination_count() -> int:
    return (
        len(USER_AGENTS)
        * len(ACCEPT_LANGUAGES)
        * len(REFERERS)
        * len(CONNECTION_OPTIONS)
        * len(CACHE_CONTROL_OPTIONS)
        * len(X_FORWARDED_FOR_OPTIONS)
        * len(ACCEPT_OPTIONS)
        * len(ACCEPT_ENCODING_OPTIONS)
        * len(UPGRADE_INSECURE_REQUESTS_OPTIONS)
    )

def generate_random_headers() -> dict[str, str]:
    global used_combinations

    while True:
        user_agent = random.choice(USER_AGENTS)
        accept_language = random.choice(ACCEPT_LANGUAGES)
        referer = random.choice(REFERERS)
        connection = random.choice(CONNECTION_OPTIONS)
        cache_control = random.choice(CACHE_CONTROL_OPTIONS)
        x_forwarded_for = random.choice(X_FORWARDED_FOR_OPTIONS)
        accept = random.choice(ACCEPT_OPTIONS)
        accept_encoding = random.choice(ACCEPT_ENCODING_OPTIONS)
        upgrade_insecure_requests = random.choice(UPGRADE_INSECURE_REQUESTS_OPTIONS)

        combination = (
            user_agent,
            accept_language,
            referer,
            connection,
            cache_control,
            x_forwarded_for,
            accept,
            accept_encoding,
            upgrade_insecure_requests,
        )

        if combination not in used_combinations:
            used_combinations.add(combination)

            if len(used_combinations) >= calculate_combination_count():
                used_combinations.clear()

            time.sleep(random.uniform(0.1, 0.2))

            return {
                "User-Agent": user_agent,
                "Accept-Language": accept_language,
                "Referer": referer,
                "Connection": connection,
                "Cache-Control": cache_control,
                "X-Forwarded-For": x_forwarded_for,
                "Accept": accept,
                "Accept-Encoding": accept_encoding,
                "Upgrade-Insecure-Requests": upgrade_insecure_requests,
            }

if __name__ == "__main__":
    for _ in range(5):
        random_headers = generate_random_headers()
        print(random_headers)
