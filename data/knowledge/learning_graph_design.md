# 🧩 Learning Graph Design

## 1. Overview

This document explains the data model defined in `schema.json`, which represents a **learning ecosystem** integrating three entities:  
- **Learner** — represents individual students or users  
- **Content** — represents the learning material or module  
- **Progress** — represents learner interactions and mastery progress  

This design supports analytics, personalization, and adaptive learning through a structured data relationship.

---

## 2. Entity Relationships

### **Core Relationship**
Each learner can interact with multiple content items, and each interaction is logged in a progress record.

Learner (1) ───< (M) Progress (M) >─── (1) Content


This **many-to-many** relationship is mediated by the `Progress` entity.

---

## 3. Entity Definitions

### 🧠 Learner

**Purpose:** Captures learner demographics, performance statistics, and behavioral clustering.

| Field | Type | Description |
|-------|------|-------------|
| learner_id | string | Unique ID for the learner |
| name | string | Full name of the learner |
| age | integer | Age of the learner |
| course_enrolled | string | Course name or program enrolled |
| time_spent | number | Total time spent on learning materials |
| avg_score | number | Average score across activities |
| accuracy | number | Learner accuracy rate (0–1 scale) |
| cluster_label | string | Cluster category (e.g., “Efficient High Performers”) |
| learning_style | string | Learner’s preferred learning mode (e.g., Visual, Auditory) |

---

### 📘 Content

**Purpose:** Represents learning resources with metadata about complexity, dependencies, and type.

| Field | Type | Description |
|-------|------|-------------|
| content_id | string | Unique ID for the learning content |
| title | string | Title of the resource |
| topic | string | Subject or concept covered |
| difficulty_level | string | Level of difficulty (Beginner, Intermediate, Advanced) |
| content_type | string | Type of material (Video, Quiz, Reading, Simulation, etc.) |
| prerequisites | array of strings | Required prior topics before this content |
| estimated_time | number | Estimated completion time (in minutes) |

---

### 📊 Progress

**Purpose:** Tracks learner’s mastery, engagement, and next-step recommendations for each content interaction.

| Field | Type | Description |
|-------|------|-------------|
| record_id | string | Unique record identifier |
| learner_id | string | Foreign key referencing Learner |
| content_id | string | Foreign key referencing Content |
| completion | number | Percentage of completion (0–1 scale) |
| mastery | number | Learner’s mastery score for that content (0–1 scale) |
| attempts | integer | Number of attempts taken |
| feedback | string | System or instructor feedback |
| next_branch | string | Suggested next content or skill node |
| last_activity_date | string | Date/time of last interaction (ISO 8601 format) |

---

## 4. Learning Graph Model

The dataset defines a **Learning Graph**, where:
- **Nodes** = Learners + Content items  
- **Edges** = Progress records linking them  

Each edge has *weights* such as `mastery`, `completion`, and `attempts`, representing learning intensity and proficiency.

### Example Graph Representation


[Learner: A101] --(mastery=0.8, completion=0.9)--> [Content: Loops]
[Learner: A101] --(mastery=0.4, completion=0.6)--> [Content: Functions]
[Content: Loops] --> [Content: Conditional Statements] (next_branch)


---

## 5. Adaptive Learning Flow

1. **Data Collection**
   - Logs from platform interactions (`time_spent`, `accuracy`, etc.)  
   - Metadata from content repository (`difficulty_level`, `content_type`)  
   - Progress updates (`completion`, `mastery`, `next_branch`)

2. **Feature Engineering**
   - Normalize performance metrics  
   - Cluster learners based on engagement and performance  

3. **Learning Graph Construction**
   - Use learner and content as graph nodes  
   - Use progress data as directed weighted edges  

4. **Adaptive Recommendation**
   - If mastery < 0.5 → suggest prerequisite content  
   - If mastery > 0.8 → unlock higher-level or next-branch content  
   - Use feedback for reinforcement and personalized hints  

---

## 6. Example Dataset Snapshot

| record_id | learner_id | content_id | completion | mastery | attempts | feedback | next_branch | last_activity_date |
|------------|-------------|-------------|-------------|----------|-----------|-----------|---------------|
| R001 | A101 | C101 | 0.85 | 0.70 | 2 | Good progress | Conditional Statements | 2025-10-20 |
| R002 | A101 | C102 | 0.60 | 0.40 | 3 | Needs more practice | Practice Problems | 2025-10-21 |
| R003 | A102 | C103 | 0.95 | 0.90 | 1 | Excellent mastery | Dictionaries | 2025-10-19 |
| R004 | A103 | C104 | 0.40 | 0.30 | 4 | Review basics | Loops | 2025-10-18 |

---

## 7. Insights from the Learning Graph

- **Performance Clusters:** Identify groups of learners with similar time-spent vs mastery profiles.  
- **Bottleneck Content:** Detect items where most learners have low mastery or high attempts.  
- **Learning Style Correlation:** Analyze how learning styles affect engagement or accuracy.  
- **Adaptive Sequencing:** Use `next_branch` to model optimal learning paths dynamically.  
- **Personalized Dashboards:** Combine learner and progress metrics to visualize improvement.

---

## 8. Data Validation Notes

- **Primary Keys:**  
  - Learner → `learner_id`  
  - Content → `content_id`  
  - Progress → `record_id`

- **Foreign Keys:**  
  - `learner_id` and `content_id` in `Progress` must exist in `Learner` and `Content`.

- **Data Types:**  
  - `completion`, `mastery`, `accuracy`, and `time_spent` should be numeric.  
  - `last_activity_date` follows ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).

- **Integrity Rules:**  
  - `completion` ≤ 1.0  
  - `mastery` ≤ 1.0  
  - Each `progress` record must link to exactly one learner and one content.

---

## 9. Scalability and Extensions

This design is scalable for:
- Adding **assessment analytics** (e.g., quiz scores, hints used)
- Adding **badges or rewards** (e.g., achievements based on mastery)
- Integrating **AI recommendation systems**
- Tracking **session-level interactions** for deeper behavioral modeling

---

## 10. Summary

The `schema.json` and this document define a **cohesive learning intelligence framework** that can:
- Track learner behavior and progress  
- Link learners and content dynamically  
- Support adaptive pathways and recommendations  

Together, they form the foundation for a **data-driven learning graph** that enhances personalization, engagement, and performance insights.

---

**End of File — learning_graph_design.md**
