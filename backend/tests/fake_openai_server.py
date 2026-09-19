"""A local OpenAI-compatible server, used to exercise the real HTTP path.

This is a test harness, not a feature. It stands in for the vendor so that
`OpenAICompatibleProvider` — the real request building, real auth header, real
JSON parsing, real tool-call decoding — runs against a real socket, and the
agent loop, tool layer and database run for real behind it.

What it does NOT prove: that a particular hosted model chooses sensible tools.
That needs a real API key.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Scripted replies, popped in order. Each is an OpenAI-shaped `message`.
SCRIPT: list[dict] = []
SEEN_REQUESTS: list[dict] = []


def tool_call_message(name: str, arguments: dict, content: str = "") -> dict:
    return {
        "role": "assistant",
        "content": content,
        "tool_calls": [{
            "id": f"call_{name}",
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments)},
        }],
    }


def text_message(content: str) -> dict:
    return {"role": "assistant", "content": content}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        SEEN_REQUESTS.append({
            "authorization": self.headers.get("Authorization", ""),
            "model": body.get("model"),
            "messages": body.get("messages", []),
            "tools": body.get("tools", []),
        })

        message = SCRIPT.pop(0) if SCRIPT else text_message("Done.")
        payload = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
        }
        encoded = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *args):
        pass


def start(port: int = 8765) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
