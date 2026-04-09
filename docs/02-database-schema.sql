-- Compass-Learning Style Homeschool Platform (MVP)
-- PostgreSQL schema

create table users (
  id bigserial primary key,
  name text not null,
  email text not null unique,
  role text not null check (role in ('parent','student','co_parent','tutor','observer','editor','admin')),
  password_hash text not null,
  created_at timestamptz not null default now()
);

create table students (
  id bigserial primary key,
  parent_id bigint not null references users(id) on delete cascade,
  name text not null,
  birthdate date,
  default_grade_band text,
  avatar_ref text,
  active_status boolean not null default true,
  created_at timestamptz not null default now()
);

create table subjects (
  id bigserial primary key,
  name text not null,
  slug text not null unique,
  description text
);

create table tracks (
  id bigserial primary key,
  name text not null,
  track_type text not null,
  subject_id bigint references subjects(id) on delete set null,
  worldview_tag text,
  grade_band text,
  description text
);

create table content_sources (
  id bigserial primary key,
  name text not null,
  source_url text,
  source_kind text not null check (source_kind in ('original','curated_link','embeddable_external','licensed_partner','public_domain','open_license')),
  ownership_type text not null,
  license_type text not null,
  hosting_mode text not null,
  embed_allowed boolean not null default false,
  rehost_allowed boolean not null default false,
  attribution_required boolean not null default false,
  commercial_use_allowed boolean,
  modification_allowed boolean,
  notes text,
  created_at timestamptz not null default now()
);

create table lessons (
  id bigserial primary key,
  title text not null,
  slug text not null unique,
  description text,
  subject_id bigint references subjects(id) on delete set null,
  track_id bigint references tracks(id) on delete set null,
  lesson_mode text not null,
  source_type text not null,
  source_id bigint references content_sources(id) on delete set null,
  hosted_content_ref text,
  external_url text,
  content_body text,
  video_url text,
  estimated_duration_minutes integer,
  difficulty_level text,
  grade_band text,
  age_min integer,
  age_max integer,
  mastery_threshold numeric(5,2),
  worldview_tags jsonb,
  parent_notes text,
  student_notes_enabled boolean not null default true,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table lesson_prerequisites (
  lesson_id bigint not null references lessons(id) on delete cascade,
  prerequisite_lesson_id bigint not null references lessons(id) on delete cascade,
  primary key (lesson_id, prerequisite_lesson_id),
  check (lesson_id <> prerequisite_lesson_id)
);

create table assignments (
  id bigserial primary key,
  student_id bigint not null references students(id) on delete cascade,
  lesson_id bigint not null references lessons(id) on delete cascade,
  assigned_date date not null,
  due_date date,
  status text not null check (status in ('assigned','in_progress','complete','skipped','optional')),
  pacing_mode text not null,
  required_flag boolean not null default true,
  created_at timestamptz not null default now()
);

create table lesson_attempts (
  id bigserial primary key,
  student_id bigint not null references students(id) on delete cascade,
  lesson_id bigint not null references lessons(id) on delete cascade,
  started_at timestamptz,
  completed_at timestamptz,
  score numeric(5,2),
  mastery_status text,
  time_spent_seconds integer,
  created_at timestamptz not null default now()
);

create table assessments (
  id bigserial primary key,
  lesson_id bigint not null references lessons(id) on delete cascade,
  assessment_type text not null,
  passing_score numeric(5,2),
  rubric_json jsonb
);

create table assessment_items (
  id bigserial primary key,
  assessment_id bigint not null references assessments(id) on delete cascade,
  item_type text not null,
  prompt text not null,
  choices_json jsonb,
  answer_key_json jsonb,
  points integer not null default 1
);

create table student_responses (
  id bigserial primary key,
  attempt_id bigint not null references lesson_attempts(id) on delete cascade,
  assessment_item_id bigint not null references assessment_items(id) on delete cascade,
  response_text text,
  response_json jsonb,
  score_awarded numeric(5,2),
  teacher_note text
);

create table content_tags (
  id bigserial primary key,
  tag_name text not null,
  tag_type text not null
);

create table lesson_tags (
  lesson_id bigint not null references lessons(id) on delete cascade,
  tag_id bigint not null references content_tags(id) on delete cascade,
  primary key (lesson_id, tag_id)
);

create table parent_notes (
  id bigserial primary key,
  student_id bigint not null references students(id) on delete cascade,
  lesson_id bigint references lessons(id) on delete set null,
  note_type text not null,
  body text not null,
  created_at timestamptz not null default now()
);

create table achievements (
  id bigserial primary key,
  code text not null unique,
  name text not null,
  description text,
  icon_ref text
);

create table student_achievements (
  student_id bigint not null references students(id) on delete cascade,
  achievement_id bigint not null references achievements(id) on delete cascade,
  awarded_at timestamptz not null default now(),
  primary key (student_id, achievement_id)
);

create index idx_assignments_student_status on assignments(student_id, status);
create index idx_lessons_subject_track on lessons(subject_id, track_id);
create index idx_attempts_student_lesson on lesson_attempts(student_id, lesson_id);
