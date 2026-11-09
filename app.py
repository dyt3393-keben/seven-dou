import streamlit as st
from datetime import datetime

# 页面基础配置
st.set_page_config(
    page_title="小星星学习与错题乐园",
    page_icon="🌟",
    layout="wide"
)

# 初始化 Session State 数据存储
if "study_progress" not in st.session_state:
    st.session_state.study_progress = {}

if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = [
        {
            "id": "w1",
            "subject": "math",
            "desc": "【环形公路运费最优化】A仓库存库40吨，B库5吨...求完成运输计划最少需要多少元运费？",
            "fixed": False,
            "selected": True,
            "date": "2026-03-30"
        },
        {
            "id": "w2",
            "subject": "chinese",
            "desc": "【错别字订正】把“辨别”的“辨”字误写成了“辩论”的“辩”。",
            "fixed": False,
            "selected": True,
            "date": "2026-03-30"
        },
        {
            "id": "w3",
            "subject": "english",
            "desc": "【语法错题】一般现在时第三人称单数：He like playing football 错写。",
            "fixed": False,
            "selected": False,
            "date": "2026-03-30"
        }
    ]

if "net_links" not in st.session_state:
    st.session_state.net_links = {
        "第301讲.四则运算一-[1.基础计算].mp4": "https://pan.quark.cn/",
        "第301讲.四则运算一-[2.添去括号凑整].mp4": "https://pan.quark.cn/"
    }

# 顶部主标题
st.title("🌟 小星星学习与错题乐园")
st.caption("iPad 专属：网盘看课打卡 + 语数英错题智能组卷打印系统")

# 导航标签页
tab_study, tab_wrong, tab_print, tab_settings = st.tabs([
    "📚 课程打卡", 
    "📝 错题跟进与组卷", 
    "🖨️ 生成无答案抽查试卷", 
    "⚙️ 家长后台设置"
])

# ==================== 1. 课程打卡视图 ====================
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
                # 修复此处变量名：is_done 对应逻辑
                if st.button("🌟 打卡" if not is_done else "取消打卡", key=f"btn_{video_name}"):
                    st.session_state.study_progress[video_name] = not is_done
                    st.rerun()
            with c3:
                st.markdown(f"[去观看]({url})")

# ==================== 2. 错题跟进与组卷视图 ====================
with tab_wrong:
    st.subheader("📝 语数英错题跟进与组卷")
    
    sub_col1, sub_col2 = st.columns([2, 1])
    with sub_col1:
        filter_sub = st.radio(
            "选择查看科目", 
            ["全部", "数学 🔢", "语文 📖", "英语 🔤"], 
            horizontal=True
        )
    with sub_col2:
        with st.expander("➕ 快速录入新错题"):
            new_sub_name = st.selectbox("科目", ["数学", "语文", "英语"], key="new_sub")
            new_desc = st.text_area("错题文字描述/核心知识点", placeholder="输入题目考点或清理手写痕迹后的文字...")
            if st.button("保存并加入错题本"):
                if new_desc:
                    sub_code = "math" if "数学" in new_sub_name else ("chinese" if "语文" in new_sub_name else "english")
                    st.session_state.wrong_questions.insert(0, {
                        "id": f"w_{datetime.now().timestamp()}",
                        "subject": sub_code,
                        "desc": new_desc,
                        "fixed": False,
                        "selected": True,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success("错题保存成功！")
                    st.rerun()
                else:
                    st.warning("请填写错题描述！")

    st.divider()

    sub_map = {"全部": "all", "数学 🔢": "math", "语文 📖": "chinese", "英语 🔤": "english"}
    current_filter = sub_map[filter_sub]
    
    filtered_questions = [
        q for q in st.session_state.wrong_questions 
        if current_filter == "all" or q["subject"] == current_filter
    ]

    if not filtered_questions:
        st.info("当前分类下没有错题，太棒了！🎉")
    else:
        st.markdown(f"当前共显示 {len(filtered_questions)} 道错题（已勾选用于组卷的题目可在专用标签页生成试卷）：")
        
        for q in filtered_questions:
            box_col1, box_col2, box_col3 = st.columns([0.5, 6, 1.5])
            with box_col1:
                is_sel = st.checkbox("选中", value=q["selected"], key=f"sel_{q['id']}", label_visibility="collapsed")
                if is_sel != q["selected"]:
                    q["selected"] = is_sel
                    st.rerun()
            with box_col2:
                sub_badge = "🔢 数学" if q["subject"] == "math" else ("📖 语文" if q["subject"] == "chinese" else "🔤 英语")
                status_text = "✅ 已订正" if q["fixed"] else "❌ 待攻克"
                st.markdown(f"**[{sub_badge}]** {q['date']} | 状态: **{status_text}**")
                if q["fixed"]:
                    st.markdown(f"~~{q['desc']}~~")
                else:
                    st.markdown(f"**{q['desc']}**")
            with box_col3:
                if st.button("切换订正状态", key=f"fix_{q['id']}"):
                    q["fixed"] = not q["fixed"]
                    st.rerun()
                if st.button("删除", key=f"del_{q['id']}"):
                    st.session_state.wrong_questions = [item for item in st.session_state.wrong_questions if item["id"] != q["id"]]
                    st.rerun()
            st.divider()

# ==================== 3. 生成无答案抽查试卷视图 ====================
with tab_print:
    st.subheader("🖨️ 错题抽查打印预览（已自动隐藏所有答案与解析）")
    
    selected_for_print = [q for q in st.session_state.wrong_questions if q["selected"]]
    
    if not selected_for_print:
        st.warning("您还没有勾选任何错题！请先到【📝 错题跟进与组卷】标签页中勾选需要抽查打印的题目。")
    else:
        st.success(f"已成功组卷！当前共选入 {len(selected_for_print)} 道错题，排版如下：")
        
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>🌟 专属错题抽查过关测试卷 🌟</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>姓名：__________ &nbsp;&nbsp;&nbsp;&nbsp; 日期：2026年___月___日 &nbsp;&nbsp;&nbsp;&nbsp; 得分：__________</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        for idx, q in enumerate(selected_for_print):
            sub_label = "[数学]" if q["subject"] == "math" else ("[语文]" if q["subject"] == "chinese" else "[英语]")
            st.markdown(f"### **第 {idx + 1} 题** {sub_label}")
            st.markdown(f"> {q['desc']}")
            st.markdown("<br><div style='border-bottom: 1px dashed #ccc; height: 120px; color: #bbb; text-align: right;'>（答题与演算区域）</div><br>", unsafe_allow_html=True)
            
        st.info("💡 提示：在电脑或 iPad 浏览器中，直接点击浏览器的打印功能（Ctrl+P 或 Cmd+P），即可输出整洁的 A4 打印卷！")

# ==================== 4. 家长后台设置 ====================
with tab_settings:
    st.subheader("⚙️ 网盘课程链接配置")
    st.write("在这里可以随时更新孩子网盘课程的直达网址：")
    
    for v_name in list(st.session_state.net_links.keys()):
        new_url = st.text_input(f"视频：{v_name}", value=st.session_state.net_links[v_name], key=f"link_{v_name}")
        st.session_state.net_links[v_name] = new_url