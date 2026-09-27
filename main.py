from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Optional
import httpx
import time
from database import init_db, validate_api_key, log_usage


################### pydantic model #####################
class Message(BaseModel):
    content: str = Field(min_length=1)
    role: Literal["system", "user", "assistant"]


# ChatRequest is a list of messages{role and content}
class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)
    model: str | None = None  # optional
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool | None = False


################ fastapi request ##################
app = FastAPI()
bearer_scheme = HTTPBearer()

################ Database ##################
init_db()


@app.get("/health")
def health():
    return {"status": "okay"}


########## request to local llm to return data ##########
@app.post("/v1/chat/completions")
def request(
    chatrequest: ChatRequest,
    token: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
):

    key_record = validate_api_key(token.credentials)
    if key_record is None:
        raise HTTPException(status_code=401, detail="invalid api key")

    # HTTPX needs JSON instead of Pydantic model
    # HTTPX will seralize into JSON
    payload = chatrequest.model_dump(
        exclude_none=True
    )  # Exclude_none will ignore optional value
    try:
        start_time = time.perf_counter()

        response = httpx.post(
            url="http://127.0.0.1:8080/v1/chat/completions",
            json=payload,
            timeout=60.0,
        )
        latency_ms = (time.perf_counter() - start_time) * 1000

        response.raise_for_status()

    except httpx.ConnectError:  # if the server is off
        raise HTTPException(status_code=503, detail="Model Server is unavailable")
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Model Server took too long to respond"
        )
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Model server returned an error")
    data = response.json()

    log_usage(
        api_key_id=key_record[0],
        status_code=response.status_code,
        prompt_tokens=data["usage"]["prompt_tokens"],
        completion_tokens=data["usage"]["completion_tokens"],
        total_tokens=data["usage"]["total_tokens"],
        latency_ms=latency_ms,
    )

    return data
