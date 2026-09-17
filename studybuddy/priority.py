from typing import List, Tuple, Dict
from .models import Task, StudyPlan, Subject


class PriorityEngine:

    DIFFICULTY_WEIGHT = {"Easy": 10, "Medium": 20, "Hard": 30}

    @classmethod
    def task_score(cls, task: Task) -> int:
        """Returns a 0-100 urgency/priority score for a single open task."""
        if task.completed:
            return 0
        days_left = max(task.days_left(), 0)
        urgency = max(0, 100 - days_left * 8)                 # closer deadline -> higher
        difficulty = cls.DIFFICULTY_WEIGHT.get(task.difficulty, 15)
        overdue_or_soon = 100 if task.days_left() <= 3 else 60
        score = 0.55 * urgency + 0.30 * difficulty + 0.15 * overdue_or_soon
        return int(min(100, round(score)))

    @classmethod
    def ranked_tasks(cls, study_plans: List[StudyPlan]) -> List[Tuple[int, Task, Subject]]:
        """All open tasks across every subject, ranked highest priority first."""
        scored = [
            (cls.task_score(t), t, plan.subject)
            for plan in study_plans
            for t in plan.open_tasks()
        ]
        scored.sort(key=lambda row: row[0], reverse=True)
        return scored

    @classmethod
    def subject_recommendations(cls, study_plans: List[StudyPlan]) -> List[Dict]:
        """
        One row per subject that still has open tasks, sorted by urgency,
        with a plain-language reason a student can act on.
        """
        rows = []
        for plan in study_plans:
            open_tasks = plan.open_tasks()
            if not open_tasks:
                continue
            top_task = max(open_tasks, key=cls.task_score)
            score = cls.task_score(top_task)
            days_left = top_task.days_left()

            if days_left <= 0:
                reason = "Deadline has passed — do this first."
            elif days_left <= 3:
                reason = f"Due in {days_left} day(s) and still at {int(plan.progress()*100)}% complete."
            elif plan.progress() < 0.3:
                reason = f"Barely started ({int(plan.progress()*100)}%) — worth getting ahead on."
            else:
                reason = f"{top_task.difficulty} task, {len(open_tasks)} task(s) left."

            rows.append({
                "subject": plan.subject,
                "plan": plan,
                "top_task": top_task,
                "score": score,
                "reason": reason,
            })
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows
