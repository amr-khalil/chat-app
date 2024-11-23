from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from chat.api.chat_facade import ChatFacade

app = FastAPI()
chat_facade = ChatFacade()


# Pydantic models for API input
class CustomerCreateRequest(BaseModel):
    customer_id: int = 123
    name: str = "Jonas"
    email: str = "Jonas@example.com"


class AgentCreateRequest(BaseModel):
    agent_id: int = 456
    name: str = "timo"
    email: str = "timo@helpdesk.com"


class ChatInitiateRequest(BaseModel):
    customer_id: int = 123
    topic: str = "Pyaments Issue"


class MessageSendRequest(BaseModel):
    session_id: uuid.UUID | str = ""
    customer_id: int = 123
    content: str = "Hi, could you help me? i can not process my Pyaments"


@app.post("/agents/")
def create_agent(agent: AgentCreateRequest):
    try:
        chat_facade.create_agent(
            agent_id=agent.agent_id,
            name=agent.name,
            email=agent.email,
        )
        return {"message": "Agent created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/customers/")
def create_customer(customer: CustomerCreateRequest):
    try:
        chat_facade.create_customer(
            customer_id=customer.customer_id,
            name=customer.name,
            email=customer.email,
        )
        return {"message": "Customer created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chats/new")
async def initiate_chat(request: ChatInitiateRequest):
    try:
        session_id = await chat_facade.initiate_chat(
            customer_id=request.customer_id, topic=request.topic
        )
        return {"session_id": str(session_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chats/{session_id}/assign-agent/")
async def assign_agent_to_session(session_id: uuid.UUID, agent_id: int = 456):
    """
    Assign an agent to a specific chat session.
    """
    try:
        await chat_facade.agent_handle_session(session_id=session_id, agent_id=agent_id)
        return {
            "message": f"Agent {agent_id} assigned to session {session_id} successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chats/{session_id}/messages/customer/")
async def customer_send_message(session_id: uuid.UUID, request: MessageSendRequest):
    try:
        await chat_facade.customer_send_message(
            session_id=session_id,
            customer_id=request.customer_id,
            content=request.content,
        )
        return {"message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chats/{session_id}/messages/agent/")
async def agent_send_message(
    session_id: uuid.UUID,
    agent_id: int = 456,
    content: str = "Hi, clould you clear your coockies and login again.",
):
    """
    Allow an agent to send a message in a chat session.
    """
    try:
        await chat_facade.agent_send_message(
            session_id=session_id, agent_id=agent_id, content=content
        )
        return {"message": f"Agent {agent_id} sent a message in session {session_id}."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/chats/{session_id}/history/")
def get_chat_history(session_id: uuid.UUID):
    try:
        history = chat_facade.get_chat_history(session_id)
        return {"messages": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/customers/")
def list_customers():
    return chat_facade.list_customers()


@app.get("/agents/")
def list_agents():
    return chat_facade.list_agents()


@app.get("/sessions/")
def get_all_sessions():
    """
    Endpoint to get all chat sessions data.
    """
    try:
        sessions = chat_facade.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
