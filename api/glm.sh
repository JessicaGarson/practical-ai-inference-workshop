#!/usr/bin/env bash
# Submit a GLM-5.3 job to the Runpod Public Endpoint, then poll until it finishes.
# Needs RUNPOD_API_KEY and jq.
BASE_URL="https://api.runpod.ai/v2/b1dd8hy2hqo1nb"

RUN_RESPONSE=$(curl --silent --show-error --fail \
  --request POST \
  --url "$BASE_URL/run" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $RUNPOD_API_KEY" \
  --data '{
    "input": {
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Runpod?"}
      ],
      "sampling_params": {
        "max_tokens": 4096,
        "temperature": 1
      },
      "model": "glm-5.3",
      "reasoning_effort": "low"
    }
  }')

JOB_ID=$(printf '%s' "$RUN_RESPONSE" | jq --raw-output '.id // empty')

if [ -z "$JOB_ID" ]; then
  printf 'The job submission did not return an ID:\n%s\n' "$RUN_RESPONSE" >&2
  exit 1
fi

printf 'Job submitted: %s\n' "$JOB_ID"

while true; do
  STATUS_RESPONSE=$(curl --silent --show-error --fail \
    --request GET \
    --url "$BASE_URL/status/$JOB_ID" \
    --header "Authorization: Bearer $RUNPOD_API_KEY")

  STATUS=$(printf '%s' "$STATUS_RESPONSE" | jq --raw-output '.status')

  case "$STATUS" in
    COMPLETED)
      printf '%s' "$STATUS_RESPONSE" | jq '.output'
      break
      ;;
    FAILED|CANCELLED|TIMED_OUT)
      printf 'Job ended with status %s:\n%s\n' \
        "$STATUS" "$STATUS_RESPONSE" >&2
      exit 1
      ;;
    *)
      printf 'Status: %s. Waiting...\n' "$STATUS"
      sleep 2
      ;;
  esac
done
