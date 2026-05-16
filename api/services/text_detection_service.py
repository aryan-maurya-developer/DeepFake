from __future__ import annotations

import io
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STOPWORDS = {
    "the", "is", "are", "that", "this", "with", "for", "and", "you", "your", "from",
    "have", "has", "not", "but", "can", "will", "use", "using", "into", "should",
}

AI_PHRASES = {
    "in conclusion", "overall", "furthermore", "moreover", "it is important to note",
    "here is", "step by step", "best practices", "comprehensive", "production-ready",
}

CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go", ".cpp", ".c", ".rs", ".rb", ".php", ".html", ".css", ".sql"}


def _safe_import_docx_text(data: bytes) -> str:
    try:
        from docx import Document  # type: ignore

        document = Document(io.BytesIO(data))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    except Exception:
        return ""


def _safe_import_pdf_text(data: bytes) -> str:
    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


@dataclass
class TextDetectionResult:
    label: str
    probability_ai: float
    confidence: float
    explanation: list[str]
    extracted_text: str
    features: dict[str, Any]


class TextDetectionService:
    def extract_text(self, filename: str | None, payload: str | None, upload_bytes: bytes | None) -> tuple[str, str]:
        if payload:
            ext = Path(filename or "input.txt").suffix.lower()
            kind = "code" if ext in CODE_EXTENSIONS else "text"
            return payload, kind
        if not upload_bytes:
            return "", "text"
        ext = Path(filename or "").suffix.lower()
        if ext == ".pdf":
            return _safe_import_pdf_text(upload_bytes), "document"
        if ext == ".docx":
            return _safe_import_docx_text(upload_bytes), "document"
        text = upload_bytes.decode("utf-8", errors="ignore")
        kind = "code" if ext in CODE_EXTENSIONS else ("markdown" if ext in {".md", ".markdown"} else "text")
        return text, kind

    def analyze(self, text: str, content_type: str) -> TextDetectionResult:
        normalized = text.replace("\r\n", "\n").strip()
        lines = [line for line in normalized.splitlines() if line.strip()]
        tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_'-]*", normalized.lower())
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", normalized) if s.strip()]
        token_counts = Counter(tokens)

        token_count = len(tokens)
        unique_ratio = (len(token_counts) / token_count) if token_count else 0.0
        sentence_lengths = [len(re.findall(r"\w+", sentence)) for sentence in sentences] or [0]
        avg_sentence_length = sum(sentence_lengths) / max(1, len(sentence_lengths))
        burstiness = (
            (sum((length - avg_sentence_length) ** 2 for length in sentence_lengths) / max(1, len(sentence_lengths))) ** 0.5
        ) / max(1.0, avg_sentence_length)
        repetition_ratio = (
            sum(count for count in token_counts.values() if count > 2) / max(1, token_count)
        )
        stopword_ratio = sum(1 for token in tokens if token in STOPWORDS) / max(1, token_count)
        ai_phrase_hits = sum(1 for phrase in AI_PHRASES if phrase in normalized.lower())
        punctuation_ratio = len(re.findall(r"[,:;()\-]", normalized)) / max(1, len(normalized))
        line_length_std = self._line_length_std(lines)
        markdown_density = sum(1 for line in lines if line.startswith(("#", "-", "*", "`"))) / max(1, len(lines))
        code_marker_ratio = sum(1 for token in tokens if token in {"def", "class", "return", "const", "function", "import"}) / max(1, token_count)

        ai_score = 0.0
        ai_score += max(0.0, 0.22 - burstiness) * 1.8
        ai_score += repetition_ratio * 0.9
        ai_score += max(0.0, 0.55 - unique_ratio) * 1.1
        ai_score += min(0.25, ai_phrase_hits * 0.05)
        ai_score += max(0.0, 0.12 - line_length_std) * 0.8
        if content_type == "code":
            ai_score += max(0.0, 0.25 - code_marker_ratio) * 0.4
        if content_type == "markdown":
            ai_score += markdown_density * 0.15
        ai_score = max(0.01, min(0.99, ai_score))

        probability_ai = 1 / (1 + math.exp(-((ai_score * 5.5) - 2.75)))
        confidence = min(0.99, max(0.1, abs(probability_ai - 0.5) * 1.7 + 0.35))
        label = "AI-generated" if probability_ai >= 0.5 else "Human-written"
        explanation = self._build_explanations(
            probability_ai=probability_ai,
            burstiness=burstiness,
            repetition_ratio=repetition_ratio,
            unique_ratio=unique_ratio,
            ai_phrase_hits=ai_phrase_hits,
            content_type=content_type,
        )
        return TextDetectionResult(
            label=label,
            probability_ai=round(probability_ai, 4),
            confidence=round(confidence, 4),
            explanation=explanation,
            extracted_text=normalized[:6000],
            features={
                "token_count": token_count,
                "unique_ratio": round(unique_ratio, 4),
                "avg_sentence_length": round(avg_sentence_length, 2),
                "burstiness": round(burstiness, 4),
                "repetition_ratio": round(repetition_ratio, 4),
                "stopword_ratio": round(stopword_ratio, 4),
                "punctuation_ratio": round(punctuation_ratio, 4),
                "markdown_density": round(markdown_density, 4),
                "code_marker_ratio": round(code_marker_ratio, 4),
            },
        )

    @staticmethod
    def _line_length_std(lines: list[str]) -> float:
        if not lines:
            return 0.0
        lengths = [len(line) for line in lines]
        avg = sum(lengths) / len(lengths)
        variance = sum((length - avg) ** 2 for length in lengths) / len(lengths)
        return (variance ** 0.5) / max(1.0, avg)

    @staticmethod
    def _build_explanations(
        probability_ai: float,
        burstiness: float,
        repetition_ratio: float,
        unique_ratio: float,
        ai_phrase_hits: int,
        content_type: str,
    ) -> list[str]:
        notes: list[str] = []
        if burstiness < 0.18:
            notes.append("Sentence and line lengths are unusually uniform, which is common in generated content.")
        if repetition_ratio > 0.18:
            notes.append("Repeated wording patterns were detected across the sample.")
        if unique_ratio < 0.38:
            notes.append("Vocabulary diversity is lower than typical human-authored long-form content.")
        if ai_phrase_hits:
            notes.append("The text contains common assistant-style framing phrases.")
        if content_type == "code":
            notes.append("Code structure was evaluated using style regularity and token burst analysis.")
        if probability_ai < 0.5 and not notes:
            notes.append("Variation in structure and vocabulary is closer to human writing patterns.")
        return notes[:4]


text_detection_service = TextDetectionService()
