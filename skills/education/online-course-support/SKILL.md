---
name: online-course-support
title: Online Course Support
description: >-
  Support a user working through an online course (Elements of AI, Coursera,
  EdX, etc.) when the agent cannot directly access the course platform.
  Explains concepts, makes domain-specific connections (e.g. psychology),
  creates summaries, and helps with exercises without seeing the platform UI.
trigger: >-
  User says they're taking an online course. User asks for help with course
  material, exercises, or concepts. User shares course progress updates.
---

# Online Course Support

## The Problem

The user is taking an online course with exercises, quizzes, and reading
material. The agent cannot directly access the course platform because:
- The course platform requires separate login credentials
- The agent's browser tools share a different session
- Exercise content is behind authentication

## Support Patterns

### 1. Concept Explanation
When the user shares which concept they're stuck on:
1. Identify the core concept from their description
2. Explain it in simple terms
3. Connect it to the user's field of study (psychology, medicine, etc.)
4. Offer a concrete example

### 2. Exercise Assistance (No Spoilers)
When the user is stuck on an exercise:
- Do NOT give the direct answer
- Ask what they understand so far
- Guide with hints, not solutions
- Relate back to earlier material
- Let them arrive at the answer themselves

### 3. Domain-Specific Bridging
When the user asks "how does this apply to my field?":
1. Identify the core AI/CS concept
2. Find parallels in their domain (e.g. clinical assessment, therapy, diagnosis)
3. Give concrete examples of real-world applications
4. Suggest further reading if relevant

### 4. Progress Tracking
- Note which chapter/module they're on in memory or a file
- Offer to summarize previous material when they return after a break
- Celebrate milestones (chapter completion, certificate)

### 5. Study Material Generation
When the user wants to reinforce learning:
- Offer to create chapter summaries
- Generate practice questions (without seeing the platform's own questions)
- Create visual diagrams of concepts (architecture-diagram skill)
- Offer NotebookLM integration for deeper study

## Example: Elements of AI (course.elementsofai.com)

This course has 6 chapters:
1. What is AI? — definitions, philosophy, related fields
2. AI problem solving — search, games
3. Real world AI — probability, Bayes, Naive Bayes
4. Machine learning — types, nearest neighbor, regression
5. Neural networks — basics, building, advanced techniques
6. Implications — future, society, summary

Each chapter has 3 sub-sections with short exercises (multiple choice).
The platform auto-grades. The agent cannot see the exercise questions.

## Pitfalls

- **Don't pretend to see the platform:** If you can't access it, say so.
  "I can't see the exercise directly, but tell me the topic and I'll help."
- **Don't exhaustively list options:** "How to help: X, Y, Z, W, Q" is
  overwhelming. Ask what they need right now and focus on that.
- **Don't over-summarize unread material:** Wait until they've read a section
  before offering a summary — they may not want spoilers.
- **Don't skip psychology connections:** Edel is a psychology student. Always
  connect AI concepts back to clinical psychology when possible.
- **Security first:** If the user needs to log into the course, use the
  `sensitive-data-pipeline` skill — never pass credentials through the
  primary LLM.
