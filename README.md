# Practical AI Inference: From API to Serverless

Workshop code for the talk *Practical AI Inference: From API to Serverless*.

| Folder | What it shows |
| --- | --- |
| [api/](api) | Call a hosted model, GLM-5.3, through a Runpod Public Endpoint. No GPUs to manage. |
| [serverless/](serverless) | Deploy your own model, OpenJev, as a Runpod Serverless endpoint with one agent prompt. |

**Prefer a notebook?** [workshop.ipynb](workshop.ipynb) has the same concepts and code in one place. Open it in Jupyter, or upload it to [Google Colab](https://colab.research.google.com/). It's optional: everything below works from the terminal too.

## Key concepts

**Inference** is using a trained model to produce an output: you send it an input (a prompt, a review, an image) and it returns a result (an answer, a score, a picture). Training builds the model; inference is everything you do with it afterward, and it's what you pay for each time your app calls a model.

Runpod gives you three ways to run inference, from least to most control:

| | Public Endpoint | Serverless | Pod |
| --- | --- | --- | --- |
| **What it is** | A model Runpod already hosts. You call it with your API key. | Your own container on autoscaling GPU workers behind a URL. Workers run only while there's work. | A GPU or CPU machine you rent and manage directly: start, stop, SSH in, expose ports. |
| **You deploy** | Nothing | A container image and endpoint settings | A container image |
| **You pay** | Per output (for example, per million tokens) | Per second while a worker runs, including cold starts | Per hour while the pod runs, plus storage while stopped |
| **Good for** | Trying popular models fast | Your own or custom models with bursty traffic | Development, experiments, and always-on apps |
| **In this workshop** | Part 1: GLM-5.3 | Part 2: OpenJev | Hollow Manor's web server |

A Serverless endpoint comes in two types, and you choose when you create it:

- **Queue**: requests become jobs. You send them to `/run` or `/runsync` and check `/status`, and jobs wait in a queue when workers are busy. Public Endpoints use this same job API, which is why `api/glm.sh` polls `/status`.
- **Load balancer**: requests go straight to the worker's own HTTP server, like `/v1/systemone` in Part 2. There's no queue, so requests are dropped when every worker is busy.

## Setup

Create a [Runpod API key](https://docs.runpod.io/get-started/credentials) and store it in your environment:

```bash
export RUNPOD_API_KEY="rpa_yourapikey"
```

Install the Python dependencies (Python 3.9 or newer):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The curl scripts also need [jq](https://jqlang.org/).

## Demo: Murder at Hollow Manor

**[Murder at Hollow Manor](https://github.com/JessicaGarson/hollow-manor-mystery)** is a Halloween murder mystery where every suspect is an LLM served through a Runpod API. **[▶ Play it here](https://vq9kfsopdoe2m2-8666.proxy.runpod.net)**. Its code lives in that repository, not this one.

## Part 1: From API (GLM-5.3 on a Public Endpoint)

GLM-5.3 is a Z.ai model that's strong at writing code and long, multi-step tasks. It runs on Runpod's Public Endpoints, so you pay per token: $0.77 per 1M input tokens ($0.143 cached) and $2.42 per 1M output tokens. You can also try it without code in the Playground: go to **The Hub**, then **Public Endpoints**, then **GLM-5.3**.

**With curl.** The request goes to `/run`, which accepts the job right away and returns an ID. The script then polls `/status/{job_id}` every two seconds until the job is `COMPLETED`, and prints the `output`:

```bash
bash api/glm.sh
```

The request uses OpenAI-style `messages`. `sampling_params` sets `max_tokens` and `temperature`, and `reasoning_effort` controls how much the model thinks before answering. The example uses `low` to keep responses fast.

**With Python.** The endpoint is OpenAI-compatible, so the OpenAI SDK skips the submit-and-poll step and returns the completion in one call:

```bash
python api/glm.py
```

The same base URL, `https://api.runpod.ai/v2/b1dd8hy2hqo1nb/openai/v1`, works with any tool that accepts a custom OpenAI base URL. To stream tokens as they arrive, add `stream=True` and iterate over the chunks.

## Part 2: To Serverless (OpenJev on your own endpoint)

[OpenJev](https://huggingface.co/openjev/openjev) doesn't chat. It answers typed questions about text (yes/no, multiple choice, or a score) and returns probabilities your code can use. In this part, you deploy it to your own Serverless endpoint by giving one prompt to an AI agent.

### 1. Connect the Runpod MCP server

Connect your agent (for example, Claude Code) to the [Runpod MCP server](https://github.com/runpod/runpod-mcp). If this is your first time, follow [MCP-SETUP.md](MCP-SETUP.md). For Claude Code, it's one command plus a browser sign-in:

```bash
claude mcp add --transport http runpod -s user https://mcp.runpod.io/
```

Then run `/mcp` in Claude Code, sign in, and check that `runpod` shows **Connected**.

### 2. Deploy with the prompt

Paste the prompt in [serverless/prompt.md](serverless/prompt.md) into your agent. The prompt creates a load-balancer endpoint on one H100 80 GB GPU with 0 active workers, so you pay only while a worker is running. The agent reports the hourly price before it creates anything and returns your endpoint URL when it's done.

The first request after deployment triggers a cold start. The worker downloads and loads the model, which takes several minutes and is billed.

### 3. Send a request

Set the endpoint ID the agent gave you:

```bash
export ENDPOINT_ID="your_endpoint_id"
```

**With curl.** This waits for a worker to be ready, then asks whether a reviewer likes the sound quality:

```bash
bash serverless/test.sh
```

```json
{"id": "shim-1790637935267", "model": "openjev-FP8 ...", "answers": {"likes_sound": {"type": "noul", "noul": 0.9801}}, "usage": {"input_tokens": 75, "output_tokens": 0}}
```

`noul` is the probability that the answer is yes. In this example, the model is about 98% confident.

**With Python.** This asks three typed questions about one headphone review in a single request:

```bash
python serverless/openjev_python.py
```

The script prints the sentiment (positive, mixed, or negative), whether the reviewer would recommend the product, and a likely star rating.

### Troubleshooting

- `no workers available` while waiting: the worker is still starting. Let the script keep polling.
- `not allowed for QB API`: the endpoint was created as Queue instead of Load balancer. Create a new endpoint with the correct type.
- `401` or `403`: check your API key and its endpoint permissions.

### Clean up

When you're done, ask your agent to delete the `openjev` endpoint. With 0 active workers, an idle endpoint costs nothing, but deleting it keeps your account tidy.

## Resources

**Blog posts**

- [Getting started with GLM-5.3 with Runpod's public endpoint](https://www.runpod.io/blog/getting-started-glm-5-3-runpod-public-endpoint)
- [How to Deploy OpenJev on Runpod Serverless](https://www.runpod.io/blog/how-to-deploy-openjev-on-runpod-serverless)

**Code**

- [Runpod MCP server](https://github.com/runpod/runpod-mcp): lets an AI agent create and manage Runpod resources
- [runpod/openjev-serverless](https://github.com/runpod/openjev-serverless): companion repository for the OpenJev post
- [Murder at Hollow Manor](https://github.com/JessicaGarson/hollow-manor-mystery): the demo game

**Docs**

- [Public Endpoints](https://docs.runpod.io/public-endpoints/overview)
- [Serverless load balancing](https://docs.runpod.io/serverless/load-balancing/overview)
- [Serverless endpoint settings](https://docs.runpod.io/serverless/endpoints/endpoint-configurations)
- [Serverless pricing](https://docs.runpod.io/serverless/pricing)
- [Managing Pods](https://docs.runpod.io/pods/manage-pods)
- [API keys](https://docs.runpod.io/get-started/credentials)

## Credits and licenses

Part 1 comes from the Runpod blog post [Getting started with GLM-5.3 with Runpod's public endpoint](https://www.runpod.io/blog/getting-started-glm-5-3-runpod-public-endpoint).

Part 2 comes from the Runpod blog post [How to Deploy OpenJev on Runpod Serverless](https://www.runpod.io/blog/how-to-deploy-openjev-on-runpod-serverless) and its companion repository, [runpod/openjev-serverless](https://github.com/runpod/openjev-serverless). It uses [Brandon Bondig's openjev-worker](https://github.com/brandonbondig/openjev-worker) image.

The code is licensed under Apache-2.0; see [LICENSE](LICENSE). The OpenJev model weights are licensed separately under **CC BY-NC 4.0**, which allows non-commercial use with attribution. For commercial use, contact the model authors on the [model card](https://huggingface.co/openjev/openjev).
