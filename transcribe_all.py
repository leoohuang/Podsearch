from pathlib import Path
from src.transcribe import save_transcript
from src.config import AUDIO_DIR


def batch_transcribe():
    # 遍历所有 mp3（递归所有子文件夹）
    audio_files = list(AUDIO_DIR.rglob("*.mp3"))

    if not audio_files:
        print("no any audio file!")
        return

    print(f"Find {len(audio_files)} audio files, transcribing...\n")

    # 逐个转录
    success = 0
    failed = 0

    for idx, path in enumerate(audio_files, 1):
        print(f"===== [{idx}/{len(audio_files)}] Processing:{path.name} =====")

        try:
            save_transcript(path, lang=None)
            success += 1
            print(f"Success!\n")

        except Exception as e:
            failed += 1
            print(f"failed:{str(e)}\n")

    # 最终统计
    print("=" * 50)
    print(f"Successfully transcribed!")
    print(f"successed:{success} ")
    print(f"failed:{failed} 个")
    print(f"saved to:data/transcripts/")
    print("=" * 50)


if __name__ == "__main__":
    batch_transcribe()