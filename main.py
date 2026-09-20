from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx


################### pydantic model #####################
class Message(BaseModel):
    role: str
    content: str


# ChatRequest is a list of messages{role and content}
class ChatRequest(BaseModel):
    messages: list[Message]


################ fastapi request ##################
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "okay"}


"""
request to local llm to return data
"""
@app.post("/v1/chat/completions")
def request(chatrequest: ChatRequest):
    data = chatrequest.messages
    # [0][content] is wrong since the pydantic is receving json, they convert it into object
    if len(data) > 0:
        # HTTPX needs JSON instead of Pydantic model
        # HTTPX will seralize into JSON
        payload = chatrequest.model_dump()
        response = httpx.post(
            url="http://127.0.0.1:8080/v1/chat/completions", json=payload, timeout=60.0
        )
        return response.json()
    else:
        raise HTTPException(status_code=400, detail="provide at least some info")
