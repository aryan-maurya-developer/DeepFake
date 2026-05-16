from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = Path(r"C:\Users\fahad\Downloads\DeepFake-amsr\docs\AmsR_DeepShield_Architecture_Improvement_Spec_v2.docx")


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_table_borders(table, color="D9E2F3", size="6"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        elem = OxmlElement(f"w:{edge}")
        elem.set(qn("w:val"), "single")
        elem.set(qn("w:sz"), size)
        elem.set(qn("w:space"), "0")
        elem.set(qn("w:color"), color)
        borders.append(elem)
    tbl_pr.append(borders)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2 + (0.2 * level))
    p.paragraph_format.first_line_indent = Inches(-0.15)
    run = p.add_run(f"- {text}")
    run.font.size = Pt(10.5)
    return p


def add_number(doc, text):
    if not hasattr(add_number, "counter"):
        add_number.counter = 0
    add_number.counter += 1
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.first_line_indent = Inches(-0.15)
    run = p.add_run(f"{add_number.counter}. {text}")
    run.font.size = Pt(10.5)
    return p


def add_code_block(doc, lines):
    for line in lines.splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.35)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)


def style_document(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)

    for style_name, size, color in (
        ("Title", 22, RGBColor(15, 60, 110)),
        ("Heading 1", 15, RGBColor(20, 74, 124)),
        ("Heading 2", 12, RGBColor(27, 84, 144)),
        ("Heading 3", 10.5, RGBColor(49, 90, 140)),
    ):
        style = doc.styles[style_name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.color.rgb = color


def add_cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(120)
    r = p.add_run("AmsR DeepShield\nArchitecture Improvement Specification")
    r.bold = True
    r.font.size = Pt(24)
    r.font.color.rgb = RGBColor(15, 60, 110)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_before = Pt(12)
    sub.paragraph_format.space_after = Pt(12)
    run = sub.add_run(
        "Revised enterprise blueprint for a scalable, secure, and deployment-flexible "
        "multi-modal deepfake detection platform"
    )
    run.italic = True
    run.font.size = Pt(11)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.paragraph_format.space_before = Pt(20)
    meta_run = meta.add_run("Prepared from the original prompt draft and aligned to the current repository architecture")
    meta_run.font.size = Pt(10.5)
    meta_run.font.color.rgb = RGBColor(90, 90, 90)

    box = doc.add_table(rows=3, cols=2)
    box.style = "Table Grid"
    box.autofit = False
    box.columns[0].width = Inches(1.7)
    box.columns[1].width = Inches(4.8)
    set_table_borders(box, color="B8CCE4")
    items = [
        ("Document Purpose", "Define the target-state architecture and implementation priorities for AmsR DeepShield."),
        ("Primary Audience", "Engineering leadership, backend/frontend developers, MLOps, security, and platform teams."),
        ("Revision Goal", "Convert a good idea list into an actionable, implementation-ready architecture plan."),
    ]
    for idx, (left, right) in enumerate(items):
        box.cell(idx, 0).text = left
        box.cell(idx, 1).text = right
        set_cell_shading(box.cell(idx, 0), "EAF1FB")

    doc.add_page_break()


def add_section_intro(doc):
    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(
        "AmsR DeepShield should mature from a Docker-first deepfake detector into a modular forensic platform "
        "that can run in cloud, local, and hybrid environments without sacrificing security, explainability, "
        "or operational observability."
    )
    doc.add_paragraph(
        "The original draft already identified the right ambition, but it mixed concrete requirements with "
        "placeholders and aspirational technology names. This revision turns that ambition into a clearer "
        "engineering target by distinguishing mandatory platform capabilities, implementation priorities, "
        "and optional future enhancements."
    )

    doc.add_heading("2. Document Improvements Applied", level=1)
    for item in (
        "Normalized section hierarchy so architecture, security, observability, and delivery topics flow in execution order.",
        "Converted placeholder headings into implementation guidance, decision criteria, or explicit backlog items.",
        "Aligned the target architecture with the current repository, which already uses a FastAPI gateway, Dockerized models, React frontend, and ensemble inference.",
        "Reduced vague language and added concrete response contracts, deployment expectations, and roadmap priorities.",
    ):
        add_bullet(doc, item)


def add_current_state(doc):
    doc.add_heading("3. Current-State Assessment", level=1)
    doc.add_paragraph(
        "The repository already demonstrates strong platform foundations: a FastAPI gateway, isolated model services, "
        "ensemble prediction logic, a React frontend, Docker Compose orchestration, and local SQLite persistence. "
        "Those strengths should be preserved."
    )

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(2.3)
    table.columns[2].width = Inches(2.6)
    set_table_borders(table)
    headers = ("Area", "Current Strength", "Improvement Required")
    for i, text in enumerate(headers):
        table.cell(0, i).text = text
        set_cell_shading(table.cell(0, i), "D9EAF7")
    set_repeat_table_header(table.rows[0])

    rows = [
        ("Inference", "Multiple specialized detectors already exist.", "Add a formal runtime abstraction and health-aware orchestration."),
        ("Deployment", "Docker Compose support is present.", "Add first-class local mode, environment auto-detection, and upgrade path to Kubernetes."),
        ("Persistence", "SQLite history exists today.", "Introduce a clean repository layer with optional MongoDB replication."),
        ("Frontend", "React dashboard exists with reporting/export flows.", "Add real-time progress, richer explainability, and system health views."),
        ("Security", "Basic validation exists.", "Add file safety pipeline, audit logging, rate limiting, and malware scanning strategy."),
    ]
    for row in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value


def add_target_architecture(doc):
    doc.add_heading("4. Target Architecture", level=1)
    doc.add_paragraph(
        "The platform should support two primary execution modes behind one stable API contract."
    )

    doc.add_heading("4.1 Required Runtime Modes", level=2)
    for item in (
        "Containerized mode: independent detector services, horizontal scale, centralized orchestration, and GPU-aware scheduling.",
        "Local mode: single-host deployment with embedded inference, shared resource management, and offline-first execution.",
        "Hybrid mode: local preprocessing and evidence capture with optional cloud-backed analysis, synchronization, or enrichment.",
    ):
        add_bullet(doc, item)

    doc.add_heading("4.2 Core Architectural Principles", level=2)
    principles = [
        "One public API contract regardless of deployment mode.",
        "Security checks must run before expensive media processing.",
        "Every detector must expose a standard lifecycle: load, preprocess, infer, postprocess, and health check.",
        "Inference orchestration must tolerate partial detector failure and still return a traceable result when policy allows.",
        "Observability, auditability, and explainability are platform requirements, not optional add-ons.",
    ]
    for principle in principles:
        add_bullet(doc, principle)

    doc.add_heading("4.3 Unified Request Pipeline", level=2)
    add_number(doc, "Client upload and request registration")
    add_number(doc, "Security validation and file safety inspection")
    add_number(doc, "Media classification and routing decision")
    add_number(doc, "Detector execution through the orchestration layer")
    add_number(doc, "Ensemble aggregation and confidence calibration")
    add_number(doc, "Forensic evidence packaging, persistence, and metrics emission")
    add_number(doc, "Response delivery with trace metadata and explainability")

    doc.add_heading("4.4 Recommended Service Map", level=2)
    service_table = doc.add_table(rows=1, cols=3)
    service_table.style = "Table Grid"
    service_table.autofit = False
    service_table.columns[0].width = Inches(2.1)
    service_table.columns[1].width = Inches(1.4)
    service_table.columns[2].width = Inches(3.2)
    set_table_borders(service_table)
    for i, text in enumerate(("Service", "Required In", "Responsibility")):
        service_table.cell(0, i).text = text
        set_cell_shading(service_table.cell(0, i), "D9EAF7")
    set_repeat_table_header(service_table.rows[0])
    services = [
        ("API Gateway", "All modes", "Authentication, request validation, orchestration entrypoint, response normalization."),
        ("Inference Orchestrator", "All modes", "Detector lifecycle, retries, concurrency limits, and aggregation control."),
        ("Detector Services", "Docker/hybrid", "Isolated model execution for image, video, audio, and future text/OCR pipelines."),
        ("Local Inference Engine", "Local mode", "Embedded detector execution with shared memory and GPU fallback logic."),
        ("Persistence Layer", "All modes", "SQLite by default, optional MongoDB replication, evidence metadata, and audit trails."),
        ("Queue/Job Layer", "Recommended", "Long-running video jobs, batch uploads, and retraining tasks."),
        ("Metrics and Tracing", "All modes", "Prometheus-compatible metrics and OpenTelemetry traces."),
    ]
    for row in services:
        cells = service_table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value


def add_data_and_ml(doc):
    doc.add_heading("5. Inference and Model Governance", level=1)
    doc.add_paragraph(
        "A consistent detector contract is the fastest path to extensibility. New models should be plug-in compatible "
        "with the orchestration layer rather than requiring custom gateway logic."
    )

    doc.add_heading("5.1 Standard Detector Interface", level=2)
    add_code_block(
        doc,
        """class BaseDetector:
    async def load_model(self): ...
    async def preprocess(self, media): ...
    async def infer(self, processed): ...
    async def postprocess(self, results): ...
    async def health_check(self): ...""",
    )

    doc.add_heading("5.2 Ensemble Strategy", level=2)
    for item in (
        "Keep weighted averaging and stacking as first-class methods because they align with the current repository design.",
        "Treat Bayesian fusion and dynamic weighting as optional roadmap items until calibration data and operational telemetry are mature enough to support them.",
        "Store per-model outputs, calibration metadata, and final fusion decisions so results remain reproducible.",
    ):
        add_bullet(doc, item)

    doc.add_heading("5.3 Explainability Requirements", level=2)
    add_bullet(doc, "Return top contributing detectors, anomaly summaries, and confidence rationale in every successful response.")
    add_bullet(doc, "Record detector-level failures and exclusions so low-confidence or partial results are understandable.")
    add_bullet(doc, "Expose enough structured evidence for UI timelines, report exports, and audit review.")


def add_security(doc):
    doc.add_heading("6. Security and Abuse Resistance", level=1)
    doc.add_paragraph(
        "Security should be built as an ordered gate ahead of inference so the system never treats untrusted media like "
        "harmless input."
    )
    for item in (
        "Hash every upload and retain immutable request identifiers.",
        "Validate MIME type, magic bytes, file extension consistency, and size limits.",
        "Detect suspicious archives, malformed media, and polyglot files before decode.",
        "Add rate limiting per IP, user, and API key, with stricter thresholds for expensive video jobs.",
        "Separate immutable audit logs for security events, admin actions, and evidence export activity.",
    ):
        add_bullet(doc, item)

    doc.add_heading("6.1 Practical Scanner Strategy", level=2)
    doc.add_paragraph(
        "VirusTotal should be treated as optional enrichment for connected deployments only. ClamAV or an equivalent "
        "local scanner is the safer baseline for air-gapped and privacy-sensitive deployments."
    )


def add_platform(doc):
    doc.add_heading("7. Persistence, Observability, and Operations", level=1)
    doc.add_heading("7.1 Persistence Model", level=2)
    add_bullet(doc, "Default to SQLite for local durability and simple installs.")
    add_bullet(doc, "Add a repository abstraction so MongoDB replication is optional rather than hard-wired.")
    add_bullet(doc, "Persist request metadata, detector outputs, processing timings, and audit events separately.")

    doc.add_heading("7.2 Observability", level=2)
    add_bullet(doc, "Use structured JSON logs across all services.")
    add_bullet(doc, "Expose Prometheus metrics for latency, queue depth, detector failures, GPU utilization, and cache behavior.")
    add_bullet(doc, "Adopt OpenTelemetry traces across gateway, orchestrator, and model calls.")
    add_bullet(doc, "Provide `/api/health` for lightweight checks and `/api/health/detailed` for operational diagnostics.")

    doc.add_heading("7.3 Async Processing", level=2)
    add_bullet(doc, "Introduce background job execution for long-running video analysis, batch processing, and report generation.")
    add_bullet(doc, "Stream progress updates to the frontend through WebSockets or server-sent events.")
    add_bullet(doc, "Define retry limits, dead-letter behavior, and job cancellation rules before adding queue scale.")


def add_api_and_frontend(doc):
    doc.add_heading("8. API and Frontend Direction", level=1)
    doc.add_heading("8.1 Response Contract", level=2)
    add_code_block(
        doc,
        """{
  "request_id": "uuid",
  "timestamp": "ISO8601",
  "media_type": "video",
  "processing_mode": "docker",
  "verdict": "fake",
  "confidence": 0.96,
  "risk_level": "high",
  "forensic_analysis": {},
  "security_analysis": {},
  "performance_metrics": {},
  "explainability": {
    "top_contributing_models": [],
    "key_anomalies_detected": [],
    "confidence_reasoning": ""
  },
  "trace": {}
}""",
    )

    doc.add_heading("8.2 Frontend Priorities", level=2)
    for item in (
        "Preserve the current React dashboard but add clearer job progress, system health, and model-level confidence breakdowns.",
        "Design for accessibility, mobile responsiveness, and exportable forensic reports.",
        "Treat advanced visualizations such as frame anomaly timelines, spectrogram overlays, and evidence viewers as high-value additions after the core response contract stabilizes.",
    ):
        add_bullet(doc, item)


def add_delivery_plan(doc):
    doc.add_heading("9. Delivery Roadmap", level=1)
    roadmap = doc.add_table(rows=1, cols=4)
    roadmap.style = "Table Grid"
    roadmap.autofit = False
    roadmap.columns[0].width = Inches(1.0)
    roadmap.columns[1].width = Inches(1.7)
    roadmap.columns[2].width = Inches(2.4)
    roadmap.columns[3].width = Inches(1.7)
    set_table_borders(roadmap)
    for idx, text in enumerate(("Phase", "Focus", "Primary Outputs", "Exit Criteria")):
        roadmap.cell(0, idx).text = text
        set_cell_shading(roadmap.cell(0, idx), "D9EAF7")
    set_repeat_table_header(roadmap.rows[0])

    phases = [
        ("1", "Platform hardening", "Runtime abstraction, config cleanup, security gate, health endpoints", "System runs reliably in Docker and local mode"),
        ("2", "Operational maturity", "Structured logging, metrics, tracing, queue-based jobs", "Long-running workloads are observable and recoverable"),
        ("3", "Forensic depth", "Explainability payloads, richer evidence storage, report exports", "Responses are audit-ready and understandable"),
        ("4", "Scale and enterprise readiness", "Kubernetes packaging, GPU scheduling, HA persistence options", "Platform meets production SLOs under load"),
    ]
    for row in phases:
        cells = roadmap.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value

    doc.add_heading("10. Final Recommendations", level=1)
    for item in (
        "Build around one stable API and one detector contract before adding more model diversity.",
        "Prioritize security gating, health-aware orchestration, and observability ahead of advanced UI polish.",
        "Keep offline-capable deployment as a non-negotiable requirement because it meaningfully differentiates the platform.",
        "Treat roadmap technologies as optional until they are backed by measured performance benefit, operating constraints, and ownership.",
    ):
        add_bullet(doc, item)

    doc.add_heading("11. Conclusion", level=1)
    doc.add_paragraph(
        "AmsR DeepShield has the foundation of a serious multi-modal detection platform. The next step is not a dramatic "
        "rewrite; it is disciplined platformization. By formalizing runtime modes, security layers, orchestration rules, "
        "and observability standards, the project can move from an impressive prototype into a production-ready forensic system."
    )


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    add_number.counter = 0
    style_document(doc)
    add_cover(doc)
    add_section_intro(doc)
    add_current_state(doc)
    add_target_architecture(doc)
    add_data_and_ml(doc)
    add_security(doc)
    add_platform(doc)
    add_api_and_frontend(doc)
    add_delivery_plan(doc)

    doc.save(OUTPUT)
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
