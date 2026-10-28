# Deploy prompt

Paste this into an agent connected to the [Runpod MCP server](https://github.com/runpod/runpod-mcp):

```text
Deploy OpenJev on Runpod Serverless using the image ghcr.io/brandonbondig/openjev-worker@sha256:1f95a727a3de6d0a29808f59d89b49424f4d4bc78c871f5080052abb4105424d (use this exact digest, not the latest tag). Create a load-balancer endpoint (not queue-based) named openjev with:

- One H100 80 GB per worker (OpenJev's measured setup is one 80 GB GPU with native FP8, so no A100 fallback). Look up the H100 GPU pool ID from the Runpod catalog rather than guessing it.
- Environment variables PORT=3000, PORT_HEALTH=3001 and HEALTH_CHECK_PATH=/
- A 60 GB container disk
- Expose HTTP ports 3000 and 3001 in the container configuration
- Active workers 0, maximum workers 1, and an idle timeout of 300 seconds
- Request count scaling (load balancer endpoints don't support queue delay scaling)
- FlashBoot on (the API defaults it to off, unlike the console)

Tell me the hourly price before you create anything. When it's done, give me the endpoint URL and a curl command that sends a test request to `/v1/systemone`.
```
