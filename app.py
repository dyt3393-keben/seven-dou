import base64
from datetime import date, datetime, timedelta
from io import BytesIO
import time
from PIL import Image
import requests
import streamlit as st

# 页面基础配置（宽屏模式，完美适配 iPad）
st.set_page_config(
    page_title="小星星学习与错题乐园", page_icon="🌟", layout="wide"
)

# 自定义全局 CSS 样式：超大号字体、现代化卡片、大触控按钮
st.markdown(
    """
    <style>
    /* 全局标题与卡片优化 */
    h3 {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #1E3A8A !important;
    }
    /* 统一样式：让打卡和常规按钮变得更大更好按 */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-size: 16px !important;
        font-weight: bold !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        border: 1px solid #cbd5e1;
    }
    /* 计时器特大号数字样式 */
    .timer-display {
        font-size: 75px !important;
        font-weight: 800 !important;
        text-align: center;
        letter-spacing: 2px;
        margin: 10px 0;
    }
    .timer-normal {
        color: #1E3A8A !important;
    }
    .timer-warning {
        color: #DC2626 !important; /* 最后15秒红色警示 */
        animation: pulse 1s infinite;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 初始化 Session State 数据存储
if "study_progress" not in st.session_state:
  st.session_state.study_progress = {}

if "wrong_questions" not in st.session_state:
  st.session_state.wrong_questions = [
      {
          "id": "w1",
          "subject": "math",
          "desc": (
              "【环形公路运费最优化】A仓库存库40吨，B库5吨...求完成运输计划最少需要多少元运费？"
          ),
          "img": "",
          "fixed": False,
          "selected": True,
          "date": "2026-03-30",
      }
  ]

if "net_links" not in st.session_state:
  st.session_state.net_links = {
      "第301讲.四则运算一-[1.基础计算].mp4": "https://pan.quark.cn/",
      "第301讲.四则运算一-[2.添去括号凑整].mp4": "https://pan.quark.cn/",
  }

if "daily_tracking" not in st.session_state:
  st.session_state.daily_tracking = {}

if "weekly_tracking" not in st.session_state:
  st.session_state.weekly_tracking = {}

# 听写计时器状态初始化
if "timer_running" not in st.session_state:
  st.session_state.timer_running = False
if "time_left" not in st.session_state:
  st.session_state.time_left = 0
if "t_count" not in st.session_state:
  st.session_state.t_count = 10
if "t_sec" not in st.session_state:
  st.session_state.t_sec = 12
if "t_buf" not in st.session_state:
  st.session_state.t_buf = 30

# 顶部主标题
st.title("🌟 小星星学习与错题乐园")
st.caption(
    "iPad 专属：全周矩阵看板 + 每周统筹 + 网盘打卡 + 智能听写计时器 + 本地"
    " minicpm-v视觉错题本"
)

# 导航标签页
(
    tab_track,
    tab_week,
    tab_study,
    tab_timer,
    tab_wrong,
    tab_print,
    tab_settings,
) = st.tabs([
    "📅 全周每日矩阵看板",
    "📌 每周统筹 (Week) 看板",
    "📚 课程打卡",
    "⏱️ 听写计时器",
    "📝 错题跟进与 AI 提取",
    "🖨️ 生成无答案抽查试卷",
    "⚙️ 系统设置与网盘配置",
])


# 辅助函数：调用本地 Ollama (minicpm-v 视觉大模型) 进行单题精细提取与去噪
def ai_extract_question_ollama(
    image_bytes, ollama_url="http://localhost:11434"
):
  try:
    base64_img = base64.b64encode(image_bytes).decode("utf-8")
    prompt = (
        "这是一张包含多道练习题和手写批改痕迹的试卷照片。"
        "请仔细观察，挑出其中最核心的**那道错题**。"
        "必须严格执行以下要求："
        "1. 只提取并返回最核心的**单道题目**的印刷体文字及选项，不要抄录整页。"
        "2. 完全过滤、忽略、擦除所有的手写草稿、计算步骤、红叉、勾选或已写答案。"
        "3. 输出格式直接为题目文本，不要多余的客套话。"
    )

    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": "minicpm-v",
            "prompt": prompt,
            "images": [base64_img],
            "stream": False,
        },
        timeout=180,
    )

    if response.status_code == 200:
      return response.json().get("response", "").strip()
    else:
      return f"Ollama 响应错误 (状态码 {response.status_code}): {response.text}"
  except requests.exceptions.ConnectionError:
    return (
        "连接 Ollama 失败！请确保本地终端已启动 Ollama 服务 (http://localhost:11434)."
    )
  except Exception as e:
    return f"本地视觉 AI 识别失败: {str(e)}"


# ==================== 1. 📅 全周每日矩阵看板 ====================
with tab_track:
  st.subheader("📅 本周每日必做 (Day) 全景矩阵看板")
  st.markdown(
      "💡 **使用指南**：下方完整展开了**本周一至周日**的所有学习任务。"
      "每个科目下的子任务点击即可切换状态，上方实时显示每天的独立进度！"
  )
  st.divider()

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
    total_items = len(day_data)
    completed_items = sum(1 for v in day_data.values() if v)
    progress_percent = int((completed_items / total_items) * 100)

    chn_keys = [k for k in day_data.keys() if "语文" in k]
    math_keys = [k for k in day_data.keys() if "数学" in k]
    eng_keys = [k for k in day_data.keys() if "英语" in k]

    chn_done = sum(1 for k in chn_keys if day_data[k])
    math_done = sum(1 for k in math_keys if day_data[k])
    eng_done = sum(1 for k in eng_keys if day_data[k])

    with st.container(border=True):
      header_marker = "🌟 【今天】" if is_today else "📌"
      st.markdown(
          f"### {header_marker} {day_names[idx]} ({d_str}) &nbsp;&nbsp;|&nbsp;&nbsp;"
          f" 总进度: **{completed_items}/{total_items}** ({progress_percent}%)"
      )
      st.progress(progress_percent / 100)

      col_c1, col_c2, col_c3 = st.columns(3)


      def render_task_btn(task_key, label_text):
        is_done = day_data[task_key]
        btn_label = f"✅ {label_text}" if is_done else f"⬜ {label_text}"
        if st.button(
            btn_label, key=f"mat_{d_str}_{task_key}", use_container_width=True
        ):
          day_data[task_key] = not is_done
          st.rerun()


      with col_c1:
        st.markdown(
            f"**📖 语文 (100')** —— 已完成 {chn_done}/{len(chn_keys)}"
        )
        render_task_btn("语文_一课一练", "一课一练 (20')")
        render_task_btn("语文_读写", "读写 (30')")
        render_task_btn("语文_S级", "S级 (10')")
        render_task_btn("语文_听写", "听写 (10')")
        render_task_btn("语文_阅读", "阅读 (30')")
        render_task_btn("语文_订正", "订正 (10')")

      with col_c2:
        st.markdown(
            f"**🔢 数学 (75')** —— 已完成 {math_done}/{len(math_keys)}"
        )
        render_task_btn("数学_计算", "计算 (15')")
        render_task_btn("数学_一课一练", "一课一练 (30')")
        render_task_btn("数学_错题跟进", "错题跟进 (20')")
        render_task_btn("数学_订正", "订正 (10')")

      with col_c3:
        st.markdown(
            f"**🔤 英语 (105')** —— 已完成 {eng_done}/{len(eng_keys)}"
        )
        render_task_btn("英语_RAZ读", "RAZ读 / 读力 (40')")
        render_task_btn("英语_听力内区", "RAZ/内区 (30')")
        render_task_btn("英语_听写", "听写 (10')")
        render_task_btn("英语_错题跟进", "错题跟进 (15')")
        render_task_btn("英语_订正", "订正 (10')")


# ==================== 2. 📌 每周统筹 (Week) 看板 ====================
with tab_week:
  st.subheader("📌 每周统筹 (Week) 学习任务总览")
  st.markdown("针对本周的大语文、数学卷子/奥数拔高、英语单词与专项进行追踪。")

  week_id = st.text_input(
      "输入当前周标识（例如：2026-W14 或 第11周）", value="2026-W1"
  )

  if week_id not in st.session_state.weekly_tracking:
    st.session_state.weekly_tracking[week_id] = {
        "周_语文大语文": False,
        "周_数学卷子奥数": False,
        "周_英语专项单词": False,
    }

  w_data = st.session_state.weekly_tracking[week_id]
  w_total = len(w_data)
  w_completed = sum(1 for v in w_data.values() if v)
  w_percent = int((w_completed / w_total) * 100)

  st.metric(
      label=f"🌟 {week_id} 每周统筹总体完成进度",
      value=f"{w_percent}%",
      delta=f"已完成 {w_completed} / {w_total} 项大任务",
  )
  st.progress(w_percent / 100)
  st.divider()

  col_w1, col_w2, col_w3 = st.columns(3)


  def render_week_button(task_key, label_text):
    is_done = w_data[task_key]
    button_label = f"✅ {label_text}" if is_done else f"⬜ {label_text}"
    if st.button(
        button_label, key=f"btn_{week_id}_{task_key}", use_container_width=True
    ):
      w_data[task_key] = not is_done
      st.rerun()


  with col_w1:
    with st.container(border=True):
      st.markdown("### 📖 语文周统筹 (60')")
      render_week_button("周_语文大语文", "大语文 / 现代文 / 新概念")
  with col_w2:
    with st.container(border=True):
      st.markdown("### 🔢 数学周统筹")
      render_week_button("周_数学卷子奥数", "卷子 / 课外奥数拔高")
  with col_w3:
    with st.container(border=True):
      st.markdown("### 🔤 英语周统筹")
      render_week_button("周_英语专项单词", "英读 / 单词 / 专项训练")


# ==================== 3. 📚 课程打卡视图 ====================
with tab_study:
  st.subheader("📚 课程视频打卡")
  col1, col2 = st.columns([1, 2])
  with col1:
    st.markdown("### 课程目录")
    st.info("当前章节：第301讲·四则运算一")
  with col2:
    st.markdown("### 视频列表与网盘直达")
    for video_name, url in st.session_state.net_links.items():
      is_done = st.session_state.study_progress.get(video_name, False)
      c1, c2, c3 = st.columns([3, 1, 1])
      with c1:
        if is_done:
          st.markdown(f"~~{video_name}~~ ✅")
        else:
          st.markdown(f"**{video_name}**")
      with c2:
        if st.button(
            "🌟 打卡" if not is_done else "取消打卡", key=f"btn_{video_name}"
        ):
          st.session_state.study_progress[video_name] = not is_done
          st.rerun()
      with c3:
        st.markdown(f"[去观看]({url})")


# ==================== 4. ⏱️ 听写智能倒计时小工具（全面大按钮优化 + 15秒语音提醒） ====================
with tab_timer:
  st.subheader("⏱️ 报听写智能大屏计时助手")
  st.markdown(
      "💡 **操作指南**：点击两侧的 **[－] / [＋]** 轻松调整数量与时间，点击“🚀"
      " 开始计时”后大屏倒计时启动。**最后 15 秒会自动红字闪烁并伴有语音提醒！**"
  )
  st.divider()

  # 用网格排版制作大号步进调节器（告别不好按的小输入框）
  c_col1, c_col2, c_col3 = st.columns(3)

  # 1. 听写数量调节
  with c_col1:
    st.markdown("#### 📝 听写数量（个）")
    sub_b1, val_b1, add_b1 = st.columns([1, 2, 1])
    with sub_b1:
      if st.button("➖", key="sub_cnt"):
        if st.session_state.t_count > 1:
          st.session_state.t_count -= 1
          st.rerun()
    with val_b1:
      st.markdown(
          f"<h3 style='text-align: center; margin:0; color:#1E3A8A;'>"
          f"{st.session_state.t_count}</h3>",
          unsafe_allow_html=True,
      )
    with add_b1:
      if st.button("➕", key="add_cnt"):
        st.session_state.t_count += 1
        st.rerun()

  # 2. 每题时长调节
  with c_col2:
    st.markdown("#### ⏳ 每题时长（秒）")
    sub_b2, val_b2, add_b2 = st.columns([1, 2, 1])
    with sub_b2:
      if st.button("➖", key="sub_sec"):
        if st.session_state.t_sec > 2:
          st.session_state.t_sec -= 1
          st.rerun()
    with val_b2:
      st.markdown(
          f"<h3 style='text-align: center; margin:0; color:#1E3A8A;'>"
          f"{st.session_state.t_sec}s</h3>",
          unsafe_allow_html=True,
      )
    with add_b2:
      if st.button("➕", key="add_sec"):
        st.session_state.t_sec += 1
        st.rerun()

  # 3. 缓冲时间调节
  with c_col3:
    st.markdown("#### ➕ 额外缓冲（秒）")
    sub_b3, val_b3, add_b3 = st.columns([1, 2, 1])
    with sub_b3:
      if st.button("➖", key="sub_buf"):
        if st.session_state.t_buf >= 5:
          st.session_state.t_buf -= 5
          st.rerun()
    with val_b3:
      st.markdown(
          f"<h3 style='text-align: center; margin:0; color:#1E3A8A;'>"
          f"{st.session_state.t_buf}s</h3>",
          unsafe_allow_html=True,
      )
    with add_b3:
      if st.button("➕", key="add_buf"):
        st.session_state.t_buf += 5
        st.rerun()

  # 计算总时间
  total_seconds = (
      st.session_state.t_count * st.session_state.t_sec
  ) + st.session_state.t_buf
  minutes = total_seconds // 60
  seconds = total_seconds % 60

  st.write("")
  st.info(
      f"📊 **节奏总览**：{st.session_state.t_count} 个单词 ×"
      f" {st.session_state.t_sec} 秒/个 ＋ 缓冲 {st.session_state.t_buf} 秒"
      f" ＝ 总耗时 **{total_seconds} 秒** （约合 **{minutes} 分 {seconds} 秒**）"
  )
  st.divider()

  # 当前显示时间
  display_seconds = (
      st.session_state.time_left
      if st.session_state.timer_running
      else total_seconds
  )
  disp_mins = display_seconds // 60
  disp_secs = display_seconds % 60

  # 如果剩下小于等于 15 秒，触发样式警告
  timer_class = (
      "timer-display timer-warning"
      if (st.session_state.timer_running and display_seconds <= 15)
      else "timer-display timer-normal"
  )

  timer_placeholder = st.empty()
  timer_placeholder.markdown(
      f'<p class="{timer_class}">⏳ {disp_mins:02d} : {disp_secs:02d}</p>',
      unsafe_allow_html=True,
  )

  # 如果恰好剩下 15 秒，通过前端 Web API 顺便触发语音播报提示
  if st.session_state.timer_running and display_seconds == 15:
    st.markdown(
        """
        <script>
        const utterance = new SpeechSynthesisUtterance("注意，最后十五秒！");
        utterance.lang = "zh-CN";
        window.speechSynthesis.speak(utterance);
        </script>
        """,
        unsafe_allow_html=True,
    )

  b_col1, b_col2, b_col3 = st.columns(3)
  with b_col1:
    start_btn = st.button("🚀 开始计时", type="primary", key="start_t")
  with b_col2:
    pause_btn = st.button("⏸️ 暂停 / 停止", key="pause_t")
  with b_col3:
    reset_btn = st.button("🔄 重置时间", key="reset_t")

  if start_btn:
    st.session_state.timer_running = True
    st.session_state.time_left = total_seconds
    st.rerun()

  if pause_btn:
    st.session_state.timer_running = False
    st.rerun()

  if reset_btn:
    st.session_state.timer_running = False
    st.session_state.time_left = total_seconds
    st.rerun()

  if st.session_state.timer_running:
    if st.session_state.time_left > 0:
      time.sleep(1)
      st.session_state.time_left -= 1
      st.rerun()
    else:
      st.session_state.timer_running = False
      st.balloons()
      # 结束时语音播报
      st.markdown(
          """
            <script>
            const utterance = new SpeechSynthesisUtterance("听写时间到，请收卷！");
            utterance.lang = "zh-CN";
            window.speechSynthesis.speak(utterance);
            </script>
            """,
          unsafe_allow_html=True,
      )
      st.success("🎉 时间到！听写结束，请核对或收卷！")


# ==================== 5. 📝 错题跟进与 AI 智能提取视图 ====================
with tab_wrong:
  st.subheader("📝 语数英错题跟进与本地 AI 智能去噪提取")

  sub_col1, sub_col2 = st.columns([2, 1])
  with sub_col1:
    filter_sub = st.radio(
        "选择查看科目",
        ["全部", "数学 🔢", "语文 📖", "英语 🔤"],
        horizontal=True,
    )
  with sub_col2:
    with st.expander("📸 拍照上传 + 本地 minicpm-v AI 自动去噪提取"):
      new_sub_name = st.selectbox("科目", ["数学", "语文", "英语"], key="new_sub")
      uploaded_file = st.file_uploader(
          "拍照或选择试卷照片（自动去除手写答案）",
          type=["jpg", "jpeg", "png"],
      )

      ollama_host = st.session_state.get(
          "ollama_url", "http://localhost:11434"
      )

      if st.button("✨ 运行本地视觉 AI 智能去噪并提取错题"):
        if uploaded_file is None:
          st.warning("请先上传一张试卷照片！")
        else:
          with st.spinner(
              "🤖 本地 minicpm-v 正在看图识别并剥离手写草稿中..."
          ):
            bytes_data = uploaded_file.getvalue()
            ai_text_result = ai_extract_question_ollama(
                bytes_data, ollama_url=ollama_host
            )

            image = Image.open(BytesIO(bytes_data))
            image.thumbnail((800, 800))
            if image.mode in ("RGBA", "P"):
              image = image.convert("RGB")
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=75)
            base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            img_data = f"data:image/jpeg;base64,{base64_str}"

            sub_code = (
                "math"
                if "数学" in new_sub_name
                else ("chinese" if "语文" in new_sub_name else "english")
            )
            st.session_state.wrong_questions.insert(
                0,
                {
                    "id": f"w_{datetime.now().timestamp()}",
                    "subject": sub_code,
                    "desc": ai_text_result,
                    "img": img_data,
                    "fixed": False,
                    "selected": True,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            st.success("🎉 本地视觉 AI 提取完成！错题已独立加入本子。")
            st.rerun()

  st.divider()

  sub_map = {
      "全部": "all",
      "数学 🔢": "math",
      "语文 📖": "chinese",
      "英语 🔤": "english",
  }
  current_filter = sub_map[filter_sub]

  filtered_questions = [
      q
      for q in st.session_state.wrong_questions
      if current_filter == "all" or q["subject"] == current_filter
  ]

  if not filtered_questions:
    st.info("当前分类下没有错题！")
  else:
    for q in filtered_questions:
      box_col1, box_col2, box_col3 = st.columns([0.5, 6, 1.5])
      with box_col1:
        is_sel = st.checkbox(
            "选中",
            value=q["selected"],
            key=f"sel_{q['id']}",
            label_visibility="collapsed",
        )
        if is_sel != q["selected"]:
          q["selected"] = is_sel
          st.rerun()
      with box_col2:
        sub_badge = (
            "🔢 数学"
            if q["subject"] == "math"
            else ("📖 语文" if q["subject"] == "chinese" else "🔤 英语")
        )
        status_text = "✅ 已订正" if q["fixed"] else "❌ 待攻克"
        st.markdown(f"**[{sub_badge}]** {q['date']} | 状态: **{status_text}**")
        st.markdown(f"**{q['desc']}**")
        if q.get("img"):
          with st.expander("查看原图参考"):
            st.image(q["img"], width=300)
      with box_col3:
        if st.button("切换订正状态", key=f"fix_{q['id']}"):
          q["fixed"] = not q["fixed"]
          st.rerun()
        if st.button("删除", key=f"del_{q['id']}"):
          st.session_state.wrong_questions = [
              item
              for item in st.session_state.wrong_questions
              if item["id"] != q["id"]
          ]
          st.rerun()
      st.divider()


# ==================== 6. 🖨️ 生成无答案抽查试卷视图 ====================
with tab_print:
  st.subheader("🖨️ 错题抽查打印预览（独立分题 + 专属演算空白区）")

  selected_for_print = [
      q for q in st.session_state.wrong_questions if q["selected"]
  ]

  if not selected_for_print:
    st.warning("您还没有勾选任何错题用于组卷！")
  else:
    st.success(
        f"已成功组卷！当前共选入 {len(selected_for_print)} 道纯净独立错题："
    )

    st.markdown("---")
    st.markdown(
        "<h2 style='text-align: center; font-family: SimSun;"
        " font-weight: bold;'>🌟 专属错题抽查过关测试卷 🌟</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; font-size: 16px;'>姓名：__________"
        " &nbsp;&nbsp;&nbsp;&nbsp; 日期：2026年___月___日"
        " &nbsp;&nbsp;&nbsp;&nbsp; 得分：__________</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    for idx, q in enumerate(selected_for_print):
      sub_label = (
          "[数学]"
          if q["subject"] == "math"
          else ("[语文]" if q["subject"] == "chinese" else "[英语]")
      )
      st.markdown(
          f"<div style='margin-bottom: 30px; padding: 15px; border: 1px solid"
          f" #e0e0e0; border-radius: 8px; background-color: #fafafa;'>"
          f"<h4 style='color: #333; margin-bottom: 8px;'>第 {idx + 1}"
          f" 题 &nbsp;<span style='font-size: 14px; color: #666;'>{sub_label}</span></h4>"
          f"<p style='font-size: 16px; line-height: 1.6; color: #111;"
          f" font-weight: 500;'>{q['desc']}</p>"
          f"<div style='margin-top: 20px; border-top: 2px dashed #b0b0b0;"
          f" height: 180px; padding-top: 8px; color: #888; text-align: right;"
          f" font-size: 13px;'>（请在此处独立演算与书写过程）</div>"
          f"</div>",
          unsafe_allow_html=True,
      )


# ==================== 7. ⚙️ 系统设置与本地配置 ====================
with tab_settings:
  st.subheader("⚙️ 本地 Ollama 配置与网盘直达")

  ollama_url_input = st.text_input(
      "Ollama 本地服务地址",
      value=st.session_state.get("ollama_url", "http://localhost:11434"),
      help="如果在本机运行 Streamlit，保持默认 http://localhost:11434 即可",
  )
  if st.button("保存地址配置"):
    st.session_state.ollama_url = ollama_url_input.strip()
    st.success("Ollama 地址配置已更新！")

  st.divider()
  st.markdown("### 课程网盘直达链接配置")
  for v_name in list(st.session_state.net_links.keys()):
    new_url = st.text_input(
        f"视频：{v_name}",
        value=st.session_state.net_links[v_name],
        key=f"link_{v_name}",
    )
    st.session_state.net_links[v_name] = new_url