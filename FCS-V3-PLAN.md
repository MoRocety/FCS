# FCS V3 — Complete Build Plan

## 1. Project Structure

```
fcs-v3/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── deps.py              # Depends(get_db), Depends(get_current_user)
│   │   ├── domains/
│   │   │   ├── __init__.py
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py    # /auth/google, /auth/callback, /auth/me, /auth/logout
│   │   │   │   ├── models.py    # User
│   │   │   │   ├── schemas.py   # UserRead, UserCreate
│   │   │   │   └── service.py   # create_or_login_user()
│   │   │   └── scheduling/
│   │   │       ├── __init__.py
│   │   │       ├── models.py    # Department, Course, Section, SectionSchedule, SavedSchedule, Term
│   │   │       ├── schemas.py   # DepartmentRead, CourseRead, SectionRead, etc.
│   │   │       ├── router.py    # /departments, /courses, /sections, /generate
│   │   │       └── service.py   # generate_combinations(), import_courses()
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # async engine, sessionmaker, Base
│   │   │   └── security.py      # OAuth token handling, cookie management
│   │   └── scraper/
│   │       ├── __init__.py
│   │       ├── scrape.py        # Port from V1, async version
│   │       ├── parse.py         # Port from V1, async version
│   │       └── pipeline.py      # scrape -> parse -> import to DB
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout, providers
│   │   │   ├── page.tsx         # Landing / course catalog
│   │   │   ├── schedule/
│   │   │   │   └── page.tsx     # Schedule builder page
│   │   │   └── saved/
│   │   │       └── page.tsx     # Saved schedules page
│   │   ├── components/
│   │   │   ├── ui/              # shadcn components
│   │   │   ├── Navbar.tsx
│   │   │   ├── CourseTable.tsx  # Paginated course list
│   │   │   ├── FilterChips.tsx  # Department/instructor chips
│   │   │   ├── SearchInput.tsx  # Search-as-you-type
│   │   │   ├── CreditSlider.tsx # Min/max credit range
│   │   │   ├── ScheduleGrid.tsx # Visual timetable
│   │   │   ├── ComboNav.tsx     # Prev/next schedule navigation
│   │   │   └── AuthButton.tsx   # Google sign-in button
│   │   ├── lib/
│   │   │   ├── api.ts           # fetch wrapper
│   │   │   └── utils.ts         # cn(), formatTime()
│   │   └── hooks/
│   │       └── useGenerate.ts   # SSE hook for combination generation
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
├── scraper/                      # GitHub Actions cron (port from V1)
│   ├── scrape.py
│   ├── parse.py
│   ├── send_webhook.py
│   └── master.py
└── docker-compose.yml            # Local dev: postgres, backend, frontend
```

## 2. Database Schema (PostgreSQL)

```sql
-- Terms
CREATE TABLE terms (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,     -- "2026FA"
    display_name VARCHAR(100) NOT NULL,   -- "2026 Fall"
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    abbreviation VARCHAR(10) UNIQUE NOT NULL,  -- "BIOL"
    name VARCHAR(200),                         -- "Biology" (nullable, can populate later)
    term_id INT REFERENCES terms(id)
);

-- Courses
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    department_id INT REFERENCES departments(id),
    code VARCHAR(20) NOT NULL,              -- "101", "699A"
    title VARCHAR(300) NOT NULL,            -- "Introduction to Art"
    credits INT NOT NULL,                   -- 3 (always int, V1 uses int(float()))
    term_id INT REFERENCES terms(id),
    UNIQUE(department_id, code, term_id)
);

-- Sections
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id),
    section_code VARCHAR(10) NOT NULL,      -- "A", "B", "IS"
    instructor VARCHAR(200),                -- "S Kamran" or "TBD"
    classroom VARCHAR(50),                  -- "SBLOCKS008"
    total_seats INT,
    available_seats INT,
    term_id INT REFERENCES terms(id),
    UNIQUE(course_id, section_code, term_id)
);

-- Section schedules (primary + alternate in same table via schedule_type)
CREATE TABLE section_schedules (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id),
    schedule_type VARCHAR(10) NOT NULL,     -- "primary" or "secondary"
    days VARCHAR(20) NOT NULL,              -- "MWF", "TR" (normalized from ['M','W','F'])
    start_time TIME NOT NULL,               -- 12:00:00
    end_time TIME NOT NULL,                 -- 12:50:00
    UNIQUE(section_id, schedule_type)
);

-- Saved schedules (requires auth)
CREATE TABLE saved_schedules (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    term_id INT REFERENCES terms(id),
    name VARCHAR(200),                      -- "Fall 2026 Plan A"
    section_ids INT[] NOT NULL,             -- PostgreSQL array of section IDs
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Users (Google OAuth)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    name VARCHAR(200),
    picture_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT now(),
    last_login TIMESTAMPTZ
);

-- Notifications (phase 3)
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,              -- "seat_alert", "schedule_reminder"
    title VARCHAR(300) NOT NULL,
    message TEXT,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- User notification preferences
CREATE TABLE notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    push_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT true,
    seat_alerts BOOLEAN DEFAULT true,
    schedule_reminders BOOLEAN DEFAULT true
);
```

## 3. API Endpoints

### Auth (domain: `/auth`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth/login` | Redirect to Google OAuth |
| GET | `/auth/callback` | Handle Google callback, set cookie, create/update user |
| GET | `/auth/me` | Return current user (or 401) |
| POST | `/auth/logout` | Clear cookie, return 200 |

