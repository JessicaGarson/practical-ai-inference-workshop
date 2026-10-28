# Set up the Runpod MCP server

In Part 2 of the workshop, an AI agent deploys OpenJev for you. To do that, the agent needs the [Runpod MCP server](https://github.com/runpod/runpod-mcp), which lets it create and manage Runpod resources on your behalf. Set it up before the workshop. It takes about five minutes.

Runpod hosts the server at `https://mcp.runpod.io/`, so there's nothing to run yourself. You point your agent at that URL and sign in with your Runpod account.

## Before you start

- A [Runpod account](https://console.runpod.io) with credits
- An MCP-capable AI agent. These directions use [Claude Code](https://code.claude.com/docs/en/setup); other agents are covered below.
- [Node.js](https://nodejs.org/en/download) 20 or newer, only if you use the guided installer for another agent

## Claude Code

1. Add the server:

   ```bash
   claude mcp add --transport http runpod -s user https://mcp.runpod.io/
   ```

   `-s user` makes the server available in every project, not just the current folder.

2. Start Claude Code, then type `/mcp`. The `runpod` entry shows **Needs authentication** the first time.

3. Select `runpod` and choose to authenticate. Your browser opens the Runpod console. Log in and approve access.

   > If you belong to more than one Runpod team, switch to the team you want to use in the console *before* you approve. The agent works in whichever team was selected.

4. Back in Claude Code, `/mcp` should now show `runpod` as **Connected**.

## Other agents

The guided installer detects the agents on your machine (Cursor, Windsurf, VS Code, Claude Desktop, and others) and configures the ones you choose:

```bash
npx @runpod/mcp-server@latest add
```

Choose **Hosted** when asked. Then restart your agent; it opens the Runpod sign-in the first time it connects.

To configure an agent by hand instead, add an MCP server entry named `runpod` with this URL:

```json
{
  "mcpServers": {
    "runpod": {
      "url": "https://mcp.runpod.io/"
    }
  }
}
```

## Check that it works

Ask your agent:

```text
List my Runpod Serverless endpoints.
```

It should call a Runpod tool and answer with your endpoints, or say you have none. Either answer means the connection works. This request only reads data, so it doesn't create anything or cost money.

## Troubleshooting

**`/mcp` still shows "Needs authentication."** Run `/mcp` again and repeat the sign-in. If the browser shows a connection error after you approve, copy the full `http://localhost:.../callback?...` address from the browser's address bar and paste it into Claude Code.

**Sign-in fails with `403 Forbidden`.** The hosted server has temporarily blocked your IP address after too many unauthenticated requests. This can happen when a whole room on the same Wi-Fi signs in at once. The block lifts within an hour. To connect right away, use your API key instead of signing in (next section).

**The agent sees the wrong account's resources.** Switch to the right team in the [console](https://console.runpod.io), then authenticate again from `/mcp`.

## Alternative: connect with an API key

If browser sign-in doesn't work for you, connect with a [Runpod API key](https://docs.runpod.io/get-started/credentials) instead. Remove the server you added, then add it again with your key:

```bash
claude mcp remove runpod -s user
claude mcp add --transport http runpod -s user https://mcp.runpod.io/ \
  --header "Authorization: Bearer $RUNPOD_API_KEY"
```

This stores your key in Claude Code's settings, so never share or commit that file. For other agents, add a `headers` block with the same `Authorization` value to the JSON entry above.

## Remove it later

```bash
claude mcp remove runpod -s user
```

Or, if you used the guided installer:

```bash
npx @runpod/mcp-server@latest remove
```
