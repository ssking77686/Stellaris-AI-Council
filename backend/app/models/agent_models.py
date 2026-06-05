from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from .database import Base


class Agent(Base):
    __tablename__ = "agents"
    id = Column(String(32), primary_key=True)
    role_name = Column(String(32))
    role_title = Column(String(64))
    domain = Column(String(32))
    system_prompt = Column(Text)


class AgentMemory(Base):
    __tablename__ = "agent_memories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(32), ForeignKey("agents.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(32), ForeignKey("agents.id"))
    session_id = Column(String(64))
    role = Column(String(16))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(String(64), primary_key=True)
    agent_id = Column(String(32))
    title = Column(String(128))
    description = Column(Text)
    cost = Column(Text)
    status = Column(String(16), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class EventLog(Base):
    __tablename__ = "event_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(32))
    title = Column(String(128))
    description = Column(Text)
    agent_id = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow)


class CoordinationTask(Base):
    __tablename__ = "coordination_tasks"
    id = Column(String(32), primary_key=True)
    from_agent = Column(String(32))
    to_agent = Column(String(32))
    issue = Column(Text)
    response_to = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    status = Column(String(16), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class CourtSession(Base):
    __tablename__ = "court_sessions"
    id = Column(String(32), primary_key=True)
    status = Column(String(16), default="pending")
    agenda = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
