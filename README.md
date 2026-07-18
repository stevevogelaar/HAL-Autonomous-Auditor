# HAL Autonomous Auditor — Autonomous Security Agent

**GDG Windsor Build with AI — Gemma Hackathon 2026**  
**Track:** Autonomous Agent  
**Model:** Google Gemma 4 (via Ollama)

---

## What It Does

HAL Autonomous Auditor is a local-AI agent that performs multi-step security audits without human intervention. Given a directory of source code, it:

1. **Reviews every source file** using HAL Guardian's Code Guardian
2. **Collects critical and high-severity findings**
3. **(Optionally) deep-scans suspicious strings** with Trust Shield
4. **Generates a ranked executive security report** using Gemma 4
5. **Saves the report to `reports/`** as Markdown

All reasoning runs locally through Ollama. No code or data leaves the machine.

---

## Why This Fits the Autonomous Agent Track

- **Goal-driven:** user gives a directory; the agent plans and executes the audit
- **Multi-step workflow:** review → filter → analyze → report
- **Self-contained:** no cloud APIs, no manual prompting between steps
- **Actionable output:** a prioritized remediation plan, not just raw findings

---

## Quick Start

### Prerequisites
- Python 3.12+
- Ollama installed and running
- Gemma 4 pulled (`gemma4:e2b`)

### Install
```powershell
python -m pip install -r requirements.txt
ollama pull gemma4:e2b
```

### Run
```powershell
python autonomous_auditor.py data\sample_code --name sample_code --model gemma4:e2b
```

Optional deep scan:
```powershell
python autonomous_auditor.py data\sample_code --name sample_code --model gemma4:e2b --deep-scan
```

Output:
- A JSON summary in the terminal
- A Markdown report saved to `reports/audit_report_<project>_<timestamp>.md`

---

## Example Report Output

The agent produces an executive report with:
- Project overview
- Top 3 risks ranked by severity and business impact
- Summary statistics (files reviewed, findings by severity)
- Prioritized next steps

---

## Architecture

```
hal_guardian/      # Reused from HAL Guardian
├── code_guardian.py
├── trust_shield.py
├── audit_engine.py
├── orchestrator.py
└── prompts/

autonomous_auditor.py
prompts/
└── autonomous_audit_report.txt

data/sample_code/    # Demo files
reports/             # Generated Markdown reports
```

---

## License

Apache 2.0 — matching Gemma 4's open license.
