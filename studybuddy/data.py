"""
StudyBuddyData — simulated in-memory backend/catalog shared by all users.
Stands in for a real database in this prototype. User accounts (email,
password, profile fields) are persisted to disk via storage.py so they
survive an app restart; study plans, resources and sessions stay
in-memory only for now.
"""

from datetime import date, timedelta
from typing import List, Optional
from .models import Subject, User, Resource, StudySession
from . import storage


class StudyBuddyData:

    def __init__(self):
        self.subjects = [Subject(n) for n in
                          ["Mathematics", "Computer Science", "Biology", "History", "Economics"]]
        self.users: List[User] = []
        self.resources: List[Resource] = []
        self.sessions: List[StudySession] = []
        self._seed_resources()
        self._load_accounts()

    def _subject(self, name: str) -> Subject:
        return next(s for s in self.subjects if s.name == name)

    def _load_accounts(self):
        """Rebuilds User objects from disk on startup (login/profile data only —
        subjects/study plans are not persisted, since they now live on
        StudyPlan/StudySession rather than being chosen up front)."""
        for record in storage.load_accounts():
            user = User(record["email"], record["password"])
            user.full_name = record.get("full_name", user.username)
            user.academic_year = record.get("academic_year", "Year 1")
            user.school = record.get("school", "")
            user.program = record.get("program", "")
            user.study_goal = record.get("study_goal", "")
            self.users.append(user)

    def persist_accounts(self) -> bool:
        """Call after any account/profile change (register, edit profile,
        change password). Returns True/False so the calling page can warn
        the user if the save silently failed."""
        records = [{
            "email": u.email,
            "password": u.password,
            "full_name": u.full_name,
            "academic_year": u.academic_year,
            "school": u.school,
            "program": u.program,
            "study_goal": u.study_goal,
        } for u in self.users]
        return storage.save_accounts(records)

    def _seed_resources(self):
        seed = [
            ("Loops explained visually", "Computer Science", "Video",
             "https://example.com/loops", "Understand for-loops and while-loops with simple visual examples."),
            ("Python loops: quick check", "Computer Science", "Quiz",
             "https://example.com/loops-quiz", "Test your understanding with 10 focused practice questions."),
            ("Mastering derivatives", "Mathematics", "Article",
             "https://example.com/derivatives", "A clear guide to the rules and patterns behind differentiation."),
            ("Cell Biology Basics", "Biology", "Article",
             "https://example.com/cellbio", "A primer on cell structure and function."),
            ("WWII Timeline", "History", "Video",
             "https://example.com/wwii", "A visual walkthrough of key WWII events."),
            ("Supply & Demand 101", "Economics", "Article",
             "https://example.com/supplydemand", "The basics of market equilibrium."),
        ]
        for title, subj_name, kind, link, blurb in seed:
            self.resources.append(Resource(title, self._subject(subj_name), kind, link, blurb))

    def seed_demo_classmates(self):
        """
        Adds a few example users with schools/programs/subjects already set,
        so 'find schoolmates' and 'find program mates' have someone to find
        even on a fresh demo run. Guarded by email so it's safe to call
        every login without creating duplicates once accounts persist to disk.
        """
        demo = [
            ("maya.chen@stateu.edu", "Maya Chen", "State University",
             "BS Computer Science (BSCS)", ["Computer Science", "Mathematics"]),
            ("jordan.lee@stateu.edu", "Jordan Lee", "State University",
             "BS Business Administration (BSBA) – Financial Management", ["Mathematics", "Economics"]),
            ("sam.rivera@citytech.edu", "Sam Rivera", "City Tech",
             "BS Computer Science (BSCS)", ["History", "Biology"]),
        ]
        added = False
        for email, name, school, program, subject_names in demo:
            if self.find_user(email):
                continue
            u = self.register(email, "Password1")
            u.full_name = name
            u.school = school
            u.program = program
            for n in subject_names:
                u.add_subject(self._subject(n))
            added = True
        if added:
            self.persist_accounts()

    def seed_demo_session(self, host: User):
        """Adds a couple of example sessions so the Sessions page isn't empty."""
        if self.sessions:
            return
        cs = self._subject("Computer Science")
        math = self._subject("Mathematics")
        hist = self._subject("History")
        self.sessions.append(StudySession(cs, host, date.today(),
                                           "Let's work through joins and normalization together.",
                                           location_name="Library, Room 214"))
        self.sessions.append(StudySession(math, host, date.today() + timedelta(days=1),
                                           "Group derivatives review before the quiz.",
                                           location_name="Online (Google Meet)"))
        self.sessions.append(StudySession(hist, host, date.today() + timedelta(days=2),
                                           "WWII essay outline workshop.",
                                           location_name="Student Union, 2nd floor"))

    def find_user(self, email: str) -> Optional[User]:
        email = email.strip().lower()
        return next((u for u in self.users if u.email.lower() == email), None)

    def register(self, email: str, password: str) -> User:
        user = User(email, password)
        self.users.append(user)
        self.persist_accounts()
        return user

    def resources_for_subjects(self, subjects: List[Subject]) -> List[Resource]:
        subj_ids = {s.id for s in subjects}
        return [r for r in self.resources if r.subject.id in subj_ids]

    def sessions_for_subjects(self, subjects: List[Subject]) -> List[StudySession]:
        subj_ids = {s.id for s in subjects}
        matching = [s for s in self.sessions if s.subject.id in subj_ids]
        return matching or self.sessions

    def schoolmates(self, user: User) -> List[User]:
        """Other users at the same school (excluding the given user)."""
        if not user.school:
            return []
        return [u for u in self.users
                if u.id != user.id and u.school.strip().lower() == user.school.strip().lower()]

    def programmates(self, user: User) -> List[User]:
        """Other users in the same degree program (excluding the given user)."""
        if not user.program:
            return []
        return [u for u in self.users
                if u.id != user.id and u.program == user.program]

    def shared_subjects(self, user: User, other: User) -> List[Subject]:
        other_ids = {s.id for s in other.subjects}
        return [s for s in user.subjects if s.id in other_ids]
