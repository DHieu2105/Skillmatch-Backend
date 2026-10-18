from sqlalchemy import text
from sqlalchemy.orm import Session


def sync_skill_id_sequence(db: Session) -> None:
    """Keep PostgreSQL's generated skill ID ahead of manually inserted rows."""
    if not db.bind or db.bind.dialect.name != "postgresql":
        return

    db.execute(text(
        "SELECT setval("
        "pg_get_serial_sequence('skills', 'skill_id')::regclass, "
        "COALESCE(MAX(skill_id), 1), "
        "MAX(skill_id) IS NOT NULL"
        ") FROM skills"
    ))
