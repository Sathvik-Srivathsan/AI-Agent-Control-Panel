from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models import Base

engine = create_engine(f"sqlite:///{settings.workspace_path.parent / 'agent_control.db'}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    with engine.begin() as conn:
        rows = conn.exec_driver_sql("PRAGMA table_info(runs)").fetchall()
        columns = {row[1] for row in rows}
        if rows and "llm_requests" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE runs ADD COLUMN llm_requests INTEGER NOT NULL DEFAULT 0"
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
