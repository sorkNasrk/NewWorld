from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class McpHttpResponse:
    status_code: int
    headers: dict[str, str]
    body: str
    raw: bytes


class McpError(RuntimeError):
    pass


class McpClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        path: str = "/mcp",
        client_name: str = "NewWorld.Tools.MCP",
        client_version: str = "1.0",
    ) -> None:
        self.host = host
        self.port = port
        self.path = path
        self.client_name = client_name
        self.client_version = client_version
        self._next_id = 1
        self.session_id: str | None = None

    def __enter__(self) -> "McpClient":
        self.initialize()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def initialize(self) -> str:
        params = {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {
                "name": self.client_name,
                "version": self.client_version,
            },
        }
        response = self.json_rpc("initialize", params=params, timeout_seconds=15)
        session_id = response["http"].headers.get("mcp-session-id")
        if not session_id:
            raise McpError("MCP initialize succeeded but did not return Mcp-Session-Id.")
        self.session_id = session_id
        self.json_rpc("notifications/initialized", notification=True, timeout_seconds=5)
        return session_id

    def close(self) -> None:
        if not self.session_id:
            return
        try:
            with socket.create_connection((self.host, self.port), timeout=1.0) as client:
                request = (
                    f"DELETE {self.path} HTTP/1.1\r\n"
                    f"Host: {self.host}:{self.port}\r\n"
                    f"Mcp-Session-Id: {self.session_id}\r\n"
                    "Connection: close\r\n\r\n"
                )
                client.sendall(request.encode("ascii"))
        except OSError:
            pass
        finally:
            self.session_id = None

    def json_rpc(
        self,
        method: str,
        params: Any | None = None,
        notification: bool = False,
        timeout_seconds: float = 60.0,
    ) -> dict[str, Any]:
        http = self.raw_request(method, params=params, notification=notification, timeout_seconds=timeout_seconds)
        parsed = self._body_json(http)
        if parsed and parsed.get("error"):
            error = parsed["error"]
            message = error.get("message") if isinstance(error, dict) else str(error)
            raise McpError(f"MCP JSON-RPC '{method}' failed: {message}")
        return {"http": http, "json": parsed}

    def raw_request(
        self,
        method: str,
        params: Any | None = None,
        notification: bool = False,
        timeout_seconds: float = 60.0,
    ) -> McpHttpResponse:
        body: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if not notification:
            body["id"] = self._next_id
            self._next_id += 1
        if params is not None:
            body["params"] = params

        payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        headers = [
            f"POST {self.path} HTTP/1.1",
            f"Host: {self.host}:{self.port}",
            "Content-Type: application/json",
            "Accept: application/json, text/event-stream",
            f"Content-Length: {len(payload)}",
            "Connection: close",
        ]
        if self.session_id:
            headers.append(f"Mcp-Session-Id: {self.session_id}")
        request = ("\r\n".join(headers) + "\r\n\r\n").encode("ascii") + payload

        deadline = time.monotonic() + timeout_seconds
        chunks: list[bytes] = []
        try:
            with socket.create_connection((self.host, self.port), timeout=3.0) as client:
                client.settimeout(1.0)
                client.sendall(request)
                while time.monotonic() < deadline:
                    try:
                        data = client.recv(8192)
                    except socket.timeout:
                        if chunks:
                            raw_so_far = b"".join(chunks)
                            if self._raw_response_complete(raw_so_far):
                                break
                        continue
                    if not data:
                        break
                    chunks.append(data)
                    raw_so_far = b"".join(chunks)
                    if self._raw_response_complete(raw_so_far):
                        break
        except OSError as exc:
            raise McpError(
                f"UE MCP server is not reachable on {self.host}:{self.port}. "
                f"Start it with python Tools/MCP/start_ue_mcp_editor.py --port {self.port}."
            ) from exc

        if not chunks:
            raise McpError(f"MCP request '{method}' produced no response before timeout.")

        response = self._parse_http_response(b"".join(chunks))
        if response.status_code >= 400:
            raise McpError(f"MCP request '{method}' failed with HTTP {response.status_code}: {response.body.strip()}")
        return response

    def tool(self, name: str, arguments: dict[str, Any] | None = None, timeout_seconds: float = 60.0) -> dict[str, Any]:
        response = self.json_rpc(
            "tools/call",
            params={"name": name, "arguments": arguments or {}},
            timeout_seconds=timeout_seconds,
        )
        result = response["json"].get("result") if response["json"] else None
        if result and result.get("isError"):
            raise McpError(f"MCP tool '{name}' failed: {tool_text(result)}")
        return result or {}

    def toolset_tool(
        self,
        toolset_name: str,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        timeout_seconds: float = 60.0,
    ) -> dict[str, Any]:
        return self.tool(
            "call_tool",
            {
                "toolset_name": toolset_name,
                "tool_name": tool_name,
                "arguments": arguments or {},
            },
            timeout_seconds=timeout_seconds,
        )

    @staticmethod
    def _raw_response_complete(raw: bytes) -> bool:
        separator = b"\r\n\r\n"
        header_end = raw.find(separator)
        if header_end < 0:
            return False
        header = raw[:header_end].decode("iso-8859-1", errors="replace")
        body = raw[header_end + len(separator):]
        status_line = header.split("\r\n", 1)[0]
        if " 202 " in status_line:
            return True
        for line in header.split("\r\n"):
            if line.lower().startswith("content-length:"):
                expected = int(line.split(":", 1)[1].strip())
                return len(body) >= expected
        body_text = body.decode("utf-8", errors="replace")
        if any(line.startswith("data: {") for line in body_text.splitlines()):
            return True
        stripped = body_text.strip()
        return stripped.startswith("{") and stripped.endswith("}")

    @staticmethod
    def _parse_http_response(raw: bytes) -> McpHttpResponse:
        separator = b"\r\n\r\n"
        header_end = raw.find(separator)
        if header_end < 0:
            raise McpError("MCP response did not contain HTTP headers.")
        header_text = raw[:header_end].decode("iso-8859-1", errors="replace")
        body_bytes = raw[header_end + len(separator):]
        lines = header_text.split("\r\n")
        status_parts = lines[0].split()
        if len(status_parts) < 2 or not status_parts[1].isdigit():
            raise McpError(f"Unable to parse MCP HTTP status line: {lines[0]}")
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        return McpHttpResponse(
            status_code=int(status_parts[1]),
            headers=headers,
            body=body_bytes.decode("utf-8", errors="replace"),
            raw=raw,
        )

    @staticmethod
    def _body_json(response: McpHttpResponse) -> dict[str, Any] | None:
        body = response.body.strip()
        if not body:
            return None
        if body.startswith("{"):
            return json.loads(body)

        data_lines: list[str] = []
        for line in response.body.splitlines():
            if line.startswith("data:"):
                data = line.split(":", 1)[1].strip()
                if data and data != "[DONE]":
                    data_lines.append(data)
        for candidate in reversed(data_lines):
            if candidate.startswith("{"):
                return json.loads(candidate)
        raise McpError(f"MCP response body was not JSON or SSE data: {response.body[:200]}")


def tool_text(tool_result: dict[str, Any] | None) -> str:
    if not tool_result:
        return ""
    texts = [
        item.get("text", "")
        for item in tool_result.get("content", [])
        if isinstance(item, dict) and item.get("type") == "text"
    ]
    return "\n".join(texts)


def tool_value(tool_result: dict[str, Any] | None) -> Any:
    if tool_result is None:
        return None
    structured = tool_result.get("structuredContent")
    if structured is not None:
        if isinstance(structured, dict) and "returnValue" in structured:
            return structured["returnValue"]
        return structured

    content = tool_result.get("content")
    if isinstance(content, list):
        texts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
        if len(texts) == 1:
            text = texts[0]
            stripped = text.strip()
            if stripped:
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, dict) and "returnValue" in parsed:
                        return parsed["returnValue"]
                    return parsed
                except json.JSONDecodeError:
                    return text
            return text
        if len(texts) > 1:
            return texts
    return tool_result

