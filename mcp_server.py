import hashlib
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request

EMAIL = "24f2000080@ds.study.iitm.ac.in"

mcp = FastMCP("solve-challenge-server", stateless_http=True)

@mcp.tool()
def solve_challenge() -> str:
    """Solves the exam challenge using the request's challenge header."""
    request: Request = mcp.get_context().request_context.request
    challenge = request.headers.get("x-exam-challenge", "")
    raw = f"{challenge}:{EMAIL}"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return digest[:16]

app = mcp.streamable_http_app()
