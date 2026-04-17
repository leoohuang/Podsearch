import sys
sys.path.append(".")

import os
import streamlit as st
from src.search import search_with_rerank
from src.audio_clip import get_audio_clip

# ===== 页面配置 =====
st.set_page_config(page_title="PodSearch", page_icon="🎙️", layout="wide")

# ===== 自定义样式 =====
st.markdown("""
<style>
    .result-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 4px solid #ff6b6b;
    }
    .rank-badge {
        display: inline-block;
        background-color: #ff6b6b;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: bold;
    }
    .score-text {
        color: #666;
        font-size: 14px;
    }
    .podcast-name {
        font-size: 16px;
        font-weight: bold;
        color: #333;
    }
    .time-badge {
        display: inline-block;
        background-color: #e9ecef;
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 13px;
        color: #555;
    }
    .transcript-text {
        color: #444;
        line-height: 1.6;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## 🎛️ 筛选")
    st.markdown("---")

    from src.indexing import get_collection
    col = get_collection()
    all_metadata = col.get(include=["metadatas"])["metadatas"]
    all_podcasts = sorted(set(
        os.path.basename(os.path.dirname(m.get("audio", ""))).replace("_", " ")
        for m in all_metadata if m.get("audio")
    ))

    selected_podcasts = st.multiselect("选择播客", all_podcasts, default=all_podcasts)
    st.markdown("---")
    st.markdown("*💡 取消勾选可过滤特定播客*")

# ===== 主区域 =====
st.markdown("# 🎙️ PodSearch")
st.markdown("*语义搜索你的播客内容*")
st.markdown("")

query = st.text_input("搜索", placeholder="试试：AI时代的焦虑、创业心态、英语学习方法...")

if query:
    with st.spinner("🔍 搜索中，正在召回 + 精排..."):
        results = search_with_rerank(query)

    filtered = [r for r in results if r["podcast_name"] in selected_podcasts]

    if not filtered:
        st.warning("没有找到匹配的结果，试试换个关键词或调整筛选条件")
    else:
        st.markdown(f"找到 **{len(filtered)}** 条相关结果")
        st.markdown("")

    for res in filtered:
        minutes = int(res['start'] // 60)
        seconds = int(res['start'] % 60)
        end_min = int(res['end'] // 60)
        end_sec = int(res['end'] % 60)

        st.markdown(f"""
        <div class="result-card">
            <span class="rank-badge">#{res['rank']}</span>
            <span class="score-text">精排分数 {res['rerank_score']:.3f}</span>
            <br><br>
            <span class="podcast-name">🎙️ {res['podcast_name']}</span>
            <br>
            <span class="time-badge">⏰ {minutes:02d}:{seconds:02d} ~ {end_min:02d}:{end_sec:02d}</span>
            <br><br>
            <span class="transcript-text">{res['text'][:250]}...</span>
        </div>
        """, unsafe_allow_html=True)

        audio_path = res.get("audio_file", "")
        if audio_path and os.path.exists(audio_path):
            clip_path = get_audio_clip(audio_path, res["start"], res["end"])
            with open(clip_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")