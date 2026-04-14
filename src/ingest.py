# src/ingest.py
import re
import requests
import feedparser
from pathlib import Path
from tqdm import tqdm
from src.config import AUDIO_DIR

UA = "Mozilla/5.0 (podcast-ingest/1.0)"
HEADERS = {"User-Agent": UA}


def slugify(s: str, max_len: int = 80) -> str:
    """把任意字符串变成安全的文件名片段"""
    s = re.sub(r"[^\w\-. ]", "_", s).strip().replace(" ", "_")
    return s[:max_len] or "untitled"


def search_podcast_feed(name: str, country: str = "us") -> dict:
    """通过 iTunes Search API 找 RSS feed URL，返回完整信息而非只有 URL"""
    url = "https://itunes.apple.com/search"
    params = {"term": name, "media": "podcast", "limit": 5, "country": country}
    r = requests.get(url, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        raise ValueError(f"No podcast found for: {name}")
    top = results[0]
    return {
        "feed_url": top["feedUrl"],
        "name": top["collectionName"],
        "artist": top.get("artistName"),
        "slug": slugify(top["collectionName"]),
    }
 

def _extract_audio_url(ep) -> str | None:
    """从 feed entry 中提取音频 URL，兼容 enclosures 和 links 两种形式"""
    # 优先 enclosures（RSS 标准）
    for enc in getattr(ep, "enclosures", []) or []:
        if "audio" in enc.get("type", ""):
            return enc.get("href") or enc.get("url")
    # 兜底 links
    for l in getattr(ep, "links", []) or []:
        if "audio" in getattr(l, "type", ""):
            return l.href
    return None


def _download_file(url: str, dest: Path) -> bool:
    """下载到 dest，支持断点续传，原子写入。返回是否成功。"""
    part = dest.with_suffix(dest.suffix + ".part")
    resume_from = part.stat().st_size if part.exists() else 0

    headers = dict(HEADERS)
    if resume_from:
        headers["Range"] = f"bytes={resume_from}-"

    with requests.get(url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0)) + resume_from
        mode = "ab" if resume_from and r.status_code == 206 else "wb"
        if mode == "wb":
            resume_from = 0  # 服务器不支持 Range，从头来

        with open(part, mode) as f, tqdm(
            total=total, initial=resume_from, unit="B", unit_scale=True,
            desc=dest.name[:40],
        ) as pbar:
            for chunk in r.iter_content(8192):
                f.write(chunk)
                pbar.update(len(chunk))

    part.rename(dest)  # 原子完成
    return True 


def download_episodes(feed_url: str, podcast_slug: str, n: int = 10) -> list[dict]:
    """下载一个播客的最近 n 集"""
    feed = feedparser.parse(feed_url)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Failed to parse feed: {feed.bozo_exception}")

    out_dir = AUDIO_DIR / podcast_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    episodes = []
    for ep in feed.entries[:n]:
        audio_url = _extract_audio_url(ep)
        if not audio_url:
            print(f"[skip] no audio: {ep.get('title', '?')}")
            continue

        ep_id = ep.get("id") or ep.get("guid") or ep.get("title", "ep")
        filename = out_dir / f"{slugify(ep_id)}.mp3"

        if not filename.exists():
            try:
                _download_file(audio_url, filename)
            except Exception as e:
                print(f"[fail] {ep.get('title', '?')}: {e}")
                continue

        episodes.append({
            "id": ep.get("id"),
            "title": ep.get("title"),
            "published": ep.get("published"),
            "duration": ep.get("itunes_duration"),
            "file": str(filename),
            "podcast": podcast_slug,
        })
    return episodes


def ingest(name: str, n: int = 10, country: str = "us") -> list[dict]:
    """一步到位：按名字搜 + 下载"""
    info = search_podcast_feed(name, country=country)
    print(f"Found: {info['name']} by {info['artist']}")
    return download_episodes(info["feed_url"], info["slug"], n=n)


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "Lex Fridman Podcast"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    eps = ingest(name, n=n)
    print(f"\nDownloaded {len(eps)} episodes")