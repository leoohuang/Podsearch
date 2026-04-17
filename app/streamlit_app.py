import sys
sys.path.append(".")
from src.audio_clip import get_audio_clip
import os
import streamlit as st
from src.search import search_with_rerank

st.title("PodSearch 播客语义搜索")

query = st.text_input("输入你想搜索的内容")

if query:
    with st.spinner("搜索中..."):
        results = search_with_rerank(query)

    for res in results:
        st.markdown(f"**第{res['rank']}名** | 精排分数：{res['rerank_score']:.3f}")
        st.markdown(f"🎙️ {res['podcast_name']} | ⏰ {res['start']:.0f}s ~ {res['end']:.0f}s")
        st.markdown(f"{res['text'][:200]}...")
        st.divider()

        # 播放按钮
        audio_path = res.get("audio_file", "")
        if audio_path and os.path.exists(audio_path):
            clip_path = get_audio_clip(audio_path, res["start"], res["end"])
            with open(clip_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        st.divider()