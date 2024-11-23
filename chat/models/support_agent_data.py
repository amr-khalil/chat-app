from dataclasses import dataclass


@dataclass
class SupportAgentData:
    agent_id: int
    name: str
    email: str = "helpdesk@example.com"
