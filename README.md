# Practical AI Inference: From API to Serverless

Workshop code for the talk *Practical AI Inference: From API to Serverless*.

## From API: Murder at Hollow Manor

The talk opens with **[Murder at Hollow Manor](https://github.com/JessicaGarson/hollow-manor-mystery)**, a Halloween murder mystery where every suspect is an LLM served through a Runpod API. **[▶ Play it here](https://vq9kfsopdoe2m2-8666.proxy.runpod.net)**. Its code lives in that repository, not this one.

## To Serverless: deploy OpenJev

In the workshop, you deploy [OpenJev](https://huggingface.co/openjev/openjev) as a Runpod Serverless endpoint by giving one prompt to an AI agent. OpenJev doesn't chat. It answers typed questions about text (yes/no, multiple choice, or a score) and returns probabilities your code can use.

### 1. Connect the Runpod MCP server

Connect your agent (for example, Claude Code) to the [Runpod MCP server](https://github.com/runpod/runpod-mcp).

### 2. Deploy with the prompt

Paste the prompt in [prompt.md](prompt.md) into your agent. The prompt creates a load-balancer endpoint on one H100 80 GB GPU with 0 active workers, so you pay only while a worker is running. The agent reports the hourly price before it creates anything and returns your endpoint URL when it's done.

The first request after deployment triggers a cold start. The worker downloads and loads the model, which takes several minutes and is billed.

### 3. Send a request

Set your API key and the endpoint ID the agent gave you:

```bash
export RUNPOD_API_KEY="rpa_yourapikey"
export ENDPOINT_ID="your_endpoint_id"
```

**With curl.** This waits for a worker to be ready, then asks whether a reviewer likes the sound quality:

```bash
bash examples/test.sh
```

```json
{"id": "shim-1790637935267", "model": "openjev-FP8 ...", "answers": {"likes_sound": {"type": "noul", "noul": 0.9801}}, "usage": {"input_tokens": 75, "output_tokens": 0}}
```

`noul` is the probability that the answer is yes. In this example, the model is about 98% confident.

**With Python.** This asks three typed questions about one headphone review in a single request:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python examples/review.py
```

The script prints the sentiment (positive, mixed, or negative), whether the reviewer would recommend the product, and a likely star rating.

### Troubleshooting

- `no workers available` while waiting: the worker is still starting. Let the script keep polling.
- `not allowed for QB API`: the endpoint was created as Queue instead of Load balancer. Create a new endpoint with the correct type.
- `401` or `403`: check your API key and its endpoint permissions.

### Clean up

When you're done, ask your agent to delete the `openjev` endpoint. With 0 active workers, an idle endpoint costs nothing, but deleting it keeps your account tidy.

## Credits and licenses

The prompt and code come from the Runpod blog post [How to Deploy OpenJev on Runpod Serverless](https://www.runpod.io/blog/how-to-deploy-openjev-on-runpod-serverless) and its companion repository, [runpod/openjev-serverless](https://github.com/runpod/openjev-serverless). They use [Brandon Bondig's openjev-worker](https://github.com/brandonbondig/openjev-worker) image. The code is licensed under Apache-2.0; see [LICENSE](LICENSE).

The OpenJev model weights are licensed separately under **CC BY-NC 4.0**, which allows non-commercial use with attribution. For commercial use, contact the model authors on the [model card](https://huggingface.co/openjev/openjev).
