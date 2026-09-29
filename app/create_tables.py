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


def migrate_integrity_constraints():
	user_columns = {column["name"] for column in inspect(engine).get_columns("companies")}

	with engine.begin() as connection:
		if "owner_user_id" not in user_columns:
			connection.execute(text(
				"ALTER TABLE companies ADD COLUMN owner_user_id INTEGER"
			))
			if engine.dialect.name == "postgresql":
				connection.execute(text(
					"UPDATE companies AS company "
					"SET owner_user_id = recruiter.user_id "
					"FROM recruiter_profiles AS recruiter "
					"WHERE company.company_id = recruiter.company_id "
					"AND company.owner_user_id IS NULL"
				))

		if engine.dialect.name == "postgresql":
			job_columns = inspect(engine).get_columns("jobs")
			deadline_column = next(
				column for column in job_columns if column["name"] == "deadline"
			)
			if "CHAR" in str(deadline_column["type"]).upper() or "TEXT" in str(
				deadline_column["type"]
			).upper():
				connection.execute(text(
					"ALTER TABLE jobs ALTER COLUMN deadline TYPE DATE "
					"USING NULLIF(deadline, '')::date"
				))

		connection.execute(text(
			"CREATE UNIQUE INDEX IF NOT EXISTS uq_application_student_job "
			"ON applications (student_id, job_id)"
		))
		connection.execute(text(
			"CREATE UNIQUE INDEX IF NOT EXISTS uq_recommendation_student_job "
			"ON recommendations (student_id, job_id)"
		))
		connection.execute(text(
			"CREATE UNIQUE INDEX IF NOT EXISTS uq_cv_default_per_student "
			"ON cvs (student_id) WHERE is_default = TRUE"
		))


migrate_integrity_constraints()