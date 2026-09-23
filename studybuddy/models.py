"""
Domain model for StudyBuddy: Subject, Task, StudyPlan, Resource,
StudySession and User. Pure data + behaviour, no Streamlit here.
"""

from datetime import date, datetime
from typing import List, Optional
import itertools

_id_counter = itertools.count(1)


class Subject:
    """Represents a subject a student is studying."""

    def __init__(self, name: str):
        self.id = next(_id_counter)
        self.name = name

    def __str__(self):
        return self.name


class Task:
    """A single to-do item inside a StudyPlan."""

    DIFFICULTIES = ["Easy", "Medium", "Hard"]

    def __init__(self, title: str, deadline: date, difficulty: str = "Medium", goal: str = ""):
        self.id = next(_id_counter)
        self.title = title
        self.deadline = deadline
        self.difficulty = difficulty
        self.goal = goal
        self.completed = False

    def mark_complete(self):
        self.completed = True

    def days_left(self) -> int:
        return (self.deadline - date.today()).days

    def status_icon(self):
        return "✅" if self.completed else "⏳"


class StudyPlan:
    """Holds the tasks/deadlines/goals for one subject."""

    def __init__(self, subject: Subject):
        self.subject = subject
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def progress(self) -> float:
        if not self.tasks:
            return 0.0
        done = sum(1 for t in self.tasks if t.completed)
        return done / len(self.tasks)

    def open_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.completed]


class Resource:
    """A learning resource (article, video, quiz, notes, etc.). A resource
    the student uploads (e.g. a PDF) can carry its extracted text plus an
    AI-generated summary, cached here so it isn't regenerated every rerun."""

    def __init__(self, title: str, subject: Subject, kind: str, link: str,
                 blurb: str = "", content_text: str = ""):
        self.id = next(_id_counter)
        self.title = title
        self.subject = subject
        self.kind = kind
        self.link = link
        self.blurb = blurb
        self.content_text = content_text   # raw extracted text, for uploads
        self.ai_summary: Optional[str] = None

    def set_summary(self, summary: str):
        self.ai_summary = summary

    def __str__(self):
        return f"{self.title} ({self.kind}) — {self.subject.name}"


class Message:
    """A single public chat message inside a StudySession."""

    def __init__(self, sender: "User", text: str, sent_at: Optional[datetime] = None):
        self.id = next(_id_counter)
        self.sender = sender
        self.text = text
        self.sent_at = sent_at or datetime.now()


class StudySession:
    """A collaborative study session other students can join, with a
    plain-text location and a public chat for participants."""

    def __init__(self, subject: Subject, host: "User", when: date, note: str = "",
                 location_name: str = ""):
        self.id = next(_id_counter)
        self.subject = subject
        self.host = host
        self.when = when
        self.note = note
        self.location_name = location_name
        self.participants: List["User"] = [host]
        self.messages: List[Message] = []

    def join(self, user: "User"):
        if user not in self.participants:
            self.participants.append(user)

    def post_message(self, user: "User", text: str):
        """Only participants can post — join the session first."""
        if user in self.participants and text.strip():
            self.messages.append(Message(user, text.strip()))

    def match_score(self, subjects: List[Subject]) -> int:
        """How well this session matches a user's subjects (simple demo heuristic)."""
        return 95 if any(s.id == self.subject.id for s in subjects) else 40

    def __str__(self):
        return f"{self.subject.name} session hosted by {self.host.username} on {self.when}"


class User:
    """A registered StudyBuddy user. Logs in with email + password.

    Subjects are NOT chosen up front in the profile — a user's subjects
    are simply whichever subjects they've started a StudyPlan for (by
    adding one on the Study Plans page or creating/joining a session for
    it). `subjects` below is a read-only view over that, not a separate
    list to keep in sync.
    """

    def __init__(self, email: str, password: str):
        self.id = next(_id_counter)
        self.email = email
        self.password = password
        self.username = email.split("@")[0]  # display handle, derived from email
        self.full_name = self.username
        self.academic_year = "Year 1"
        self.school = ""
        self.program = ""
        self.study_goal = ""
        self.study_plans: List[StudyPlan] = []
        self.saved_resources: List[Resource] = []

    def check_password(self, password: str) -> bool:
        return self.password == password

    @property
    def subjects(self) -> List[Subject]:
        return [p.subject for p in self.study_plans]

    def add_subject(self, subject: Subject) -> StudyPlan:
        """Returns the existing plan for this subject, or creates one."""
        plan = self.plan_for(subject)
        if plan is None:
            plan = StudyPlan(subject)
            self.study_plans.append(plan)
        return plan

    def plan_for(self, subject: Subject) -> Optional[StudyPlan]:
        for p in self.study_plans:
            if p.subject.id == subject.id:
                return p
        return None

    def save_resource(self, resource: Resource):
        if resource not in self.saved_resources:
            self.saved_resources.append(resource)

    def total_tasks(self) -> int:
        return sum(len(p.tasks) for p in self.study_plans)

    def completed_tasks(self) -> int:
        return sum(1 for p in self.study_plans for t in p.tasks if t.completed)

    def overall_progress(self) -> float:
        if not self.study_plans:
            return 0.0
        return sum(p.progress() for p in self.study_plans) / len(self.study_plans)
