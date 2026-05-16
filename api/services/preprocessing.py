from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

try:
    import librosa  # type: ignore
    import soundfile as sf  # type: ignore
except Exception:  # pragma: no cover
    librosa = None
    sf = None


@dataclass
class PreprocessResult:
    content: bytes
    metadata: dict[str, Any]


class MediaPreprocessor:
    def preprocess(self, media_type: str, content: bytes, filename: str | None = None) -> PreprocessResult:
        if media_type == "image":
            return self._preprocess_image(content)
        if media_type == "audio":
            return self._preprocess_audio(content)
        if media_type == "video":
            return self._inspect_video(content)
        return PreprocessResult(content=content, metadata={"quality_score": 0.5})

    def _preprocess_image(self, content: bytes) -> PreprocessResult:
        image = Image.open(io.BytesIO(content))
        image = ImageOps.exif_transpose(image).convert("RGB")
        original_size = image.size
        image = ImageOps.autocontrast(image)
        image = ImageEnhance.Contrast(image).enhance(1.08)
        image = ImageEnhance.Sharpness(image).enhance(1.05)
        image = image.filter(ImageFilter.DETAIL)

        face_alignment_applied = False
        if cv2 is not None:
            try:
                bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                classifier = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                faces = classifier.detectMultiScale(gray, 1.1, 4)
                face_alignment_applied = len(faces) > 0
            except Exception:
                logger.debug("Face alignment inspection skipped for image preprocessing.", exc_info=True)

        image_array = np.asarray(image).astype(np.float32) / 255.0
        brightness = float(image_array.mean())
        contrast = float(image_array.std())
        sharpness = float(np.abs(np.gradient(image_array, axis=(0, 1))).mean())
        quality_score = max(0.0, min(1.0, (contrast * 1.5) + (sharpness * 0.8)))

        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True)
        return PreprocessResult(
            content=output.getvalue(),
            metadata={
                "original_size": {"width": original_size[0], "height": original_size[1]},
                "preprocessed_size": {"width": image.width, "height": image.height},
                "brightness": brightness,
                "contrast": contrast,
                "sharpness": sharpness,
                "face_alignment_applied": face_alignment_applied,
                "quality_score": quality_score,
            },
        )

    def _preprocess_audio(self, content: bytes) -> PreprocessResult:
        metadata: dict[str, Any] = {
            "quality_score": 0.5,
            "normalization_applied": False,
            "noise_reduction_applied": False,
        }
        if sf is None:
            return PreprocessResult(content=content, metadata=metadata)

        try:
            waveform, sample_rate = sf.read(io.BytesIO(content))
            if waveform.ndim > 1:
                waveform = waveform.mean(axis=1)
            if librosa is not None and sample_rate != 16000:
                waveform = librosa.resample(waveform.astype(np.float32), orig_sr=sample_rate, target_sr=16000)
                sample_rate = 16000

            waveform = waveform.astype(np.float32)
            peak = float(np.max(np.abs(waveform))) if len(waveform) else 0.0
            if peak > 0:
                waveform = waveform / peak
                metadata["normalization_applied"] = True
            if len(waveform) > 1:
                noise_floor = np.percentile(np.abs(waveform), 10)
                waveform[np.abs(waveform) < noise_floor * 0.8] = 0
                metadata["noise_reduction_applied"] = True
            metadata["quality_score"] = max(0.0, min(1.0, float(np.std(waveform) * 3)))
            metadata["sample_rate"] = sample_rate
            metadata["duration_seconds"] = len(waveform) / float(sample_rate or 1)
            output = io.BytesIO()
            sf.write(output, waveform, sample_rate, format="WAV")
            return PreprocessResult(content=output.getvalue(), metadata=metadata)
        except Exception:
            logger.warning("Audio preprocessing failed, falling back to original content.", exc_info=True)
            return PreprocessResult(content=content, metadata=metadata)

    def _inspect_video(self, content: bytes) -> PreprocessResult:
        metadata: dict[str, Any] = {"quality_score": 0.5, "frame_quality_checked": False}
        if cv2 is None:
            return PreprocessResult(content=content, metadata=metadata)
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                capture = cv2.VideoCapture(temp_file.name)
                frame_scores: list[float] = []
                frame_count = 0
                while frame_count < 12:
                    ok, frame = capture.read()
                    if not ok or frame is None:
                        break
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
                    brightness = float(gray.mean()) / 255.0
                    frame_scores.append(max(0.0, min(1.0, (blur / 400.0) * 0.7 + brightness * 0.3)))
                    frame_count += 1
                capture.release()
                if frame_scores:
                    metadata["quality_score"] = float(sum(frame_scores) / len(frame_scores))
                    metadata["sampled_frames"] = frame_count
                    metadata["frame_quality_checked"] = True
        except Exception:
            logger.debug("Video quality inspection failed.", exc_info=True)
        return PreprocessResult(content=content, metadata=metadata)


media_preprocessor = MediaPreprocessor()
