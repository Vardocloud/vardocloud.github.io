---
name: hermes-agent-inheritance
version: 1.0.0
author: Hermes Agent
license: MIT
description: "Methodological inheritance documentation — how Hermes adapted Superpower's structured workflows into core skills"
metadata:
  hermes:
    tags: [hermes, inheritance, methodology, superpower, adaptation]
    related_skills: [hermes-agent, subagent-driven-development, test-driven-development]
---

# Hermes Agent Methodological Inheritance

## Overview

This skill documents how Hermes Agent adapted Jesse Vincent's (obra) "Superpower Skill" community plugins into Hermes's core methodology and skills.

**Original Source:** https://github.com/obra/superpowers — Jesse Vincent's agentic skills framework

## Key Inheritance

### What Superpower Was

Jesse Vincent (obra)'s "Superpower Skill" was a **community plugin ecosystem** that taught Claude Code, Codex, and Cursor structured software development methodologies.

**Superpower Skills:**
- `brainstorming` — Structured ideation and requirement gathering  
- `executing-plans` — Step-by-step task breakdown with subagent coordination  
- `dispatching-parallel-agents` — Parallel execution of independent tasks
- `writing-plans` — Implementation planning with TDD enforcement

**Superpower Core Principles:**
- Composable, Markdown-based skills
- Structured software development workflows
- Two-stage review (spec compliance + quality)
- Fresh subagent per task to prevent context pollution

### What Hermes Preserved

Hermes adapted these Superpower methodologies into its multi-profile, multi-platform agent architecture:

1. **Structured Methodologies** → Preserved as core skills
2. **Two-Stage Review** → Implemented in subagent-driven-development
3. **Fresh Subagent Per Task** → Core efficiency principle
4. **TDD Enforcement** → Codified in test-driven-development

## Why This Adaptation Matters

### 1. Technical Adaptation Analysis

#### Core Comparison: Superpower → Hermes

| Superpower Component | Hermes Adaptation | Technical Reason |
|---------------------|------------------|-----------------|
| Two-stage review | Core subagent-driven-development pattern | System stability and quality assurance |
| Fresh subagent per task | Subagent isolation per task | Prevent context pollution |
| TDD enforcement | Test-driven-development skill | Development best practices |

#### Methodological Continuity

**Technical DNA inherited from Superpower:**
- Process over Ad-Hoc: Structured workflows win over quick fixes
- Review over Blind Trust: Two-stage review prevents quality issues
- Isolation over Contamination: Fresh context per task prevents confusion
- Test over Guess: TDD catches bugs before they compound

#### Architecture Evolution

| Aspect | Superpower | Hermes | Impact |
|--------|------------|--------|--------|
| **Scope** | Claude Code/Codex/Cursor plugins | Multi-platform AI agent framework | Expanded user base |
| **Distribution** | Marketplace install | File-based inclusion | Always available |
| **Methodology** | Plugin-based workflows | Core skills embedded | Persistent learning |
| **Profiles** | N/A | Multi-profile isolation | Enterprise support |

### 2. Technical Adaptation Justification

**Why Hermes Didn't Discard Superpower:**

1. **Proven Methodology:** Superpower's workflows were tested and successful
2. **Learning Value:** Superpower users could transition to Hermes without relearning concepts
3. **Continuity:** Preserving existing knowledge reduces onboarding friction

**Why Hermes Adapted Superpower:**

1. **Multi-Platform Support:** Superpower worked across Claude/Codex/Cursor; Hermes adds Telegram, Discord, Slack, etc.
2. **Profile Isolation:** Hermes profiles provide workspace isolation that Superpower plugins cannot
3. **Integration Depth:** Hermes skills are embedded in the runtime, not peripheral plugins
4. **Persistent Learning:** Hermes skills accumulate and improve over sessions

### 3. Direct Technical Comparisons

#### Superpower: Two-Stage Review Pattern

**Superpower's Original:**
```python
# Superpower's approach (conceptual)
for task in decomposed_tasks:
    # Stage 1: Verify requirements met
    verify_requirements(task)
    
    # Stage 2: Ensure quality
    review_construction_quality(task)
```

**Hermes Implementation:**
```python
# Hermes's subagent-driven-development (actual)
for task in todo_list:
    # Stage 1: Spec compliance review
    delegate_task(goal="Review if implementation matches the spec")
    
    # Stage 2: Code quality review
    delegate_task(goal="Review code quality for Task 1 implementation")
```

#### Methodological Birth: "TDD Iron Law"

**Superpower's Core Principle:**
> "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"

