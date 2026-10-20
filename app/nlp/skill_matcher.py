from sqlalchemy.orm import Session

from app.models.job_skill import JobSkill
from app.models.student_skill import StudentSkill


LEVEL_SCORES = {
	"BEGINNER": 1,
	"INTERMEDIATE": 2,
	"ADVANCED": 3,
}

REQUIREMENT_WEIGHTS = {
	"REQUIRED": 2,
	"PREFERRED": 1,
}


def get_student_skills(db: Session, student_id: int) -> list[StudentSkill]:
	return db.query(StudentSkill).filter(
		StudentSkill.student_id == student_id
	).all()


def get_job_skills(db: Session, job_id: int) -> list[JobSkill]:
	return db.query(JobSkill).filter(JobSkill.job_id == job_id).all()


def get_skill_ids(
	db: Session,
	*,
	student_id: int | None = None,
	job_id: int | None = None,
) -> list[int]:
	if (student_id is None) == (job_id is None):
		raise ValueError("Provide exactly one of student_id or job_id")

	if student_id is not None:
		return [
			student_skill.skill_id
			for student_skill in get_student_skills(db, student_id)
		]

	return [job_skill.skill_id for job_skill in get_job_skills(db, job_id)]


def _normalized(value: str | None) -> str:
	return (value or "").strip().upper()


def match_skills(
	student_skills: list[StudentSkill],
	job_skills: list[JobSkill],
) -> dict[str, list[int] | float]:
	"""Calculate a requirement- and level-aware weighted skill score."""
	student_skills_by_id = {
		student_skill.skill_id: student_skill
		for student_skill in student_skills
	}
	matched_skill_ids: list[int] = []
	missing_skill_ids: list[int] = []
	earned_weight = 0.0
	total_weight = 0.0

	for job_skill in job_skills:
		weight = REQUIREMENT_WEIGHTS.get(
			_normalized(job_skill.requirement_type),
			REQUIREMENT_WEIGHTS["PREFERRED"],
		)
		required_level = LEVEL_SCORES.get(
			_normalized(job_skill.level),
			LEVEL_SCORES["ADVANCED"],
		)
		total_weight += weight

		student_skill = student_skills_by_id.get(job_skill.skill_id)
		student_level = (
			LEVEL_SCORES.get(_normalized(student_skill.level), 0)
			if student_skill
			else 0
		)
		level_ratio = min(student_level / required_level, 1.0)
		earned_weight += weight * level_ratio

		if student_skill and student_level >= required_level:
			matched_skill_ids.append(job_skill.skill_id)
		else:
			missing_skill_ids.append(job_skill.skill_id)

	match_score = (
		earned_weight / total_weight * 100
		if total_weight
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
