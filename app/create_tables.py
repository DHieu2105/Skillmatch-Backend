from sqlalchemy import inspect, text

from app.core.database import Base, SessionLocal, engine
from app.seed_skills import seed_skill_catalog

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


def migrate_cv_archive_column():
	cv_columns = {column["name"] for column in inspect(engine).get_columns("cvs")}

	if "is_archived" not in cv_columns:
		with engine.begin() as connection:
			connection.execute(text(
				"ALTER TABLE cvs "
				"ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT FALSE"
			))
			connection.execute(text(
				"UPDATE cvs SET is_archived = TRUE "
				"WHERE is_default = FALSE "
				"AND cv_id IN (SELECT DISTINCT cv_id FROM applications)"
			))


migrate_cv_archive_column()


def migrate_avatar_column():
	user_columns = {column["name"] for column in inspect(engine).get_columns("users")}
	if "avatar_url" not in user_columns:
		with engine.begin() as connection:
			connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))


migrate_avatar_column()


def migrate_company_columns():
	columns = {column["name"] for column in inspect(engine).get_columns("companies")}
	new_cols = [
		("address", "VARCHAR"),
		("google_map_url", "VARCHAR"),
		("logo_url", "VARCHAR"),
		("company_size", "VARCHAR"),
		("industry", "VARCHAR"),
		("benefits", "VARCHAR"),
	]
	with engine.begin() as connection:
		for col_name, col_type in new_cols:
			if col_name not in columns:
				connection.execute(text(f"ALTER TABLE companies ADD COLUMN {col_name} {col_type}"))


migrate_company_columns()


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
		duplicate_skill_name = connection.execute(text(
			"SELECT LOWER(skill_name) FROM skills "
			"GROUP BY LOWER(skill_name) HAVING COUNT(*) > 1 LIMIT 1"
		)).first()
		if not duplicate_skill_name:
			connection.execute(text(
				"CREATE UNIQUE INDEX IF NOT EXISTS uq_skill_name_ci "
				"ON skills (LOWER(skill_name))"
			))


migrate_integrity_constraints()


def seed_reference_data():
	with SessionLocal() as db:
		seed_skill_catalog(db)


seed_reference_data()
