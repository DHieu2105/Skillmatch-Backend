from sqlalchemy.orm import Session

from app.models.job_skill import JobSkill
from app.models.student_skill import StudentSkill


def get_skill_ids(
	db: Session,
	*,
	student_id: int | None = None,
	job_id: int | None = None,
) -> list[int]:
	if (student_id is None) == (job_id is None):
		raise ValueError("Provide exactly one of student_id or job_id")

	if student_id is not None:
		student_skills = db.query(StudentSkill).filter(
			StudentSkill.student_id == student_id
		).all()
		return [student_skill.skill_id for student_skill in student_skills]

	job_skills = db.query(JobSkill).filter(
		JobSkill.job_id == job_id
	).all()
	return [job_skill.skill_id for job_skill in job_skills]


def match_skills(
	student_skill_ids: list[int],
	job_skill_ids: list[int],
) -> dict[str, list[int] | float]:
	student_skill_set = set(student_skill_ids)
	job_skill_set = set(job_skill_ids)

	matched_skill_ids = [
		skill_id
		for skill_id in student_skill_ids
		if skill_id in job_skill_set
	]
	missing_skill_ids = [
		skill_id
		for skill_id in job_skill_ids
		if skill_id not in student_skill_set
	]

	match_score = (
		len(matched_skill_ids) / len(job_skill_ids) * 100
		if job_skill_ids
		else 0.0
	)

	return {
		"matched_skill_ids": matched_skill_ids,
		"missing_skill_ids": missing_skill_ids,
		"match_score": match_score,
	}


def calculate_final_score(
	tfidf_score: float,
	skill_match_score: float,
) -> float:
	return tfidf_score * 0.4 + skill_match_score * 0.6
