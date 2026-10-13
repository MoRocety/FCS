"""Catalog identities and ownership helpers shared by student features."""

import hashlib
from flask import current_app, abort
from .identity import current_user


def catalog():
    return current_app.extensions["catalog"].load()


def subjects(data):
    courses, teachers = {}, {}
    for section in data["sections"]:
        key = section["course_key"]
        courses.setdefault(
            key,
            {
                "key": key,
                "name": section["name"],
                "code": f"{section['department']} {section['number']}",
                "department": section["department"],
                "sections": 0,
                "instructors": {},
            },
        )["sections"] += 1
        name = section["instructor"]
        if name.upper() not in ("TBD", "TEAM"):
            teacher_key = hashlib.sha256(name.strip().casefold().encode()).hexdigest()[
                :20
            ]
            teacher = teachers.setdefault(
                teacher_key,
                {
                    "key": teacher_key,
                    "name": name,
                    "code": "Instructor",
                    "department": "",
                    "courses": set(),
                },
            )
            teacher["courses"].add(key)
            courses[key]["instructors"][teacher_key] = name
    return {
        "course": [
            {
                **course,
                "instructors": [
                    {"key": key, "name": name}
                    for key, name in course["instructors"].items()
                ],
            }
            for course in courses.values()
        ],
        "instructor": [
            {**teacher, "courses": sorted(teacher["courses"])}
            for teacher in teachers.values()
        ],
    }


def subject(kind, key):
    if kind not in ("course", "instructor"):
        raise ValueError("Choose a course or instructor")
    result = next((s for s in subjects(catalog())[kind] if s["key"] == key), None)
    if not result:
        abort(404, description="Subject not found in the current catalog")
    return result


def owned(connection, table, identity):
    row = connection.execute(
        f"SELECT * FROM {table} WHERE id=? AND owner_id=?",
        (identity, current_user()["id"]),
    ).fetchone()
    if not row:
        abort(404)
    return row
