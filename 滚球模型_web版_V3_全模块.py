
import streamlit as st
import pandas as pd

st.set_page_config(page_title="滚球进球&角球&盘口分析系统", layout="wide")

st.title("⚽ 滚球自动分析系统 V3")
st.markdown("模块：进球追击 + 角球分析 + 下一球预测 + 盘口变化")
st.markdown("---")

st.subheader("输入比赛数据（支持多场）")

num_matches = st.number_input("比赛场数", 1, 10, 3)

match_data = []
for i in range(num_matches):
    st.markdown(f"### 比赛 {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        match = st.text_input(f"比赛名称 {i+1}", key=f"match_{i}")
        time = st.number_input(f"时间（分钟） {i+1}", 0, 120, key=f"time_{i}")
        score = st.text_input(f"比分（如1-1） {i+1}", key=f"score_{i}")
        corners = st.number_input(f"总角球数 {i+1}", 0, key=f"corners_{i}")
        next_goal_odds_home = st.number_input(f"主队进下一球赔率 {i+1}", min_value=1.0, step=0.01, key=f"ngo_home_{i}")
        next_goal_odds_away = st.number_input(f"客队进下一球赔率 {i+1}", min_value=1.0, step=0.01, key=f"ngo_away_{i}")
    with col2:
        shots_home = st.number_input(f"主射门数 {i+1}", 0, key=f"shots_home_{i}")
        shots_away = st.number_input(f"客射门数 {i+1}", 0, key=f"shots_away_{i}")
        target_home = st.number_input(f"主射正数 {i+1}", 0, key=f"target_home_{i}")
        target_away = st.number_input(f"客射正数 {i+1}", 0, key=f"target_away_{i}")
        last_odds = st.number_input(f"开赛时大球赔率 {i+1}", min_value=1.0, step=0.01, key=f"last_odds_{i}")
    with col3:
        poss_home = st.number_input(f"主控球% {i+1}", 0, 100, key=f"poss_home_{i}")
        poss_away = st.number_input(f"客控球% {i+1}", 0, 100, key=f"poss_away_{i}")
        current_odds = st.number_input(f"当前大球赔率 {i+1}", min_value=1.0, step=0.01, key=f"current_odds_{i}")

    match_data.append({
        "比赛": match,
        "时间": time,
        "比分": score,
        "总角球": corners,
        "主射门": shots_home,
        "客射门": shots_away,
        "主射正": target_home,
        "客射正": target_away,
        "主控球": poss_home,
        "客控球": poss_away,
        "初始大球赔率": last_odds,
        "当前大球赔率": current_odds,
        "主下一球赔率": next_goal_odds_home,
        "客下一球赔率": next_goal_odds_away
    })

# 评分逻辑
def get_goal_score(row):
    score = 0
    if row["时间"] >= 60:
        score += 2
    if row["比分"] in ["0-0", "1-1", "1-2", "2-2"]:
        score += 1
    if row["主射门"] + row["客射门"] >= 20:
        score += 2
    if row["主射正"] + row["客射正"] >= 8:
        score += 2
    if abs(row["主控球"] - row["客控球"]) <= 15:
        score += 1
    if row["当前大球赔率"] > 1.90:
        score += 1
    return score

def get_goal_recommend(score):
    if score >= 7:
        return "✅ 推荐追大球"
    elif score >= 5:
        return "⚠️ 可观望"
    else:
        return "❌ 不建议"

def get_corner_recommend(row):
    pace = row["总角球"] / (row["时间"] + 1) * 90
    if pace >= 11:
        return "✅ 角球节奏快，可追"
    elif pace >= 9:
        return "⚠️ 较快，可关注"
    else:
        return "❌ 节奏慢，暂不建议"

def get_next_goal_recommend(row):
    if row["主射正"] > row["客射正"] + 2 and row["主下一球赔率"] < 2.3:
        return "主队有望进下一球"
    elif row["客射正"] > row["主射正"] + 2 and row["客下一球赔率"] < 2.3:
        return "客队有望进下一球"
    else:
        return "⚠️ 形势不明"

def get_odds_change(row):
    delta = row["当前大球赔率"] - row["初始大球赔率"]
    if delta <= -0.2:
        return "✅ 盘口下调，进球被看好"
    elif delta >= 0.2:
        return "❌ 盘口上调，进球不被看好"
    else:
        return "⚠️ 盘口变化不大"

# 输出表格
if st.button("分析所有比赛"):
    df = pd.DataFrame(match_data)
    df["进球评分"] = df.apply(get_goal_score, axis=1)
    df["进球建议"] = df["进球评分"].apply(get_goal_recommend)
    df["角球建议"] = df.apply(get_corner_recommend, axis=1)
    df["下一球预测"] = df.apply(get_next_goal_recommend, axis=1)
    df["盘口变化"] = df.apply(get_odds_change, axis=1)

    st.success("分析完成！")
    st.dataframe(df[["比赛", "时间", "比分", "总角球", "进球建议", "角球建议", "下一球预测", "盘口变化"]], use_container_width=True)
