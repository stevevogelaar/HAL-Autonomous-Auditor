# HAL Autonomous Auditor — Autonomous Security Agent

**GDG Windsor Build with AI — Gemma Hackathon 2026**  
**Track:** Autonomous Agent

---

## Problem

Security audits are repetitive: review code, filter findings, rank risks, write a report. Most teams skip them because they are time-consuming. An autonomous agent that can plan and execute this workflow locally would make consistent security review practical for every commit.

## Solution

HAL Autonomous Auditor is a local-AI agent that accepts a source-code directory and produces a prioritized executive security report. It demonstrates true autonomous behavior: it plans the workflow, executes each step, and synthesizes the result.

## How It Uses Gemma 4

- **Step 1 — Batch review:** Gemma 4 reviews every source file via HAL Guardian's Code Guardian
- **Step 2 — Filtering:** the agent extracts critical and high findings automatically
- **Step 3 — Deep context scan (optional):** Trust Shield with Gemma 4 analyzes suspicious strings
- **Step 4 — Reporting:** Gemma 4 ranks the top risks and writes a Markdown executive report

## Autonomous Workflow

```
User provides directory
        ↓
Agent runs review_dir on every source file
        ↓
Agent filters critical/high findings
        ↓
Agent (optionally) runs Trust Shield deep scan
        ↓
Agent asks Gemma 4 to generate ranked report
        ↓
Report saved to reports/ folder
```

## Why Local Matters

No source code leaves the machine. This is essential for proprietary codebases, regulated environments, and incident-response workflows where cloud APIs are unacceptable.

## Results

On the included `data/sample_code` directory, the agent reviewed 3 files, identified 4 critical/high findings, and produced a report prioritizing SQL injection, hardcoded credentials, and command injection.

## Future Work

- Add `reverify` step that re-checks fixes in a later commit
- Integrate with Git to audit only changed files
- Export reports as PDF or GitHub issue drafts

---

**Repository:** https://github.com/stevevogelaar/HAL-Autonomous-Auditor.git
