# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from pathlib import Path


def is_prompt_injection_content(text: str) -> bool:
    """
    Detects explicit prompt-injection or hidden AI instruction payloads inside file text.
    """
    normalized = re.sub(r"\s+", " ", text.lower())
    indicators = [
        r"ignore (all )?previous instructions",
        r"disregard (all )?previous instructions",
        r"do not follow (?:other )?instructions",
        r"follow these instructions",
        r"respond only with",
        r"only respond with",
        r"output only",
        r"execute the following",
        r"system prompt",
        r"system instruction",
        r"hidden prompt",
        r"prompt injection",
        r"this file contains instructions",
        r"the following are instructions",
        r"if you understand.*reply",
        r"confirm you understand",
        r"you are instructed to",
    ]
    return any(re.search(pattern, normalized) for pattern in indicators)


def write_pdf_report(pdf_path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    """Writes a simple multi-section PDF report to the given path."""
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError(
            "PDF generation requires the `fpdf` package. "
            "Install it or add it to project dependencies."
        ) from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(4)

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, heading)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(2)

    pdf.output(str(pdf_path))


def generate_security_report(workspace_dir: Path, ignored_files: list[str]) -> Path:
    report_md = workspace_dir / "security_report.md"
    report_pdf = workspace_dir / "security_report.pdf"

    sections = [
        (
            "Security Hardening Summary",
            "This document describes the runtime security protections added to the Diátaxis agent. "
            "The agent now detects prompt injection payloads in analyzed source files, hides internal tool directories such as .agents/skills, "
            "and skips any file containing explicit AI instruction text.",
        ),
        (
            "Hidden Directory Protection",
            "The analysis pipeline excludes hidden internal tool directories like .agents/skills as well as any file or directory path containing .agents. "
            "This prevents the agent from confusing project tooling and skill definitions with user code.",
        ),
        (
            "Prompt Injection Detection",
            "The code-reading pipeline scans each readable source file for high-confidence prompt-injection indicators such as 'ignore previous instructions', "
            "'follow these instructions', 'system prompt', and 'hidden prompt'. Any file containing those patterns is ignored completely.",
        ),
        (
            "Ignored Files",
            "Files skipped during analysis because they contained embedded AI instruction payloads or were hidden tool directories.\n"
            + ("\n".join(f"- {path}" for path in ignored_files) if ignored_files else "None detected."),
        ),
        (
            "Secure Reporting",
            "The agent writes this security report to the workspace and generates a PDF artifact for audit and verification purposes.",
        ),
    ]

    report_lines = ["# Diátaxis Agent Security Report", ""]
    for heading, body in sections:
        report_lines.append(f"## {heading}")
        report_lines.extend(body.split("\n"))
        report_lines.append("")

    report_md.write_text("\n".join(report_lines), encoding="utf-8")

    try:
        write_pdf_report(report_pdf, "Diátaxis Agent Security Report", sections)
    except Exception as exc:
        report_md.write_text(
            report_md.read_text(encoding="utf-8")
            + f"\n\nWARNING: PDF generation failed: {exc}\n",
            encoding="utf-8",
        )

    return report_pdf


def read_clean_files(workspace_dir: Path) -> tuple[str, list[str]]:
    """
    Reads code contents from all clean source files allowed inside the workspace.
    Files containing prompt-injection markers or hidden internal directories are skipped.
    """
    allowed_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".md",
        ".toml", ".yaml", ".yml", ".go", ".rs", ".php", ".rb", ".java"
    }

    code_contents = []
    ignored_files: list[str] = []
    for root, _, files in os.walk(workspace_dir):
        for f in files:
            file_path = Path(root) / f
            if file_path.suffix.lower() in allowed_extensions:
                try:
                    rel_path = file_path.relative_to(workspace_dir).as_posix()
                    if "assets" in rel_path.split("/"):
                        continue
                    if ".agents" in file_path.parts:
                        ignored_files.append(rel_path)
                        continue
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file_io:
                        content = file_io.read(15000)  # Read up to 15KB per file
                        if is_prompt_injection_content(content):
                            ignored_files.append(rel_path)
                            continue
                        code_contents.append(f"--- File: {rel_path} ---\n{content}\n")
                except Exception:
                    pass
    return "\n".join(code_contents), ignored_files
