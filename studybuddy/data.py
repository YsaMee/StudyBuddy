from datetime import date, timedelta
from typing import List, Optional
from .models import Subject, User, Resource, StudySession


class StudyBuddyData:

    def __init__(self):
        self.subjects = [Subject(n) for n in
                          [
                              "Mathematics",
                              "Computer Science",
                              "Biology",
                              "History",
                              "Economics",
                              "Object-Oriented Programming",
                              "Data Structures and Algorithm",
                              "Programming Languages",
                              "IT Infrastructures and Networks Technologies",
                              "Differential and Integral Calculus",
                          ]]
        self.users: List[User] = []
        self.resources: List[Resource] = []
        self.sessions: List[StudySession] = []
        self._classmates_seeded = False
        self._seed_resources()

    def _subject(self, name: str) -> Subject:
        return next(s for s in self.subjects if s.name == name)

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
            ("Object-Oriented Design Basics", "Object-Oriented Programming", "Article",
             "https://example.com/oop", "A practical introduction to classes, objects, and encapsulation."),
            ("Data Structures Practice", "Data Structures and Algorithm", "Quiz",
             "https://example.com/data-structures", "Practice choosing the right structure for each problem."),
            ("Programming Language Concepts", "Programming Languages", "Video",
             "https://example.com/programming-languages", "Explore how programming languages express ideas and manage data."),
            ("Network Infrastructure Fundamentals", "IT Infrastructures and Networks Technologies", "Article",
             "https://example.com/network-infrastructure", "Learn the building blocks of modern IT networks."),
            ("Calculus Essentials", "Differential and Integral Calculus", "Article",
             "https://example.com/calculus", "Review derivatives, integrals, and their practical applications."),
        ]
        for title, subj_name, kind, link, blurb in seed:
            self.resources.append(Resource(title, self._subject(subj_name), kind, link, blurb))

    def seed_demo_session(self, host: User):
        """Adds a couple of example sessions so the Sessions page isn't empty."""
        if self.sessions:
            return
        cs = self._subject("Computer Science")
        math = self._subject("Mathematics")
        hist = self._subject("History")
        self.sessions.append(StudySession(cs, host, date.today(),
                                           "Let's work through joins and normalization together."))
        self.sessions.append(StudySession(math, host, date.today() + timedelta(days=1),
                                           "Group derivatives review before the quiz."))
        self.sessions.append(StudySession(hist, host, date.today() + timedelta(days=2),
                                           "WWII essay outline workshop."))
        new_subject_sessions = [
            ("Object-Oriented Programming", "Design patterns study group."),
            ("Data Structures and Algorithm", "Compare sorting and search strategies."),
            ("Programming Languages", "Discuss language paradigms and type systems."),
            ("IT Infrastructures and Networks Technologies", "Review network layers and protocols."),
            ("Differential and Integral Calculus", "Work through derivatives and integrals together."),
        ]
        for subject_name, note in new_subject_sessions:
            self.sessions.append(StudySession(
                self._subject(subject_name), host, date.today() + timedelta(days=3), note
            ))

    def seed_demo_classmates(self):
        """
        Adds a few example users with schools/subjects already set, so the
        'find schoolmates' feature has someone to find even on a fresh demo
        run (a brand-new prototype otherwise has only the one registered user).
        """
        if self._classmates_seeded:
            return
        self._classmates_seeded = True
        demo = [
            ("maya.chen@stateu.edu", "Maya Chen", "State University", ["Computer Science", "Mathematics"]),
            ("jordan.lee@stateu.edu", "Jordan Lee", "State University", ["Mathematics", "Economics"]),
            ("sam.rivera@citytech.edu", "Sam Rivera", "City Tech", ["History", "Biology"]),
            ("riley.patel@stateu.edu", "Riley Patel", "State University",
             ["Object-Oriented Programming", "Programming Languages"]),
            ("noah.kim@stateu.edu", "Noah Kim", "State University",
             ["Data Structures and Algorithm", "IT Infrastructures and Networks Technologies"]),
            ("sofia.rossi@citytech.edu", "Sofia Rossi", "City Tech",
             ["Differential and Integral Calculus"]),
        ]
        for email, name, school, subject_names in demo:
            u = self.register(email, "Password1")
            u.full_name = name
            u.school = school
            u.select_subjects([self._subject(n) for n in subject_names])

    def find_user(self, email: str) -> Optional[User]:
        email = email.strip().lower()
        return next((u for u in self.users if u.email.lower() == email), None)

    def register(self, email: str, password: str) -> User:
        user = User(email, password)
        self.users.append(user)
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

    def shared_subjects(self, user: User, other: User) -> List[Subject]:
        other_ids = {s.id for s in other.subjects}
        return [s for s in user.subjects if s.id in other_ids]
