import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.runpod.ai/v2/b1dd8hy2hqo1nb/openai/v1",
    api_key=os.environ["RUNPOD_API_KEY"],
)

completion = client.chat.completions.create(
    model="glm-5.3",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Runpod?"},
    ],
    max_tokens=4096,
    temperature=1,
    reasoning_effort="low",
)

print(completion.choices[0].message.content)
