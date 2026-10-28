import os
import sys
import time

import requests

API_KEY = os.environ.get("RUNPOD_API_KEY")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
if not API_KEY or not ENDPOINT_ID:
    sys.exit("Set RUNPOD_API_KEY and ENDPOINT_ID first.")

BASE_URL = f"https://{ENDPOINT_ID}.api.runpod.ai"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def wait_until_ready(max_wait=1200):
    """Poll /v1/version until a worker is ready to take requests."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            # The worker only answers /v1/version once the model is loaded.
            # If no worker is ready, Runpod returns an error after about
            # 2 minutes, so each check is short and we keep polling.
            r = requests.get(f"{BASE_URL}/v1/version", headers=HEADERS, timeout=130)
            if r.status_code == 200:
                print("Worker ready.")
                return
            if r.status_code in (401, 403):
                sys.exit(f"HTTP {r.status_code}: check RUNPOD_API_KEY and its endpoint permissions.")
            print(f"Not ready yet (HTTP {r.status_code}): {r.text[:200]}")
        except requests.RequestException as e:
            print(f"Not ready yet: {e}")
        time.sleep(10)
    sys.exit("No worker became ready. Check the endpoint's logs in the console.")


def ask(state, questions, attempts=3):
    """Send text plus typed questions to OpenJev and return the answers."""
    body = {"model": "openjev", "state": state, "questions": questions}
    for attempt in range(1, attempts + 1):
        try:
            r = requests.post(
                f"{BASE_URL}/v1/systemone", headers=HEADERS, json=body, timeout=60
            )
            r.raise_for_status()
            return r.json()["answers"]
        except requests.RequestException as e:
            # Covers timeouts, HTTP errors, and dropped connections. If the
            # model server fails, it closes the connection with no JSON body,
            # which raises ConnectionError rather than Timeout.
            print(f"Attempt {attempt} failed: {e}")
            if attempt < attempts:
                time.sleep(10)
    sys.exit(f"No answer after {attempts} attempts. Check the endpoint's logs.")


review = (
    "Review: I bought these headphones for my commute. The sound is great "
    "and the noise cancelling works well on the train, but the battery "
    "barely lasts a day and they hurt my ears after an hour."
)

questions = {
    "sentiment": {
        "type": "choice",
        "instructions": "What is the overall tone of this review?",
        "criteria": {"positive": None, "mixed": None, "negative": None},
    },
    "recommends": {
        "type": "noul",
        "instructions": "Does the reviewer say they would recommend this product?",
    },
    "rating": {
        "type": "score",
        "instructions": "How many stars would this reviewer likely give?",
        "criteria": ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"],
    },
}

wait_until_ready()
answers = ask(review, questions)

# choice: the option the model picked
sentiment = answers["sentiment"]
print(f"Sentiment: {sentiment['choice']} (confidence {sentiment['confidence']})")

# noul: the probability that the answer is yes
p_yes = answers["recommends"]["noul"]
print(f"Recommends: {'yes' if p_yes >= 0.5 else 'no'} (probability of yes {p_yes})")

# score: a position on the scale, counted from 0; legend maps positions to labels
rating = answers["rating"]
label = rating["legend"][str(round(rating["score"]))]
print(f"Rating: {label} (score {rating['score']}, confidence {rating['confidence']})")
