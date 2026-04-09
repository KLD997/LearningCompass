# LearningCompass MVP

A lightweight, runnable homeschool platform prototype based on the Compass-Learning-style blueprint.

## What is implemented

- Parent dashboard with student-level overview and source-rights snapshot.
- Student dashboard with daily queue and progress bar.
- Assignment completion action.
- Basic legal metadata modeling for content sources.
- SQLite-backed sample data and schema initialization.

## Run

```bash
python app/server.py
```

Then open:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/parent
- http://127.0.0.1:8000/student/1

## Notes

This is an MVP scaffold (single-process WSGI + SQLite) intended for quick iteration.
