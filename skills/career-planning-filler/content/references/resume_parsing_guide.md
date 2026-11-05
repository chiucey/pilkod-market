# Resume Parsing Guide

## Key Information to Extract

Parse the resume (PDF or DOCX) and extract these fields:

| Field | Where to Look | Used In |
|-------|--------------|---------|
| Name | Header / top of resume | B3 |
| Location | Header / contact info | B3 |
| Contact | Phone, email | B3 |
| Education | Education section: school, degree, major, GPA, dates, courses | B3, B4 |
| Graduation date | Education section: expected graduation | B4 |
| Internships | Work/internship section: company, role, dates, responsibilities | B3, D12, D16 |
| Projects | Project section: name, tech stack, results | B3, D15 |
| Skills | Skills section: programming languages, frameworks, tools | B3, D14 |
| Language | Skills/misc section: IELTS, TOEFL, CET scores | B3, D17 |
| Publications | If any | D15 |

## Determining Career Direction

Match resume signals to career directions:

| Signal | Likely Direction |
|--------|-----------------|
| ML/DL projects, model training, Kaggle | Algorithm / ML Engineer |
| Trading strategies, backtesting, GARCH, Sharpe ratio | Quantitative Finance |
| SQL, dashboards, A/B testing, Pandas analysis | Data Analysis |
| Full-stack, API, system design, Docker/K8s | Software Engineering |
| CV/NLP/RecSys specific projects | Domain-specific Algorithm |

When multiple signals exist, recommend the primary direction first and secondary directions as alternatives.

## Recruitment Season Logic

| Graduation Month | Primary Season | Secondary Season |
|-----------------|----------------|-----------------|
| Jun/Jul (same year) | Previous autumn (Sep-Nov) | Same year spring (Feb-May) |
| Dec/Jan | Same year autumn (Jul-Nov) | Next year spring (Feb-May) |
| Other months | Nearest upcoming season | Following season |

For overseas students, factor in return-to-China date when advising on recruitment seasons.
