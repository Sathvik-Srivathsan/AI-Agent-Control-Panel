from sqlalchemy.orm import Session
from app.db.models import Agent


def seed_agents(db: Session):
    existing = db.query(Agent).first()
    if existing:
        return

    code_assistant = Agent(
        id="code-assistant",
        name="Code Assistant",
        description="Analyzes source code using controlled filesystem tools.",
        system_prompt=(
            "You are a code analysis assistant.\n"
            "You can inspect files using the available controlled filesystem tools.\n"
            "You must not invent file contents.\n"
            "You must inspect relevant files before making claims about them.\n"
            "You should explain findings clearly.\n"
            "You should identify potential bugs, maintainability issues, and suspicious patterns.\n"
            "You must not modify files."
        ),
        model="",
        enabled=True,
    )

    db.add(code_assistant)
    db.commit()
