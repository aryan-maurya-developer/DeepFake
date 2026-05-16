from __future__ import annotations

import io
import math
import mimetypes
import zipfile
from pathlib import Path
from typing import Any


SUSPICIOUS_EXTENSIONS = {".exe", ".dll", ".bat", ".cmd", ".ps1", ".js", ".vbs", ".scr", ".jar", ".msi"}
SCRIPT_PATTERNS = [b"<script", b"powershell", b"wscript", b"cmd.exe", b"base64,", b"fromcharcode"]
EXECUTABLE_SIGNATURES = {
    "pe": b"MZ",
    "elf": b"\x7fELF",
    "mach_o": b"\xcf\xfa\xed\xfe",
    "java_archive": b"PK\x03\x04",
}


class FileSafetyService:
    def analyze(self, filename: str, content: bytes) -> dict[str, Any]:
        ext = Path(filename).suffix.lower()
        mime_type, _ = mimetypes.guess_type(filename)
        detected_signatures = [name for name, signature in EXECUTABLE_SIGNATURES.items() if content.startswith(signature)]
        entropy = self._estimate_entropy(content[:4096])
        suspicious_hits = [pattern.decode("utf-8", errors="ignore") for pattern in SCRIPT_PATTERNS if pattern in content[:200000].lower()]
        macros_detected = self._detect_office_macros(content, ext)
        mismatch = bool(detected_signatures and ext not in SUSPICIOUS_EXTENSIONS and ext not in {".zip", ".docm", ".xlsm"})
        risk_score = 0
        reasons: list[str] = []

        if ext in SUSPICIOUS_EXTENSIONS:
            risk_score += 35
            reasons.append(f"The file extension `{ext}` is commonly associated with executable or script payloads.")
        if detected_signatures:
            risk_score += 25
            reasons.append(f"Executable signature(s) detected: {', '.join(detected_signatures)}.")
        if mismatch:
            risk_score += 15
            reasons.append("The file signature does not match a typical document or media payload.")
        if suspicious_hits:
            risk_score += min(20, len(suspicious_hits) * 5)
            reasons.append("Embedded script-like or obfuscation-related patterns were found.")
        if macros_detected:
            risk_score += 20
            reasons.append("Office macro artifacts were detected inside the document container.")
        if entropy > 7.2:
            risk_score += 10
            reasons.append("High byte entropy suggests compression, packing, or obfuscation.")

        risk_score = min(100, risk_score)
        risk_level = "safe" if risk_score < 20 else "suspicious" if risk_score < 55 else "high-risk"
        quarantine = risk_score >= 45

        return {
            "filename": filename,
            "extension": ext,
            "mime_type": mime_type or "application/octet-stream",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_safe": risk_score < 20,
            "quarantine_recommended": quarantine,
            "explanation": reasons or ["No strong static malware indicators were detected in the uploaded file."],
            "detected_signatures": detected_signatures,
            "suspicious_patterns": suspicious_hits,
            "macros_detected": macros_detected,
            "entropy": round(entropy, 3),
        }

    @staticmethod
    def _detect_office_macros(content: bytes, ext: str) -> bool:
        if ext not in {".docm", ".xlsm", ".pptm", ".docx", ".xlsx", ".pptx"}:
            return False
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                return any("vbaProject.bin" in name or "macros/" in name.lower() for name in archive.namelist())
        except Exception:
            return False

    @staticmethod
    def _estimate_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        counts = {}
        for byte in data:
            counts[byte] = counts.get(byte, 0) + 1
        total = len(data)
        return -sum((count / total) * math.log2(count / total) for count in counts.values())


file_safety_service = FileSafetyService()
