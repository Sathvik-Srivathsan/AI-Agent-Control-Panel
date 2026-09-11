from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="")
    system_prompt = Column(Text, nullable=False, default="")
    model = Column(String, nullable=False, default="")
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    runs = relationship("Run", back_populates="agent")


class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    final_response = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")
    model = Column(String, nullable=False, default="")
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    llm_requests = Column(Integer, nullable=False, default=0)
    error = Column(Text, nullable=True)

    agent = relationship("Agent", back_populates="runs")
    tool_calls = relationship("ToolCall", back_populates="run")
    messages = relationship("Message", back_populates="run")


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    tool_name = Column(String, nullable=False)
    arguments = Column(Text, nullable=False, default="{}")
    result = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    run = relationship("Run", back_populates="tool_calls")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    run = relationship("Run", back_populates="messages")