### Scheduling (domain: `/api`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/departments` | List departments (with course counts) |
| GET | `/api/courses` | List courses (filterable by dept, search, instructor) |
| GET | `/api/sections` | List sections (filterable by course, dept) |
| POST | `/api/generate` | Generate schedules — returns SSE stream |
| GET | `/api/saved-schedules` | List user's saved schedules (auth required) |
| POST | `/api/saved-schedules` | Save a schedule (auth required) |
| DELETE | `/api/saved-schedules/{id}` | Delete saved schedule (auth required) |

### Scraper (internal)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/webhook/update-courses` | Receive scraped data from GitHub Actions |

### `POST /api/generate` — SSE Stream Contract

**Request body:**
```json
{
  "selected_sections": [1, 2, 3, 4, 5],      // section IDs
  "credit_min": 15,
  "credit_max": 17,
  "crucial_courses": ["BIOL100", "CHEM201"],  // optional: must-include courses
  "filters": {                                 // optional
    "exclude_days": ["F"],
    "max_courses": 6,
    "instructor_blacklist": ["Some Prof"]
  }
}
```

**SSE events:**
```
event: progress
data: {"generated": 1200, "filtered": 1150, "elapsed_ms": 340}

event: schedule
data: {"index": 1, "sections": [{"id": 1, "course": "BIOL100-A", "days": "MWF", "start": "12:00", "end": "12:50"}, ...], "credits": 16}

event: done
data: {"total": 1150, "elapsed_ms": 2340}
```

## 4. Week-by-Week Breakdown

### Weeks 1-2: Foundation
- [ ] Initialize FastAPI project, configure async SQLAlchemy + Alembic
- [ ] Create all DB models, run first migration
- [ ] Set up `docker-compose.yml` with Postgres + pgAdmin
- [ ] Port `scrape.py` and `parse.py` to backend, test data import
- [ ] Initialize Next.js project with App Router, Tailwind, shadcn/ui
- [ ] Create basic layout: navbar, footer, responsive shell

### Weeks 3-4: Course Catalog
- [ ] `GET /api/departments` with course counts
- [ ] `GET /api/courses` with search, department filter, instructor filter
- [ ] Paginated `CourseTable` component (server component)
- [ ] `FilterChips` for department selection
- [ ] `SearchInput` with debounced search-as-you-type
- [ ] Wire up course selection → section list flow

### Weeks 5-6: Schedule Generation
- [ ] Port `credit_check`, `clash_check`, `duplicate_checker`, `crucial` to `service.py`
- [ ] Implement SSE streaming with `StreamingResponse` + `asyncio.to_thread()`
- [ ] `CreditSlider` (min/max range)
- [ ] `ScheduleGrid` visual timetable component (Mon-Fri, 8AM-8PM)
- [ ] `ComboNav` for navigating generated schedules
- [ ] Wire frontend `useGenerate` hook to SSE stream

### Weeks 7-8: Authentication
- [ ] Google OAuth via Authlib
- [ ] Set httpOnly secure cookie on callback
- [ ] `User` model, create-or-login on callback
- [ ] `AuthButton` component (Google sign-in / user avatar)
- [ ] Protected route middleware for saved schedules

### Weeks 9-10: Saved Schedules
- [ ] `POST /api/saved-schedules` (save current combo)
- [ ] `GET /api/saved-schedules` (list saved)
- [ ] `DELETE /api/saved-schedules/{id}`
- [ ] Saved schedules page with grid preview
- [ ] Quick-load: click saved schedule → populate grid

### Weeks 11-12: Notifications
- [ ] Web Push API subscription + service worker
- [ ] Resend email integration
- [ ] Seat monitoring cron job (check available_seats)
- [ ] Notification preferences page
- [ ] Push + email delivery on seat availability change

### Weeks 13-14: Migration & Polish
- [ ] Migrate V1 data to PostgreSQL
- [ ] Configure V1 PythonAnywhere to 301 redirect to V3
- [ ] Deploy backend to Railway, frontend to Vercel
- [ ] Responsive design pass (mobile schedule grid)
- [ ] Error handling, loading states, empty states
- [ ] Performance testing with real data volume

### Phase 4 (Weeks 15+): Advanced Features
- [ ] Boolean algebra drag-and-drop constraint builder
- [ ] Soft constraints / scoring / ranking
- [ ] Side-by-side plan comparison
- [ ] PDF/PNG schedule export
- [ ] Open source docs, README, CONTRIBUTING

---

## 5. Addendum — Long-Term Ecosystem Vision

### 5.1 User Management (Priority)

User management is the foundation for everything else. Every feature below depends on knowing who the user is and what they've done.

