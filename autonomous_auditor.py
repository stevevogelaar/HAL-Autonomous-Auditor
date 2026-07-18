"""
HAL Autonomous Auditor
An autonomous security auditing agent that plans, executes, and reports.
Built from HAL Guardian's local-AI orchestrator.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import ollama

# Reuse HAL Guardian modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hal_guardian.config import DEFAULT_MODEL, OLLAMA_HOST, get_available_models
from hal_guardian.orchestrator import run
from hal_guardian.models import Finding


def _load_prompt(name: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "You are a security analyst. Summarize the findings."


def _call_ollama(prompt: str, model: str) -> str:
    client = ollama.Client(host=OLLAMA_HOST)
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2, "num_ctx": 8192},
    )
    return response["message"]["content"]


def _extract_high_risk_findings(reviews: List[dict]) -> List[dict]:
    """Collect critical and high findings from all file reviews."""
    collected = []
    for review in reviews:
        file_path = review.get("file", "unknown")
        findings = review.get("review", {}).get("findings", [])
        for f in findings:
            if f.get("severity") in ("critical", "high"):
                collected.append({
                    "file": file_path,
                    **f,
                })
    return collected


def _build_report_prompt(project_name: str, reviews: List[dict], high_risk: List[dict]) -> str:
    stats = {
        "files_reviewed": len(reviews),
        "total_findings": sum(len(r.get("review", {}).get("findings", [])) for r in reviews),
        "critical": sum(1 for r in reviews for f in r.get("review", {}).get("findings", []) if f.get("severity") == "critical"),
        "high": sum(1 for r in reviews for f in r.get("review", {}).get("findings", []) if f.get("severity") == "high"),
        "medium": sum(1 for r in reviews for f in r.get("review", {}).get("findings", []) if f.get("severity") == "medium"),
        "low": sum(1 for r in reviews for f in r.get("review", {}).get("findings", []) if f.get("severity") == "low"),
    }

    findings_text = "\n\n".join(
        f"File: {f.get('file')}\nSeverity: {f.get('severity')}\nCategory: {f.get('category')}\nLine: {f.get('line')}\nDescription: {f.get('description')}\nRecommendation: {f.get('recommendation')}"
        for f in high_risk[:15]
    )

    prompt = (
        f"{_load_prompt('autonomous_audit_report')}\n\n"
        f"PROJECT: {project_name}\n\n"
        f"STATISTICS:\n{json.dumps(stats, indent=2)}\n\n"
        f"TOP FINDINGS:\n{findings_text}\n\n"
        "Write the executive security report now."
    )
    return prompt


def autonomous_audit(directory: str, project_name: str = "", model: str = DEFAULT_MODEL, deep_scan_text: bool = False) -> Dict[str, Any]:
    """
    Run an autonomous multi-step security audit on a directory.

    Steps:
    1. Batch-review all source files in the directory.
    2. Collect critical/high findings.
    3. (Optional) Deep-scan suspicious strings with Trust Shield.
    4. Ask Gemma 4 to generate an executive security report.
    5. Return structured result and save report to reports/.
    """
    start = time.time()
    project_name = project_name or Path(directory).name

    # Step 1: review directory
    review_result = run("review_dir", target=directory, model=model, recursive=True)
    if not review_result.get("ok"):
        return {"ok": False, "error": review_result.get("error")}

    reviews = review_result["data"].get("reviews", [])

    # Step 2: collect high-risk findings
    high_risk = _extract_high_risk_findings(reviews)

    # Step 3: optional deep scan on joined high-risk descriptions
    trust_findings = []
    if deep_scan_text and high_risk:
        suspicious_text = "\n".join(f"{f.get('file')}: {f.get('description')}" for f in high_risk[:10])
        scan_result = run("scan", target=suspicious_text, source="untrusted", deep=True, deep_model=model)
        if scan_result.get("ok"):
            trust_findings = scan_result["data"].get("findings", [])

    # Step 4: generate executive report
    prompt = _build_report_prompt(project_name, reviews, high_risk)
    try:
        report_md = _call_ollama(prompt, model)
    except Exception as e:
        report_md = f"[Report generation failed: {e}]"

    # Step 5: save report
    reports_dir = Path(__file__).resolve().parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"audit_report_{project_name}_{timestamp}.md"
    report_path.write_text(
        f"# Autonomous Security Audit Report: {project_name}\n\n"
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n\n"
        f"**Model:** {model}\n\n"
        f"{report_md}\n",
        encoding="utf-8",
    )

    duration_ms = int((time.time() - start) * 1000)

    return {
        "ok": True,
        "project": project_name,
        "directory": directory,
        "model": model,
        "duration_ms": duration_ms,
        "files_reviewed": len(reviews),
        "high_risk_findings": len(high_risk),
        "trust_shield_findings": trust_findings,
        "report_path": str(report_path),
        "report_markdown": report_md,
    }


def _pick_model(requested: str) -> str:
    """Resolve requested model against locally pulled models."""
    available = get_available_models()
    if requested in available:
        return requested
    if DEFAULT_MODEL in available:
        return DEFAULT_MODEL
    if available:
        return available[0]
    return requested


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HAL Autonomous Auditor")
    parser.add_argument("directory", nargs="?", default="", help="Directory to audit")
    parser.add_argument("--name", default="", help="Project name")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model")
    parser.add_argument("--list-models", action="store_true", help="List locally available Ollama models")
    parser.add_argument("--deep-scan", action="store_true", help="Run Trust Shield deep scan on high-risk findings")
    args = parser.parse_args()

    if args.list_models:
        print("Available local models:")
        for m in get_available_models():
            marker = " (default)" if m == DEFAULT_MODEL else ""
            print(f"  - {m}{marker}")
        sys.exit(0)

    if not args.directory:
        parser.print_help()
        sys.exit(1)

    selected_model = _pick_model(args.model)
    if selected_model != args.model:
        print(f"Requested model '{args.model}' not found. Using '{selected_model}'.")

    result = autonomous_audit(args.directory, project_name=args.name, model=selected_model, deep_scan_text=args.deep_scan)
    print(json.dumps(result, indent=2, default=str))
