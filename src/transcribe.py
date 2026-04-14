from faster_whisper import WhisperModel
import json
from pathlib import Path
from tqdm import tqdm 
from src.config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE,
    TRANSCRIPT_DIR
)

_model = None

def get_model():
    global _model
    if _model is None:
        print(f"Loading model: {WHISPER_MODEL}")
        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE
        )
    return _model

def transcribe(audio_path: str | Path, lang: str = None) -> dict:
    model = get_model()
    print(f"\nTrascribing...：{audio_path}")

    segments, info = model.transcribe(
        audio_path,
        language=lang,
        vad_filter=True,
        beam_size=5
    )

    segment_list = []
    print("reading transcribed results...")
    for s in tqdm(segments, desc="转录进度", unit="段"):
        segment_list.append({
            "start": s.start,
            "end": s.end,
            "text": s.text
        })

    result = {
        "audio_path": str(audio_path),
        "language": info.language,
        "duration": info.duration,
        "segments": segment_list
    }
    return result

def save_transcript(audio_path: str | Path, lang: str = None) -> Path:
    data = transcribe(audio_path, lang=lang)

    audio_path = Path(audio_path)
    json_filename = audio_path.stem + ".json"
    out_path = TRANSCRIPT_DIR / json_filename

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅completed transcribe!{out_path}")
    return out_path