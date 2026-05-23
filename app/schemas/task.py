from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    topic: str
    template_type: str
    user_context: str | None = None


class TaskResponse(BaseModel):
    id: str
    topic: str
    template_type: str
    user_context: str | None
    status: str
    current_round: int
