#!/usr/bin/env python3
"""LearningCompass MVP homeschool platform.

Run:
  python app/server.py
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path
from string import Template
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "learning_compass.db"
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = db()
    conn.executescript(
        """
        create table if not exists students (
          id integer primary key,
          name text not null,
          grade_math text not null,
          grade_reading text not null
        );

        create table if not exists lessons (
          id integer primary key,
          title text not null,
          subject text not null,
          mode text not null,
          external_url text,
          estimated_minutes integer not null default 15,
          mastery_threshold integer not null default 80
        );

        create table if not exists assignments (
          id integer primary key,
          student_id integer not null references students(id),
          lesson_id integer not null references lessons(id),
          assigned_date text not null,
          status text not null default 'assigned',
          score integer,
          parent_note text
        );

        create table if not exists content_sources (
          id integer primary key,
          name text not null,
          source_url text,
          ownership_type text not null,
          license_type text not null,
          hosting_mode text not null,
          attribution_required integer not null default 0,
          embed_allowed integer not null default 0
        );
        """
    )

    has_data = conn.execute("select count(*) c from students").fetchone()["c"] > 0
    if not has_data:
        conn.executemany(
            "insert into students(name, grade_math, grade_reading) values(?,?,?)",
            [
                ("Ava", "4", "5"),
                ("Eli", "2", "2"),
            ],
        )
        conn.executemany(
            "insert into lessons(title, subject, mode, external_url, estimated_minutes) values(?,?,?,?,?)",
            [
                ("Intro to Fractions", "Math", "hosted_text", None, 15),
                ("Story Elements", "Reading", "hosted_text", None, 20),
                (
                    "Counting Practice",
                    "Math",
                    "external_link",
                    "https://www.khanacademy.org/math/cc-1st-grade-math",
                    15,
                ),
                ("Seed Observation Log", "Science", "offline_activity", None, 10),
            ],
        )
        today = date.today().isoformat()
        conn.executemany(
            "insert into assignments(student_id, lesson_id, assigned_date, status) values(?,?,?,?)",
            [
                (1, 1, today, "in_progress"),
                (1, 2, today, "assigned"),
                (1, 4, today, "assigned"),
                (2, 3, today, "assigned"),
            ],
        )
        conn.executemany(
            """insert into content_sources(name, source_url, ownership_type, license_type, hosting_mode, attribution_required, embed_allowed)
               values(?,?,?,?,?,?,?)""",
            [
                ("Family Authored", None, "original", "owned", "hosted", 0, 1),
                ("Khan Academy", "https://www.khanacademy.org", "third_party", "link_only", "external_link", 1, 0),
            ],
        )
    conn.commit()
    conn.close()


def render_template(name: str, **context: str) -> bytes:
    raw = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
    return Template(raw).safe_substitute(**context).encode("utf-8")


def json_response(start_response, payload: dict, status="200 OK"):
    body = json.dumps(payload).encode("utf-8")
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path.startswith("/static/"):
        file_path = STATIC_DIR / path.removeprefix("/static/")
        if file_path.exists() and file_path.is_file():
            content = file_path.read_bytes()
            ctype = "text/css" if file_path.suffix == ".css" else "text/plain"
            start_response("200 OK", [("Content-Type", ctype), ("Content-Length", str(len(content)))])
            return [content]

    if path == "/":
        body = render_template("index.html")
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [body]

    if path == "/parent":
        conn = db()
        students = conn.execute(
            """
            select s.*, 
            (select count(*) from assignments a where a.student_id = s.id and a.status in ('assigned','in_progress')) as open_count,
            (select count(*) from assignments a where a.student_id = s.id and a.status = 'complete') as complete_count
            from students s order by s.id
            """
        ).fetchall()
        rows = "".join(
            f"<tr><td>{s['name']}</td><td>{s['grade_math']}</td><td>{s['grade_reading']}</td><td>{s['open_count']}</td><td>{s['complete_count']}</td><td><a href='/student/{s['id']}'>Open</a></td></tr>"
            for s in students
        )
        sources = conn.execute("select * from content_sources").fetchall()
        source_rows = "".join(
            f"<tr><td>{r['name']}</td><td>{r['license_type']}</td><td>{r['hosting_mode']}</td><td>{'Yes' if r['attribution_required'] else 'No'}</td><td>{'Yes' if r['embed_allowed'] else 'No'}</td></tr>"
            for r in sources
        )
        conn.close()
        body = render_template("parent.html", student_rows=rows, source_rows=source_rows)
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [body]

    if path.startswith("/student/"):
        student_id = path.split("/")[-1]
        conn = db()
        student = conn.execute("select * from students where id = ?", (student_id,)).fetchone()
        if not student:
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Student not found"]

        assignments = conn.execute(
            """
            select a.id as assignment_id, a.status, l.title, l.subject, l.mode, l.external_url, l.estimated_minutes
            from assignments a
            join lessons l on l.id = a.lesson_id
            where a.student_id = ?
            order by a.id
            """,
            (student_id,),
        ).fetchall()
        conn.close()

        lesson_rows = ""
        for item in assignments:
            action = (
                f"<a class='btn small' href='{item['external_url']}' target='_blank'>Launch</a>"
                if item["mode"] == "external_link"
                else f"<button class='btn small' onclick='markComplete({item['assignment_id']})'>Mark Complete</button>"
            )
            lesson_rows += (
                "<tr>"
                f"<td>{item['title']}</td><td>{item['subject']}</td><td>{item['estimated_minutes']}</td><td>{item['status']}</td><td>{action}</td>"
                "</tr>"
            )

        completed = sum(1 for a in assignments if a["status"] == "complete")
        progress = 0 if not assignments else round((completed / len(assignments)) * 100)

        body = render_template(
            "student.html",
            student_name=student["name"],
            lesson_rows=lesson_rows,
            progress=str(progress),
            student_id=str(student_id),
        )
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [body]

    if path.startswith("/api/assignments/") and path.endswith("/complete") and method == "POST":
        assignment_id = path.split("/")[3]
        conn = db()
        conn.execute("update assignments set status = 'complete' where id = ?", (assignment_id,))
        conn.commit()
        conn.close()
        return json_response(start_response, {"ok": True, "assignment_id": assignment_id})

    if path == "/health":
        return json_response(start_response, {"status": "ok"})

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]


if __name__ == "__main__":
    init_db()
    print("LearningCompass MVP running on http://127.0.0.1:8000")
    with make_server("127.0.0.1", 8000, app) as httpd:
        httpd.serve_forever()
