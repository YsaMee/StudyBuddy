"""
programs — the catalog of degree programs a student can put on their
profile. A student's program acts as a second identifier alongside their
school, for finding "program mates" (classmates in the same degree).
Kept as plain data, separate from the UI, so the list can be edited
without touching profile.py.
"""

PROGRAM_CATALOG = {
    "Information Technology & Computing": [
        "BS Computer Science (BSCS)",
        "BS Information Systems (BSIS)",
        "BS Entertainment and Multimedia Computing",
    ],
    "Business & Management": [
        "BS Accountancy (BSA)",
        "BS Business Administration (BSBA) – Financial Management",
        "BS Business Administration (BSBA) – Marketing Management",
        "BS Business Administration (BSBA) – HR Management",
        "BS Business Administration (BSBA) – Operations Management",
        "BS Entrepreneurship",
        "BS Hospitality Management / Tourism Management",
    ],
    "Health & Medical Sciences": [
        "BS Medical Technology (BSMT)",
        "BS Pharmacy",
        "BS Physical Therapy (BSPT) / Occupational Therapy (BSOT)",
        "BA/BS Psychology",
    ],
    "Engineering & Architecture": [
        "BS Civil Engineering (BSCE)",
        "BS Computer Engineering (BSCpE)",
        "BS Electrical / Electronics Engineering (BSEE / ECE)",
        "BS Mechanical Engineering (BSME)",
        "BS Industrial Engineering (BSIE)",
        "BS Architecture (BS Archi)",
    ],
    "Arts & Communications": [
        "Bachelor of Multimedia Arts (BMMA)",
        "BS Interactive Entertainment / Game Development",
        "BA Communication / Mass Communication",
    ],
}


def all_programs():
    """Flat list of every program name, in catalog order."""
    return [name for names in PROGRAM_CATALOG.values() for name in names]


def category_for(program_name: str) -> str:
    for category, names in PROGRAM_CATALOG.items():
        if program_name in names:
            return category
    return ""
