from datetime import date, datetime, timedelta
import time
import streamlit as st

# 页面基础配置
st.set_page_config(
    page_title="小星星语数英学习与听写打卡中心", page_icon="🌟", layout="wide"
)

# 🎨 现代化高颜值 UI 样式注入
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4fbf7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-header {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
    }
    .app-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #e5e7eb;
    }
    .card-title {
        font-size: 20px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 16px;
    }
    .subject-title {
        font-size: 16px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 12px;
        border-bottom: 2px solid #f3f4f6;
        padding-bottom: 6px;
    }
    .stButton button {
        width: 100%;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        background-color: #f8fafc !important;
        color: #334155 !important;
        border: 1px solid #cbd5e1 !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }
    .timer-display-box {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 12px 30px rgba(16, 185, 129, 0.25);
    }
    .timer-huge-nums {
        font-size: 82px;
        font-weight: 800;
        letter-spacing: 3px;
        font-family: monospace;
        margin: 12px 0;
    }
    @keyframes blink-warning {
        0% { color: #ffffff; }
        50% { color: #fecaca; }
        100% { color: #ffffff; }
    }
    .blink-text {
        animation: blink-warning 1s infinite;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 初始化状态数据
if "daily_tracking" not in st.session_state:
  st.session_state.daily_tracking = {}
if "weekly_tracking" not in st.session_state:
  st.session_state.weekly_tracking = {}

# 计时器专属独立状态
if "timer_status" not in st.session_state:
  st.session_state.timer_status = "STOPPED"  # "STOPPED", "RUNNING", "PAUSED"
if "time_left" not in st.session_state:
  st.session_state.time_left = 0
if "t_count" not in st.session_state:
  st.session_state.t_count = 10
if "t_sec" not in st.session_state:
  st.session_state.t_sec = 12
if "t_buf" not in st.session_state:
  st.session_state.t_buf = 30

# 顶栏头部
st.markdown(
    """
    <div class="top-header">
        <h2 style="margin:0; font-size:24px; color:#111827; font-weight:800;">🌟 小星星语数英学习与听写打卡中心</h2>
        <p style="margin:6px 0 0 0; font-size:14px; color:#4b5563;">每日任务跟催 ＋ 每周统筹大目标 ＋ 智能听写计时器</p>
    </div>
""",
    unsafe_allow_html=True,
)

# 分栏标签（独立拆分，清晰不拥挤）
tab_daily, tab_weekly, tab_timer = st.tabs(
    ["📅 每日任务跟催看板", "📌 每周统筹看板", "⏱️ 智能听写大屏计时器"]
)


# ==================== 1. 📅 每日任务跟催看板 ====================
with tab_daily:
  st.markdown("### 📅 本周每日必做 (Day) 学习跟催")
  st.markdown(
      "独立管理周一至周日每一天的日常学科子任务，随时勾选查看单日过关情况。"
  )
  st.write("")

  today = date.today()
  start_of_week = today - timedelta(days=today.weekday())
  week_days = [start_of_week + timedelta(days=i) for i in range(7)]
  day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

  for idx, d_obj in enumerate(week_days):
    d_str = d_obj.strftime("%Y-%m-%d")
    is_today = d_obj == today

    if d_str not in st.session_state.daily_tracking:
      st.session_state.daily_tracking[d_str] = {
          "语文_一课一练": False,
          "语文_读写": False,
          "语文_S级": False,
          "语文_听写": False,
          "语文_阅读": False,
          "语文_订正": False,
          "数学_计算": False,
          "数学_一课一练": False,
          "数学_错题跟进": False,
          "数学_订正": False,
          "英语_RAZ读": False,
          "英语_听力内区": False,
          "英语_听写": False,
          "英语_错题跟进": False,
          "英语_订正": False,
      }

    day_data = st.session_state.daily_tracking[d_str]
    t_cnt = len(day_data)
    c_cnt = sum(1 for v in day_data.values() if v)
    pct = int((c_cnt / t_cnt) * 100)

    card_border = (
        "border-left: 6px solid #10b981;"
        if is_today
        else "border-left: 6px solid #cbd5e1;"
    )

    st.markdown(
        f'<div class="app-card" style="{card_border}">', unsafe_allow_html=True
    )
    marker = "🌟 【今天】" if is_today else "📌"
    st.markdown(
        f'<div class="card-title">{marker} {day_names[idx]} <span style="font-size:14px; color:#4b5563; font-weight:normal; margin-left:8px;">({d_str})</span> <span style="margin-left:auto; font-size:15px; color:#059669;">完成度: {c_cnt}/{t_cnt} ({pct}%)</span></div>',
        unsafe_allow_html=True,
    )
    st.progress(pct / 100)
    st.write("")

    dc1, dc2, dc3 = st.columns(3)


    def render_d_btn(date_k, task_k, label):
      done = day_data[task_k]
      txt = f"✅ {label}" if done else f"⬜ {label}"
      if st.button(txt, key=f"db_{date_k}_{task_k}"):
        day_data[task_k] = not done
        st.rerun()


    with dc1:
      st.markdown(
          '<div class="subject-title">📖 语文 (100\')</div>',
          unsafe_allow_html=True,
      )
      render_d_btn(d_str, "语文_一课一练", "一课一练 (20')")
      render_d_btn(d_str, "语文_读写", "读写 (30')")
      render_d_btn(d_str, "语文_S级", "S级 (10')")
      render_d_btn(d_str, "语文_听写", "听写 (10')")
      render_d_btn(d_str, "语文_阅读", "阅读 (30')")
      render_d_btn(d_str, "语文_订正", "订正 (10')")

    with dc2:
      st.markdown(
          '<div class="subject-title">🔢 数学 (75\')</div>',
          unsafe_allow_html=True,
      )
      render_d_btn(d_str, "数学_计算", "计算 (15')")
      render_d_btn(d_str, "数学_一课一练", "一课一练 (30')")
      render_d_btn(d_str, "数学_错题跟进", "错题跟进 (20')")
      render_d_btn(d_str, "数学_订正", "订正 (10')")

    with dc3:
      st.markdown(
          '<div class="subject-title">🔤 英语 (105\')</div>',
          unsafe_allow_html=True,
      )
      render_d_btn(d_str, "英语_RAZ读", "RAZ读/读力 (40')")
      render_d_btn(d_str, "英语_听力内区", "RAZ/内区 (30')")
      render_d_btn(d_str, "英语_听写", "听写 (10')")
      render_d_btn(d_str, "英语_错题跟进", "错题跟进 (15')")
      render_d_btn(d_str, "英语_订正", "订正 (10')")

    st.markdown("</div>", unsafe_allow_html=True)


# ==================== 2. 📌 每周统筹看板 ====================
with tab_weekly:
  st.markdown("### 📌 每周大统筹任务看板 (Week Goals)")
  st.markdown(
      "独立查看和跟进本周的综合大目标（如大语文、奥数拔高、英语专项等全周统筹进度）。"
  )
  st.write("")

  st.markdown('<div class="app-card">', unsafe_allow_html=True)
  st.markdown(
      '<div class="card-title">🎯 本周综合统筹总览</div>', unsafe_allow_html=True
  )

  week_key = "2026-Current-Week"
  if week_key not in st.session_state.weekly_tracking:
    st.session_state.weekly_tracking[week_key] = {
        "周_语文大语文": False,
        "周_数学卷子奥数": False,
        "周_英语专项单词": False,
    }
  w_data = st.session_state.weekly_tracking[week_key]
  w_tot = len(w_data)
  w_done = sum(1 for v in w_data.values() if v)
  w_pct = int((w_done / w_tot) * 100)

  st.progress(
      w_pct / 100, text=f"本周统筹总完成进度：{w_pct}% （{w_done}/{w_tot}）"
  )
  st.write("")

  wc1, wc2, wc3 = st.columns(3)


  def render_w_btn(key, label):
    done = w_data[key]
    txt = f"✅ {label}" if done else f"⬜ {label}"
    if st.button(txt, key=f"wb_{key}"):
      w_data[key] = not done
      st.rerun()


  with wc1:
    render_w_btn("周_语文大语文", "📖 语文：大语文/现代文 (60')")
  with wc2:
    render_w_btn("周_数学卷子奥数", "🔢 数学：卷子/奥数拔高")
  with wc3:
    render_w_btn("周_英语专项单词", "🔤 英语：单词/英读专项")

  st.markdown("</div>", unsafe_allow_html=True)


# ==================== 3. ⏱️ 智能听写大屏计时器 ====================
with tab_timer:
  st.markdown("### ⏱️ 报听写大屏计时器工具")
  st.markdown(
      "自由调整数量与时间，点击开始后独立倒计时。暂停键可随时冻结时间，重置键可恢复初始总时长。"
  )
  st.write("")

  st.markdown('<div class="app-card">', unsafe_allow_html=True)
  st.markdown(
      '<div class="card-title">⚙️ 听写参数设置</div>', unsafe_allow_html=True
  )

  tc1, tc2, tc3 = st.columns(3)

  with tc1:
    st.markdown(
        "<span style='font-size:15px; font-weight:700;'>📝 听写总数量（个）</span>",
        unsafe_allow_html=True,
    )
    b1, b2, b3 = st.columns([1, 2, 1])
    with b1:
      if st.button("➖", key="tc_sub"):
        if st.session_state.t_count > 1:
          st.session_state.t_count -= 1
          st.rerun()
    with b2:
      st.markdown(
          f"<h2 style='text-align: center; margin:0; color:#059669;'>{st.session_state.t_count}</h2>",
          unsafe_allow_html=True,
      )
    with b3:
      if st.button("➕", key="tc_add"):
        st.session_state.t_count += 1
        st.rerun()

  with tc2:
    st.markdown(
        "<span style='font-size:15px; font-weight:700;'>⏳ 每题间隔（秒）</span>",
        unsafe_allow_html=True,
    )
    s1, s2, s3 = st.columns([1, 2, 1])
    with s1:
      if st.button("➖", key="ts_sub"):
        if st.session_state.t_sec > 2:
          st.session_state.t_sec -= 1
          st.rerun()
    with s2:
      st.markdown(
          f"<h2 style='text-align: center; margin:0; color:#059669;'>{st.session_state.t_sec}s</h2>",
          unsafe_allow_html=True,
      )
    with s3:
      if st.button("➕", key="ts_add"):
        st.session_state.t_sec += 1
        st.rerun()

  with tc3:
    st.markdown(
        "<span style='font-size:15px; font-weight:700;'>➕ 额外缓冲（秒）</span>",
        unsafe_allow_html=True,
    )
    bu1, bu2, bu3 = st.columns([1, 2, 1])
    with bu1:
      if st.button("➖", key="tb_sub"):
        if st.session_state.t_buf >= 5:
          st.session_state.t_buf -= 5
          st.rerun()
    with bu2:
      st.markdown(
          f"<h2 style='text-align: center; margin:0; color:#059669;'>{st.session_state.t_buf}s</h2>",
          unsafe_allow_html=True,
      )
    with bu3:
      if st.button("➕", key="tb_add"):
        st.session_state.t_buf += 5
        st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)

  total_secs = (
      st.session_state.t_count * st.session_state.t_sec
  ) + st.session_state.t_buf
  t_mins = total_secs // 60
  t_rem = total_secs % 60

  st.info(
      f"📊 **节奏精算**：{st.session_state.t_count} 个单词 ×"
      f" {st.session_state.t_sec} 秒 ＋ 缓冲 {st.session_state.t_buf} 秒"
      f" ＝ 总耗时 **{total_secs} 秒** （约合 **{t_mins} 分 {t_rem} 秒**）"
  )
  st.write("")

  # 根据计时器状态计算当前应显示的时间
  if st.session_state.timer_status == "STOPPED":
    disp_secs = total_secs
  else:
    disp_secs = st.session_state.time_left

  d_mins = disp_secs // 60
  d_secs = disp_secs % 60

  is_running = st.session_state.timer_status == "RUNNING"
  is_warning = is_running and disp_secs <= 15
  num_cls = "timer-huge-nums blink-text" if is_warning else "timer-huge-nums"

  status_text = (
      "🔥 听写倒计时进行中..."
      if is_running
      else ("⏸️ 计时已暂停" if st.session_state.timer_status == "PAUSED" else "⏳ 准备就绪")
  )

  st.markdown(
      f"""
      <div class="timer-display-box">
          <div style="font-size:16px; font-weight:600; opacity:0.9;">{status_text}</div>
          <div class="{num_cls}">{d_mins:02d} : {d_secs:02d}</div>
          <div style="font-size:15px; opacity:0.9;">{'⚠️ 注意！最后 15 秒即将结束！' if is_warning else '保持好听写节奏，从容不迫'}</div>
      </div>
  """,
      unsafe_allow_html=True,
  )

  if is_running and disp_secs == 15:
    st.markdown(
        """
        <script>
        const u = new SpeechSynthesisUtterance("注意，最后十五秒！");
        u.lang = "zh-CN";
        window.speechSynthesis.speak(u);
        </script>
    """,
        unsafe_allow_html=True,
    )

  act1, act2, act3 = st.columns(3)
  with act1:
    btn_start = st.button("🚀 开始 / 继续", type="primary", key="tr_start")
  with act2:
    btn_pause = st.button("⏸️ 暂停", key="tr_pause")
  with act3:
    btn_reset = st.button("🔄 重置时间", key="tr_reset")

  if btn_start:
    if st.session_state.timer_status == "STOPPED":
      st.session_state.time_left = total_secs
    st.session_state.timer_status = "RUNNING"
    st.rerun()

  if btn_pause:
    if st.session_state.timer_status == "RUNNING":
      st.session_state.timer_status = "PAUSED"
      st.rerun()

  if btn_reset:
    st.session_state.timer_status = "STOPPED"
    st.session_state.time_left = total_secs
    st.rerun()

  # 倒计时循环执行逻辑
  if st.session_state.timer_status == "RUNNING":
    if st.session_state.time_left > 0:
      time.sleep(1)
      st.session_state.time_left -= 1
      st.rerun()
    else:
      st.session_state.timer_status = "STOPPED"
      st.balloons()
      st.markdown(
          """
          <script>
          const u2 = new SpeechSynthesisUtterance("听写时间到，请收卷！");
          u2.lang = "zh-CN";
          window.speechSynthesis.speak(u2);
          </script>
      """,
          unsafe_allow_html=True,
      )
      st.success("🎉 时间到！听写顺利结束！")