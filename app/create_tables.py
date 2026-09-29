from sqlalchemy import inspect, text

from app.core.database import Base, engine

from app.models import application
from app.models import user
from app.models import student_skill
from app.models import skill
from app.models import company
from app.models import job
from app.models import job_skill
from app.models import cv
from app.models import recommendation
from app.models import recruiter_profile
from app.models import student_profile
from app.models import notification
from app.models import password_reset_token

Base.metadata.create_all(bind=engine)


def migrate_auth_columns():
	user_columns = {column["name"] for column in inspect(engine).get_columns("users")}

	with engine.begin() as connection:
		if "google_id" not in user_columns:
			connection.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR"))
		if "auth_provider" not in user_columns:
			connection.execute(
				text(
					"ALTER TABLE users "
					"ADD COLUMN auth_provider VARCHAR NOT NULL DEFAULT 'local'"
				)
			)
		if engine.dialect.name == "postgresql":
			connection.execute(
				text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL")
			)


migrate_auth_columns()