**Enhanced user model:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    name VARCHAR(200),
    picture_url VARCHAR(500),
    university_id INT REFERENCES universities(id),  -- multi-uni support
    major VARCHAR(100),
    expected_graduation DATE,
    course_history JSONB,       -- {"BIOL101": {"grade": "A", "semester": "2025FA"}, ...}
    role VARCHAR(20) DEFAULT 'student',  -- 'student', 'admin', 'moderator'
    reputation INT DEFAULT 0,  -- earned from contributions
    created_at TIMESTAMPTZ DEFAULT now(),
    last_login TIMESTAMPTZ
);
```

**Why this matters:** The user profile becomes the input vector for recommendations. Course history + major + graduation timeline = what courses they need next. Upvote/downvote patterns = which instructors are good. Saved schedules = what their priorities are (early classes? no Fridays?).

### 5.2 Community Features

**Upvote/Downvote Schedules:**
- Users can publish schedules to the community
- Other users upvote/downvote based on quality, time slots, instructor choices
- Top-voted schedules surface as "recommended" for new students

```sql
CREATE TABLE published_schedules (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    term_id INT REFERENCES terms(id),
    name VARCHAR(200),
    description TEXT,
    section_ids INT[] NOT NULL,
    upvotes INT DEFAULT 0,
    downvotes INT DEFAULT 0,
    views INT DEFAULT 0,
    is_featured BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE schedule_votes (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    schedule_id INT REFERENCES published_schedules(id),
    vote_type VARCHAR(10) NOT NULL,  -- 'up' or 'down'
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, schedule_id)
);
```

**Favorites/Shares:**
- Users favorite schedules they like (separate from voting)
- Shareable links: `/schedule/shared/{uuid}`
- "Fork" feature: copy someone else's schedule to your own saved list

### 5.3 Teacher & Course Reviews

**Instructor Reviews:**
```sql
CREATE TABLE instructor_reviews (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    section_id INT REFERENCES sections(id),  -- ties to specific term/section
    instructor_name VARCHAR(200) NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    difficulty INT CHECK (difficulty >= 1 AND difficulty <= 5),
    workload INT CHECK (workload >= 1 AND workload <= 5),
    grade_received VARCHAR(5),  -- "A", "B+", etc.
    would_recommend BOOLEAN,
    review_text TEXT,
    upvotes INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, section_id)  -- one review per section per user
);
```

**Course Reviews:**
```sql
CREATE TABLE course_reviews (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    course_id INT REFERENCES courses(id),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    difficulty INT CHECK (difficulty >= 1 AND difficulty <= 5),
    workload INT CHECK (workload >= 1 AND workload <= 5),
    grade_received VARCHAR(5),
    would_recommend BOOLEAN,
    review_text TEXT,
    upvotes INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, course_id)
);
```

**Aggregated stats (computed, not stored):**
- `avg_rating` = avg of all ratings for instructor/course
- `avg_difficulty` = avg of difficulty ratings
- `recommendation_rate` = % who said would_recommend
- Displayed on course cards and instructor profiles

### 5.4 Forum

**Thread-based forum tied to courses/instructors:**
```sql
CREATE TABLE forum_threads (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    course_id INT REFERENCES courses(id),     -- optional: thread about a course
    instructor_id INT,                        -- optional: thread about instructor
    title VARCHAR(300) NOT NULL,
    body TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT false,
    is_locked BOOLEAN DEFAULT false,
    upvotes INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE forum_replies (
    id SERIAL PRIMARY KEY,
    thread_id INT REFERENCES forum_threads(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id),
    body TEXT NOT NULL,
    upvotes INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**Forum categories auto-generated from courses:**
- `/forum/biol101` → threads about BIOL101
- `/forum/instructor/s-kamran` → threads about Prof. Kamran
- `/forum/general` → off-topic, advice, etc.

### 5.5 AI/ML Pipeline

**Data collected from user behavior:**
- Schedules saved/generated → time slot preferences, course load preferences
- Upvotes/downvotes on schedules → which combinations work
- Reviews (instructor + course) → quality signals
- Course history + grades → difficulty progression, grade distribution
- Search patterns → what students look for

**Phase 1 — Recommendation Engine (Rules-based first, ML later):**
- "Students who took X also took Y" (collaborative filtering)
- "This instructor has 4.2 rating from 150 reviews" (aggregated reviews)
- "This course is hard — avg difficulty 4.5, avg grade B-" (review data)
- "Most popular schedule for BIOL majors in Fall" (saved schedule patterns)

**Phase 2 — ML Models:**
- **Grade prediction:** Given course history + grades → predict likely grade in target course
- **Schedule optimization:** Given constraints + preferences → rank schedules by predicted satisfaction
- **Instructor recommendation:** Given student learning style + course → recommend best-matched instructor
- **Prerequisite gap detection:** Given course history → flag missing prerequisites

**Phase 3 — Chatbot:**
- "I'm a Bio major, what should I take next semester?"
- "Which instructor is better for CHEM201 — Dr. A or Dr. B?"
- "Can I handle 18 credits with these courses?"
- Powered by RAG: course catalog + reviews + user history → LLM generates answer

### 5.6 Degree Audit & Planning

**Degree tracking:**
```sql
CREATE TABLE degree_requirements (
    id SERIAL PRIMARY KEY,
    university_id INT REFERENCES universities(id),
    major VARCHAR(100) NOT NULL,
    catalog_year INT NOT NULL,          -- "2026" catalog
    requirements JSONB NOT NULL,        -- structured requirement tree
    total_credits_required INT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**User's degree progress:**
```sql
CREATE TABLE student_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    degree_requirement_id INT REFERENCES degree_requirements(id),
    completed_courses JSONB,   -- {"BIOL101": {"grade": "A", "term": "2025FA"}, ...}
    in_progress_courses JSONB, -- {"CHEM201": {"term": "2026FA"}, ...}
    total_credits_earned INT,
    gpa DECIMAL(3,2),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

**Predictive recommendations based on degree audit:**
- "You need 3 more science electives to graduate"
- "Based on your schedule, you can graduate in Spring 2027"
- "This course is only offered Fall — take it now or wait a year"
- "Your GPA will likely drop if you take CHEM301 + PHYS202 together"

### 5.7 Multi-University Expansion

**University model:**
```sql
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,        -- "FCC" / "University of X"
    slug VARCHAR(50) UNIQUE NOT NULL,  -- "fcc" / "university-of-x"
    domain VARCHAR(200),               -- "fccollege.edu" (for email verification)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**Architecture for multi-uni:**
- All models gain a `university_id` foreign key (departments, courses, sections, terms)
- Scraper becomes configurable per university (different SIS = different parser)
- Frontend shows university selector on first visit
- Auth can be scoped: Google OAuth + email domain verification
- Users can belong to multiple universities (transfer students, grad students)

**Scaling strategy:**
- Start with FCC (one university, proven data source)
- Add university: new scraper config + new DB seed + university flag in UI
- Community features scale naturally: reviews, votes, and forum are per-university
- ML models can be university-specific or cross-university (depends on data volume)

### 5.8 Priority-Ordered Implementation Roadmap

| Phase | Features | Timeline |
|-------|----------|----------|
| **V1 (Now)** | Scheduling engine, course catalog, basic auth, saved schedules | Weeks 1-10 |
| **V2 (Soon)** | Notifications, seat monitoring | Weeks 11-12 |
| **V3 (Launch)** | Migration, polish, deploy | Weeks 13-14 |
| **Phase 4** | Boolean constraints, soft scoring, plan comparison, PDF export | Weeks 15-18 |
| **Phase 5** | Published schedules, upvote/downvote, favorites, sharing | Weeks 19-22 |
| **Phase 6** | Instructor reviews, course reviews | Weeks 23-26 |
| **Phase 7** | Forum | Weeks 27-30 |
| **Phase 8** | Course history input, degree planning, prerequisite tracking | Weeks 31-36 |
| **Phase 9** | Recommendation engine (rules-based) | Weeks 37-40 |
| **Phase 10** | ML models, chatbot | Weeks 41+ |
| **Phase 11** | Multi-university expansion | Ongoing |

### 5.9 Data Moat

Every feature generates data that makes the platform more valuable:
- **Saved schedules** → know what combinations students actually want
- **Upvotes/downvotes** → know which schedules are good
- **Reviews** → know which instructors/courses are good
- **Forum** → know what students struggle with
- **Course history** → know grade distributions, difficulty progression
- **Search patterns** → know what students look for

This data feeds the ML pipeline, which feeds better recommendations, which attracts more users, which generates more data.

---

## 6. Genuinely Exciting Features

These are the differentiating ideas that go beyond basic scheduling. Each one is data-dependent — the more students use the platform, the better they get.

### 6.1 Schedule Difficulty Heatmap

A visual 4-year calendar showing semester-by-semester difficulty for a student's major. Color-coded red/yellow/green based on:
- Average credit load for that semester
- Average course difficulty from reviews
- Average GPA of students who took that combination
- Historical grade distributions

Example: A bio major sees Fall of junior year is red — "CHEM301 + BIOL310 + PHYS201, avg GPA 2.4 for students who took all three." The system suggests shuffling courses to smooth the load.

**DB schema:**
```sql
CREATE TABLE semester_difficulty (
    id SERIAL PRIMARY KEY,
    university_id INT REFERENCES universities(id),
    major VARCHAR(100) NOT NULL,
    catalog_year INT NOT NULL,
    semester VARCHAR(20) NOT NULL,      -- "Fall Junior", "Spring Senior"
    avg_difficulty DECIMAL(3,2),
    avg_gpa DECIMAL(3,2),
    avg_credits DECIMAL(3,1),
    top_courses JSONB,                  -- most common courses in this semester
    sample_size INT,                    -- how many students this data represents
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**Why it's special:** No scheduling tool does this. It turns abstract course selection into "what will my life actually feel like over 4 years."

### 6.2 Instructor Effectiveness Index

Not just a star rating. A multi-dimensional index built from:
- **Quality rating:** 1-5 from student reviews
- **Difficulty rating:** 1-5 from student reviews
- **First-time pass rate:** % of students who passed without retaking
- **Grade distribution:** A/B/C/D/F breakdown
- **Retake rate:** How many students needed to retake with a different instructor
- **Downstream performance:** Did students who took this instructor do better in the next course?

Display as: "Dr. Smith: Quality 4.2/5, Difficulty 3.1/5, Pass rate 92%, Avg grade B+. Dr. Jones: Quality 3.8/5, Difficulty 4.5/5, Pass rate 71%, Avg grade C+."

**DB schema:**
```sql
CREATE TABLE instructor_effectiveness (
    id SERIAL PRIMARY KEY,
    instructor_name VARCHAR(200) NOT NULL,
    university_id INT REFERENCES universities(id),
    course_id INT REFERENCES courses(id),    -- can be course-specific
    quality_rating DECIMAL(3,2),
    difficulty_rating DECIMAL(3,2),
    first_time_pass_rate DECIMAL(5,2),
    avg_grade DECIMAL(3,2),
    grade_distribution JSONB,                -- {"A": 15, "B": 30, "C": 25, "D": 15, "F": 15}
    retake_rate DECIMAL(5,2),
    downstream_performance JSONB,            -- avg grades in prerequisite courses
    review_count INT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

**Why it's special:** Aggregated reviews are noisy. The pass rate and downstream performance metrics are signals no competitor has. This is the kind of data that makes a student say "oh, this tool actually knows what it's talking about."

### 6.3 Grade Distribution Data

**Source options (ranked by reliability):**
1. **Self-reported from users:** When students input course history, they provide grades. Unreliable at small scale, but becomes statistical as volume grows. Add confidence intervals: "Based on 47 self-reported grades."
2. **Scraped from public sources:** Some universities publish grade distributions in course catalogs or through public records requests. FCC may have this data available.
3. **Inferred from reviews:** When users review a course and say "I got a B+", that's a data point. Aggregate across reviews.
4. **Partnerships:** Long-term, partner with registrar offices to get official grade distributions.

**DB schema:**
```sql
CREATE TABLE grade_distributions (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id),
    instructor_name VARCHAR(200),
    term_id INT REFERENCES terms(id),
    university_id INT REFERENCES universities(id),
    distribution JSONB NOT NULL,        -- {"A": 12, "B": 25, "C": 18, "D": 8, "F": 3}
    total_students INT,
    source VARCHAR(20) NOT NULL,        -- "self-reported", "scraped", "inferred", "official"
    confidence DECIMAL(3,2),            -- 0.0 to 1.0 based on sample size
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**Why it's special:** Grade distributions are the single most useful piece of data for course selection. If you can build a reliable database of them, students will come for this alone.

### 6.4 Course History Input

Users input their completed courses + grades. This is the foundation for personalized recommendations.

**Input flow:**
1. "What's your major?" → dropdown
2. "What year are you?" → Freshman/Sophomore/Junior/Senior
3. "Enter courses you've completed" → search-as-you-type, add grade per course
4. Optional: "Import from transcript" → CSV/PDF upload, parse with LLM (future)

**What it enables:**
- "You've taken BIOL101, CHEM101, MATH201. Based on your Bio major, here are courses you should consider next."
- "Your GPA in science courses is 3.4. Students with similar GPAs who took CHEM301 got avg B+."
- "You're missing MATH301 as a prerequisite for BIOL310. Here's the path."

**DB schema:**
```sql
CREATE TABLE course_history (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    course_id INT REFERENCES courses(id),
    grade VARCHAR(5),                -- "A", "B+", "IP" (in progress)
    term_taken VARCHAR(10),          -- "2025FA"
    is_transfer BOOLEAN DEFAULT false,
    transfer_institution VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, course_id)
);
```

### 6.5 Smart Waitlist Strategy

Not just "monitor seats" but play the game strategically:
- **Seat velocity:** "CHEM201-A has 1 seat left. Losing ~1 seat/day. Will be full by Thursday."
- **Waitlist odds:** "3 people on waitlist. Historical data: 60% chance a seat opens before add/drop ends."
- **Safe alternative:** "CHEM201-B has 4 seats, nobody on waitlist. Safer bet."
- **Auto-swap:** "If a seat opens in CHEM201-A, we'll auto-enroll you and swap your current section. You won't lose a spot."

**DB schema:**
```sql
CREATE TABLE seat_history (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(id),
    available_seats INT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT now()
);
```

**Why it's special:** This is tactical. Students tell their friends about tools that solve immediate, painful problems. Waitlist anxiety is one of those problems.

### 6.6 Schedule Compatibility Match

"Find me a schedule that works for me AND my study group."
- Input 2-4 friends' constraints (credit range, preferred days, blocked times)
- System generates schedules where:
  - They share at least 1 free block for group study
  - No one has a conflict
  - Optionally: they're in the same section of a course
- Social feature: invite friends via link, they enter their constraints

**Why it's special:** This is social + practical. Students actually care about coordinating with friends. It's also a growth mechanism — you need to invite friends to use it.

### 6.7 Course Load Simulator

Before committing, simulate the actual week:
- **Daily time blocks:** "Monday: 8AM-3PM straight, no break. Tuesday: free until 2PM, then 2PM-6PM."
- **Weekly workload estimate:** "Expect ~25 hours/week based on historical data for these courses."
- **Exam/paper calendar:** "Week 8 has 3 midterms. Week 12 has 2 papers due."
- **Energy estimate:** "Your hardest day is Wednesday — 2 labs + 1 lecture. Consider moving one."

**Why it's special:** Turns abstract credit numbers into "what will my life actually feel like?"

### 6.8 Schedule History + Patterns

Meta-data from aggregated user behavior:
- "Last year, 847 students created schedules with CHEM201. Here are the most popular patterns:"
  - 34% took it with BIOL101 + MATH201 (avg GPA: 3.1)
  - 22% took it with PHYS101 + MATH201 (avg GPA: 2.8)
  - 18% took it alone as their only science (avg GPA: 3.6)
- "Students who took CHEM201 + PHYS201 together had avg GPA 2.6. Consider spreading them out."

**Why it's special:** This is meta-data that only exists if you have the scheduling data. It's your moat. Every student who uses the tool adds to it.

---

## 7. Creative Features

These are the ideas that make people screenshot and send to friends.

### 7.1 Schedule Archetypes

Stop making students build from scratch. Let them pick a vibe:
- **The 4-Day Weekend** — no Friday classes
- **The Morning Bird** — classes done by 1PM
- **The Late Riser** — no classes before 11AM
- **The Balanced Life** — spread evenly, no back-to-back
- **The Grindset** — compact all classes into 2-3 days, rest free
- **The No-Death-Day** — no 3+ consecutive classes

The system generates schedules matching the archetype and scores each one. Marketable because it's instantly relatable.

### 7.2 Schedule Tournament

Generate 8 candidate schedules. Show them bracket-style. User picks A vs B in each round until one wins. Turns a stressful decision into a 30-second game. The data also tells you which tradeoffs users actually care about.

### 7.3 "What If" Simulator

Let students perturb any schedule and instantly see consequences:
- "What if I swap CHEM201-A for CHEM201-B?"
- "What if I drop this course?"
- "What if I move everything 30 minutes later?"

Show side-by-side: credit hours, difficulty score, free time, commute load, exam density. Makes exploration addictive.

### 7.4 Study Buddy Matcher

Match users in the same section who opt in. "3 other students in CHEM201-A are looking for a study group. Want an intro?" Optional, privacy-respecting, course-section-specific. Huge retention play.

### 7.5 Schedule Aesthetic Score

Purely algorithmic: reward clean grids, minimal weird gaps, compact days, consistent start times. Some students deeply care that their schedule *looks* good. Show a score: "8.7/10 — nice clean blocks."

### 7.6 Room Quality Intel

Crowdsourced classroom reviews:
- "SBLOCKS008 has no windows, broken AC"
- "SBLOCKS312 has natural light and outlets at every seat"
- "Lab 4 computers are slow"

Use it as a soft constraint: "Prefer classrooms rated 4+ stars."

### 7.7 Textbook Cost Estimator

Aggregate required textbooks per section and total the cost per schedule. "This schedule costs $410 in books. This alternative costs $165." Could affiliate-link to cheaper versions. Actually saves students money.

### 7.8 Commute-Aware Scheduling

Student inputs where they live (on-campus dorm / off-campus address). Factor real walking/driving time between buildings into clash detection. "You have 10 minutes between these classes but it's a 14-minute walk. This schedule won't work."

### 7.9 "Will It Fill?" Predictions

Train a tiny model on seat history:
- "CHEM201-A has 4 seats left. Based on velocity, 78% chance it's full by tomorrow."
- "BIOL310 filled in 3 days last year. Register soon."
- "This section usually has last-minute drops — waitlist is worth it."

Gamify it with confidence intervals.

### 7.10 Professor Consistency Tracker

"Dr. Smith has taught MWF 10:00-10:50 for 6 consecutive semesters. If you like them, you can plan future semesters around this slot." Useful for returning students planning multi-term.

### 7.11 Course Substitution Finder

"I need a humanities elective." System shows all qualifying courses, ranked by difficulty, instructor quality, time fit, and seat availability. One click adds the best fit.

### 7.12 Reverse Schedule Builder

"I want to graduate in 3 years with a CS degree." System works backward from degree requirements and generates the entire 6-semester plan. Then lets you drag-and-drop to customize.

### 7.13 Schedule Stress Test

Run worst-case scenarios:
- "If you miss Tuesday, you miss 2 lectures and 1 lab. Recovery cost: high."
- "Week 6 has 4 exams. Consider moving one course."
- "No free day + 3 labs = burnout risk."

### 7.14 Semester Wrapped

End-of-semester personalized summary:
- "You spent 22 hours/week in class."
- "Your hardest week had 4 exams."
- "You saved 4 schedules before choosing one."
- "Your most-generated course was CHEM201."

Shareable. Viral. Students love this format.

### 7.15 Anonymous Schedule Critique

Post your schedule, community roasts or validates it. "18 credits + O-Chem + lab? Brave." "Solid, but move BIOL101 to morning." Low-effort community content.

### 7.16 Professor Hunter

Set preferences for instructor traits: "explains concepts clearly," "easygoing grader," "challenging but fair," "no group projects," "accessible office hours." System matches you to instructors and sections. Like dating app matching for professors.

### 7.17 Meal / Prayer / Gym Time Protector

User defines protected time blocks. System refuses to generate schedules that violate them. "Keep my lunch hour free." "No classes during Jummah." "Gym time 4-6PM protected."

### 7.18 Schedule Trading / Seat Swap

When a student drops a watched section, the system can offer the seat to someone else in the same watch group. Optional, fair queue. Solves the "refresh the page at 3AM" problem.

### 7.19 Course Workload DNA

Break down each course by assessment type from reviews/syllabi:
- "40% exams, 30% problem sets, 30% final project"
- "Heavy memorization"
- "Group work required"
- "Attendance mandatory"

Then warn when a schedule has too many of the same workload type.

### 7.20 Predictive Drop Risk

Based on user's course history + planned schedule difficulty, estimate: "Students with your GPA and this schedule have a 34% chance of dropping or withdrawing from at least one course." Flag it before they register.

### 7.21 Professor Office Hours Alignment

Not just when they teach — when they're available to help. "Dr. Smith holds office hours MWF 2-3PM. If you're struggling, this section aligns with their office hours." Factor this into section selection: a slightly worse time slot might be worth it if office hours line up with your free blocks.

### 7.22 Course Grade Trajectory

Track how a course's grade distribution changes over time. "CHEM201 avg grade was B+ in 2023, dropped to C+ in 2024 after curriculum change." Warns students when a course is getting harder. Useful for comparing sections across semesters.

### 7.23 Social Proof on Schedules

"This exact schedule has been generated by 23 other students this week. 18 of them saved it." Shows which schedules are popular and validated by peers. Builds trust: "If 18 students saved this, it's probably good."

### 7.24 Schedule Health Score

A single composite score (0-100) for any schedule, combining:
- Time conflict risk
- Commute feasibility
- Workload balance
- Grade prediction
- Seat availability urgency

One number to rule them all. "Your schedule scores 82/100. Solid, but the Wednesday commute is tight."

### 7.25 Exam Conflict Detector

Beyond time clashes — detect exam scheduling conflicts. "MATH201 and CHEM101 both have midterms on Oct 15. Two exams in one day." Pulls from syllabi data or historical exam patterns. Critical for students who don't think about this until it's too late.

### 7.26 Instructor Schedule History

"Dr. Jones has taught this course 4 times. Here's how grade distributions differed:
- Fall 2024: 12 A's, 20 B's, 8 C's (easier semester)
- Spring 2025: 5 A's, 10 B's, 15 C's, 5 D's (harder semester)"

Helps students pick the right semester for a specific instructor.

### 7.27 Schedule Comparison Engine

Side-by-side comparison of two schedules with pros/cons:
- "Schedule A: earlier classes, more free days, harder instructors"
- "Schedule B: later starts, compact days, easier instructors"
- "Schedule A scores 78/100. Schedule B scores 85/100."

Takes the guesswork out of choosing between two good options.

---

## 8. Agentic Platform — Cursor for University Management

Not a chatbot. Not a cron job. A conversational agent that the user directs with natural language to manage their entire university experience. Like Cursor manages your codebase — this manages your academic life.

### 8.1 The Agent Loop

```
User types prompt
    ↓
Agent reads user context (profile, history, preferences, current schedule)
    ↓
Agent reasons about what tools to call
    ↓
Agent calls tools (search, generate, save, monitor, compare)
    ↓
Agent returns results + explanation
    ↓
User follows up with another prompt
    ↓
Agent continues the conversation
```

The agent is stateful. It remembers the conversation, the user's profile, and their preferences across sessions. Every interaction makes it smarter about that specific student.

### 8.2 UI — Chat Interface

A sidebar or floating panel, like Cursor's chat. Persistent across the app. The agent can also surface proactive suggestions contextually:

- User is browsing course catalog → agent says "I notice you're looking at CHEM201. Want me to find the best section?"
- User is viewing a schedule → agent says "This scores 78/100. Want me to generate alternatives?"
- User is on a instructor page → agent says "This instructor has 4.2/5 quality but only 71% pass rate. Want to see alternatives?"

### 8.3 Available Tools

The agent has access to these primitives. It reasons about which to call based on user intent:

| Tool | Description |
|------|-------------|
| `search_courses(dept, keywords, filters)` | Query the course catalog |
| `get_sections(course_id, term)` | Get all sections for a course |
| `get_seats(section_id)` | Fetch current seat availability |
| `get_instructor_info(name)` | Pull instructor ratings, reviews, effectiveness index |
| `get_grade_distribution(course_id, instructor)` | Fetch grade data |
| `generate_schedules(constraints)` | Run combination engine |
| `check_clashes(schedule)` | Validate a schedule for conflicts |
| `estimate_workload(schedule)` | Calculate weekly hours, exam density |
| `calculate_commute(schedule, user_location)` | Add travel time between buildings |
| `compare_schedules(schedule_a, schedule_b)` | Side-by-side comparison with scores |
| `score_schedule(schedule)` | Health score (0-100) composite |
| `save_schedule(user_id, section_ids, name)` | Persist a schedule |
| `share_schedule(user_id, schedule_id)` | Generate shareable link |
| `enroll_in_section(section_id)` | Auto-enroll via SIS API (if integrated) |
| `waitlist_section(section_id)` | Join waitlist via SIS API |
| `drop_section(section_id)` | Drop via SIS API |
| `swap_sections(from_id, to_id)` | Drop one, enroll in another |
| `add_to_watchlist(section_id, trigger)` | Monitor section for changes |
| `remove_from_watchlist(section_id)` | Stop monitoring |
| `notify_user(title, message, method)` | Send push/email/sms |
| `import_transcript(file)` | Parse uploaded transcript PDF/CSV |
| `update_course_history(user_id, courses)` | Batch update completed courses |
| `get_semester_difficulty(major, term)` | Pull heatmap data |
| `find_substitution(user_id, requirement_type)` | Find courses satisfying a gen-ed |
| `find_study_buddies(section_id, user_id)` | Match nearby students in same section |
| `predict_seat_fill(section_id)` | ML prediction of fill time |
| `get_schedule_patterns(course_id)` | Aggregated scheduling data |
| `post_review(user_id, section_id, rating, text)` | Submit instructor review |
| `post_to_forum(course_id, title, body)` | Create forum thread |

### 8.4 Example Conversations

**Conversation 1: Building a schedule**
```
User: I'm a bio major, need 15-17 credits for spring

Agent: I see you've completed BIOL101, CHEM101, and MATH201. Based on your
major, here are courses to consider for spring:
- BIOL201 (Cell Biology) - 4 credits
- CHEM201 (Organic Chemistry) - 3 credits
- MATH301 (Statistics) - 3 credits
- ENGL201 (Academic Writing) - 3 credits

Want me to generate schedules with these?

User: yeah but skip anything on fridays

Agent: Generating schedules with no Friday classes... Found 12 options.
Here are the top 3 by health score:

1. Score 87/100 — MWF 9-10:50, T/Th 10-11:50
   BIOL201 + CHEM201 + MATH301 + ENGL201 (16 credits)
   Avg instructor rating: 4.1/5

2. Score 82/100 — MWF 11-12:50, T/Th 1-2:50
   Same courses, later start
   Avg instructor rating: 3.8/5

3. Score 79/100 — T/Th only (compact)
   BIOL201 + CHEM201 + MATH301 + ENGL201
   Avg instructor rating: 3.9/5

Want me to save any of these?

User: save #1 as "Spring 2027 Plan A"

Agent: Saved. Want me to add any of these to your watchlist?

User: yeah watch CHEM201 sections with open seats

Agent: Done. I'll notify you if seats open or fill up.
```

**Conversation 2: Instructor comparison**
```
User: who's better for CHEM201, Dr. Smith or Dr. Jones?

Agent: Here's the breakdown:

Dr. Smith:
- Quality: 4.2/5 (from 127 reviews)
- Difficulty: 3.1/5 (easier)
- First-time pass rate: 92%
- Avg grade: B+
- Teaches MWF 10-10:50

Dr. Jones:
- Quality: 3.8/5 (from 89 reviews)
- Difficulty: 4.5/5 (harder)
- First-time pass rate: 71%
- Avg grade: C+
- Teaches T/Th 1-2:50

Students with your GPA (3.4) who took Dr. Smith avg'd B+.
Students with your GPA who took Dr. Jones avg'd B-.

Dr. Smith is easier but fills fast. Dr. Jones has more seats.

Want me to add Dr. Smith's section to your watchlist?
```

**Conversation 3: Degree planning**
```
User: what courses do I still need to graduate?

Agent: I see your course history. You're a Bio major, junior year.

Completed (42 credits):
- BIOL101 ✓, CHEM101 ✓, MATH201 ✓, ENGL101 ✓
- 6 general electives ✓

Still needed:
- BIOL201 (Cell Bio) - prerequisite for BIOL310
- BIOL310 (Genetics) - only offered Fall
- CHEM201 (Orgo) - prerequisite for CHEM301
- CHEM301 (Biochem) - spring only
- PHYS101 (Physics I) - fall or spring
- 3 more science electives

⚠️ BIOL310 is only offered Fall and you haven't taken BIOL201 yet.
You need to take BIOL201 this spring or you'll be delayed.

Want me to plan your remaining semesters?

User: yeah, show me the path to graduation

Agent: Here's the optimal path:

Fall 2027: BIOL201 + PHYS101 + 2 electives (14 credits)
Spring 2028: BIOL310 + CHEM301 + 1 elective (13 credits)
Fall 2028: BIOL401 + CHEM401 + 1 science elective (12 credits)
Spring 2029: Capstone + remaining electives (12 credits)

Total: 51 credits remaining. Graduation: Spring 2029.

Want me to generate schedules for Fall 2027?
```

**Conversation 4: Stress testing**
```
User: how bad is this schedule?

Agent: Let me run a stress test on your current schedule:

Schedule: BIOL310 + CHEM301 + PHYS201 + MATH301 (16 credits)

Workload: ~28 hours/week (high)
Hardest day: Wednesday — 2 lectures + 1 lab back-to-back
Exam conflicts: MATH301 and CHEM301 midterms same week
Free days: Friday is open
Commute: 8 min between PHYS201 and MATH301 (tight but doable)

⚠️ Risk flags:
- Week 8 has 3 midterms
- No free day for 5 consecutive days
- Students with your GPA who took this combo avg'd 2.9

Want me to find a lighter alternative?
```

**Conversation 5: Transcript import**
```
User: I uploaded my transcript, can you parse it?

Agent: Found 24 courses in your transcript. Here's what I extracted:

- BIOL101: A (Fall 2025)
- CHEM101: B+ (Fall 2025)
- MATH201: A- (Spring 2026)
- ENGL101: B (Spring 2026)
- ... (20 more)

GPA: 3.4 | Science GPA: 3.2 | Credits: 72

Is this correct? Want me to update your course history?

User: yeah looks right

Agent: Updated. Want me to use this to recommend courses for next semester?
```

### 8.5 Agent Memory

The agent maintains per-user state:

| Memory Type | Description |
|-------------|-------------|
| **Profile** | Major, year, expected graduation, location |
| **Course History** | Completed courses + grades (from import or manual input) |
| **Preferences** | Protected time blocks, commute tolerance, instructor preferences, schedule archetype |
| **Current Schedule** | Active enrollment for current term |
| **Watchlist** | Sections being monitored for seat changes |
| **Saved Schedules** | Previously saved schedule configurations |
| **Conversation History** | Previous prompts and responses (context window) |
| **Behavioral Patterns** | What time slots they prefer, which instructors they gravitate toward |

The agent uses this context to personalize every response. "Based on your preference for morning classes" instead of generic "here are 5 schedules."

### 8.6 Agent Trust & Safety

| Rule | Description |
|------|-------------|
| **Destructive actions require confirmation** | Enroll, drop, waitlist, swap — agent asks "Are you sure?" before executing |
| **Read-first pattern** | Agent always reads data before acting. Never guesses. |
| **Explain before acting** | Agent tells the user what it's about to do and why, then asks for approval |
| **Rate limiting** | Max 10 SIS API calls per hour per user (avoid getting blocked) |
| **Audit log** | Every action logged with timestamp, tool called, result. User can review. |
| **Circuit breaker** | If agent fails 3x on same task, pause and tell user to check manually |
| **No hallucinated data** | Agent only uses data from tools. Never makes up grades, ratings, or seat counts. |
| **Opt-in per action type** | User can enable/disable specific tools (e.g., "never auto-enroll me, just notify") |

### 8.7 Proactive Agent Behavior

The agent doesn't just wait for prompts. It surfaces suggestions contextually:

- **Registration approaching:** "Registration opens in 3 days. Want me to prep your priority list?"
- **Seat alert:** "CHEM201-A just opened. Want me to grab it?"
- **Schedule improvement:** "I found a better version of your schedule with higher-rated instructors. Want to see it?"
- **Degree check:** "You're behind on science electives. Want me to find options?"
- **Review prompt:** "You took CHEM201 last semester. Want to leave a review?"
- **Study buddy:** "3 students in your CHEM201 section are looking for study partners."

Proactive suggestions are non-intrusive. They appear as subtle notifications or contextual hints, not popups. User can disable all proactive behavior.

### 8.8 Why This Is Different

No scheduling tool has a conversational agent that takes actions. Most tools are static: you build a schedule, that's it. FCS would be the first where the agent:

- **Understands** your full academic context (major, history, preferences, constraints)
- **Reasons** about multi-step tasks (not just "find courses" but "plan my path to graduation")
- **Acts** on your behalf (saves schedules, monitors seats, imports transcripts)
- **Learns** from every interaction (what you prefer, what tradeoffs you make)
- **Suggests** proactively (not just reactive to prompts)

This is the platform shift: from "tool you use" to "agent that manages your university life."