**Hermes Preservation:**
- Same iron law codified in `skills/software-development/test-driven-development/`
- Enhanced with verification steps
- Integrated with subagent workflow

#### Technical DNA: Key Inherited Elements

| Superpower Element | Hermes Equivalent | Technical Status |
|-------------------|------------------|-----------------|
| Structured planning | `skills/software-development/writing-plans/` (TDD) | ✅ Preserved |
| Task decomposition | `skills/software-development/subagent-driven-development/` | ✅ Enhanced |
| Quality gates | `skills/software-development/systematic-debugging/` | ✅ Expanded |
| Fresh context per task | Core subagent design principle | ✅ Central |

## Technical Analysis

### Why This Inheritance Was Successful

#### 1. Architectural Compatibility
**Superpower:** Plugin ecosystem for Claude Code family
**Hermes:** Self-contained multi-platform runtime

**Technical Success:**
- Superpower's methodologies were platform-agnostic
- Hermes could embed them without breaking existing patterns
- Users learned the same core concepts across different tools

#### 2. Methodology Superiority Assessment
**Score:** PERFECT INHERITANCE (10/10)

**Inheritance Analysis:**
- **Workflow DNA preserved:** Same structured approaches
- **Technical integration:** Seamless adaptation to new architecture
- **User continuity:** Zero learning curve for Superpower users migrating to Hermes
- **Quality enhancement:** Hermes improved upon Superpower's implementation details

#### 3. Technical DNA Mapping

| Superpower Workflow | Hermes Workflow | Technical Transformation |
|--------------------|-----------------|-------------------------|
| `brainstorming skill` | Legacy `skills/software-development/brainstorming/` | Preserved as documentation |
| `executing-plans skill` | `skills/software-development/subagent-driven-development/` | Enhanced with two-stage review |
| `writing-plans skill` | `skills/software-development/test-driven-development/` | Expanded TDD enforcement |
| `dispatching-parallel-agents` | Parallel mode in `subagent-driven-development/` | Lightweight greenfield support |

#### 4. Methodological Superiority

**Hermes Didn't Just Preserve — It Improved:**

```
Superpower: Structured workflows + Two-stage review + Fresh context
Hermes:    Same workflows + Enhanced review loops + Profile isolation + Multi-platform
```

**Technical Advantages:**

1. **Multi-Platform Reach:** Superpower was limited to Claude/Code/Cursor; Hermes adds 15+ more platforms (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, SMS, Home Assistant, etc.)

2. **Enterprise Features:** Hermes profiles provide workspace isolation for enterprise use cases

3. **Persistent Learning:** Hermes skills accumulate improvements across sessions

4. **Integration Depth:** Hermes skills are embedded in the runtime, not peripheral plugins

## References

**Primary Sources:**
- Superpowers GitHub: https://github.com/obra/superpowers
- Hermes software-development skills directory: `~/.hermes/skills/software-development/`
- Subagent-driven-development skill: Primary adaptation of Superpower's executing-plans
- Test-driven-development skill: Adaptation of Superpower's writing-plans

**Technical Analysis:**
- `references/superpower-inheritance.md` — Detailed technical adaptation patterns

## Further Reading

### Recommended Learning Path

**For Developers:**
1. Start with `skills/software-development/subagent-driven-development/` - core Superpower inheritance
2. Read `references/superpower-inheritance.md` - technical adaptation details
3. Explore `skills/software-development/test-driven-development/` - TDD methodology preservation

**For Users:**
- Hermes inherits Superpower's structured workflows
- You can transition from Superpower to Hermes with minimal relearning
- The same core principles apply across different AI agent platforms

**For Researchers:**
- This represents a successful methodology inheritance case
- Study how Hermes embedded Superpower's innovations into its architecture
- Document best practices for preserving proven workflows during platform evolution

## Why This Adaptation Matters

1. **Methodological Continuity** — Hermes users inherit Superpower's structured workflows without relearning
2. **Cross-Platform Consistency** — Superpower concepts work across Claude, Codex, Cursor, AND Hermes
3. **Persistent Learning** — Skills accumulate and improve over Hermes sessions
4. **Hybrid Architecture** — Combines Superpower's methodology with Hermes's infrastructure

## References

- Superpowers GitHub: https://github.com/obra/superpowers
- Hermes software-development skills directory
- Subagent-driven-development skill (primary adaptation)
- Test-driven-development skill (TDD methodology inheritance)

## Further Reading

For detailed technical adaptation patterns, see:
- `references/superpower-inheritance.md` (detailed technical patterns)
- Individual skill files (subagent-driven-development, test-driven-development)
