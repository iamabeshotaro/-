import streamlit as st
import pandas as pd
import re
import json
import hashlib
import os
import time

# ==========================================
# 1. ページ設定とスマホ向けCSS
# ==========================================
st.set_page_config(page_title="時間割概論", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    div.stButton > button {
        border-radius: 4px !important;
        font-weight: bold !important;
        padding: 4px 0px !important;
        font-size: 11px !important;
        min-height: 32px !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 2px !important;
        gap: 2px !important;
        background-color: var(--secondary-background-color);
    }
    .tt-header {
        text-align: center;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .auth-btn button {
        font-size: 14px !important;
        padding: 8px !important;
    }
    .confirmed-cell {
        background-color: #004080;
        color: white;
        border-radius: 4px;
        padding: 6px;
        font-size: 10px;
        text-align: center;
        font-weight: bold;
        height: 100%;
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .empty-cell {
        background-color: var(--secondary-background-color);
        border-radius: 4px;
        min-height: 40px;
    }
    @media (prefers-color-scheme: dark) {
        .confirmed-cell {
            background-color: #4a90e2;
        }
    }

    /* =========================================
       ★ スマホの縦並び崩れを防止する魔法のコード
       ========================================= */
    @media (max-width: 640px) {
        /* カラムの折り返しを禁止し、絶対に横並びにする */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 2px !important; /* スマホでは隙間を極力減らす */
        }
        /* 各カラムの幅を均等に圧縮する */
        div[data-testid="column"] {
            width: auto !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
        }
        /* 6列あるブロック（時間割グリッド）の1列目（時限の数字）だけ少し細くする */
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(6)) > div:first-child {
            flex: 0.6 1 0% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. データベース（JSON）管理
# ==========================================
USER_FILE = 'users_data.json'

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
        for u_data in users.values():
            if "likes" not in u_data:
                u_data["likes"] = []
        return users

def save_users(users):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_and_rerun():
    if st.session_state.get('current_user'):
        users = load_users()
        u_name = st.session_state.current_user
        users[u_name]['registered'] = st.session_state.registered
        users[u_name]['bookmarks'] = st.session_state.bookmarks
        save_users(users)
    st.rerun()

# ==========================================
# 3. データの準備
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('syllabus_master.csv').fillna("不明")
    except FileNotFoundError:
        st.error("syllabus_master.csv が見つかりません。")
        st.stop()
        
    def get_priority(code):
        if len(str(code)) >= 2:
            attr = str(code)[1]
            priorities = {'M': 1, 'P': 2, 'O': 3, 'S': 4, 'L': 5, 'Z': 6}
            return priorities.get(attr, 99)
        return 99
        
    df['優先度'] = df['授業コード'].apply(get_priority)
    return df

df = load_data()

# ==========================================
# 4. 状態管理（Session State）
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'registered' not in st.session_state:
    st.session_state.registered = {"春学期": {}, "秋学期": {}}
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = []
if 'active_slot' not in st.session_state:
    st.session_state.active_slot = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "tt"

# ==========================================
# 5. アカウント画面
# ==========================================
if not st.session_state.logged_in:
    st.title("📚 時間割概論")
    st.write("アカウントにログインまたは新規登録してください。")
    
    auth_mode = st.radio("メニュー", ["ログイン", "新規登録"], horizontal=True)
    user_input = st.text_input("ユーザーネーム (公開されます)")
    pass_input = st.text_input("パスワード", type="password")
    
    st.markdown('<div class="auth-btn">', unsafe_allow_html=True)
    if auth_mode == "新規登録":
        if st.button("登録してはじめる", type="primary", use_container_width=True):
            if not user_input or not pass_input:
                st.error("入力してください")
            else:
                users = load_users()
                if user_input in users:
                    st.error("既に使用されています")
                else:
                    users[user_input] = {
                        "password": hash_pass(pass_input),
                        "registered": {"春学期": {}, "秋学期": {}},
                        "bookmarks": [],
                        "likes": []
                    }
                    save_users(users)
                    st.success("✅ 登録完了！「ログイン」から入ってください。")
    else:
        if st.button("ログイン", type="primary", use_container_width=True):
            users = load_users()
            if user_input in users and users[user_input]["password"] == hash_pass(pass_input):
                st.session_state.logged_in = True
                st.session_state.current_user = user_input
                st.session_state.registered = users[user_input]["registered"]
                st.session_state.bookmarks = users[user_input]["bookmarks"]
                st.rerun()
            else:
                st.error("⚠️ 間違っています")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 6. サイドバー
# ==========================================
with st.sidebar:
    st.subheader("👤 アカウント")
    st.write(f"ユーザー: **{st.session_state.current_user}**")
    if st.button("🚪 ログアウト", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

# ==========================================
# 7. 共通関数
# ==========================================
def get_slot_pairs(course):
    d_list = str(course['曜日']).split()
    p_list = str(course['時限']).split()
    return list(zip(d_list, p_list))

def toggle_register(semester, course):
    if isinstance(course, pd.Series): 
        course = course.to_dict()
        
    cid = course['授業コード']
    if cid not in [b['授業コード'] for b in st.session_state.bookmarks]:
        st.session_state.bookmarks.append(course)
        
    reg = st.session_state.registered[semester]
    if cid in reg:
        del reg[cid]
        return
        
    target_slots = get_slot_pairs(course)
    conflicts = []
    for r_cid, r_course in reg.items():
        if any(s in get_slot_pairs(r_course) for s in target_slots): 
            conflicts.append(r_cid)
            
    for c in conflicts:
        del reg[c]
        st.toast("⚠️ 重複授業を仮登録に戻しました")
        
    reg[cid] = course

def get_total_credits(semester_data):
    total = 0
    for c in semester_data.values():
        match = re.search(r'(\d+\.?\d*)', str(c.get('単位数', '0')))
        if match: 
            total += float(match.group(1))
    return total

def display_links(course):
    l1, l2 = st.columns(2)
    with l1:
        if course.get('詳細URL') and course['詳細URL'] != "不明": 
            st.link_button("📄 シラバス", course['詳細URL'], use_container_width=True)
    with l2:
        if course.get('みんキャン検索LINK') and course['みんキャン検索LINK'] != "不明": 
            st.link_button("🗣️ みんキャン", course['みんキャン検索LINK'], use_container_width=True)

def draw_confirmed_timetable(registered_data, semester):
    days = ["月", "火", "水", "木", "金"]
    cols = st.columns([0.6, 1, 1, 1, 1, 1])
    for i, d in enumerate([""] + days): 
        cols[i].markdown(f"<div class='tt-header'>{d}</div>", unsafe_allow_html=True)
        
    for p in range(1, 7):
        cols = st.columns([0.6, 1, 1, 1, 1, 1])
        cols[0].markdown(f"<div style='text-align:center; margin-top:15px; font-weight:bold;'>{p}</div>", unsafe_allow_html=True)
        for i, d in enumerate(days):
            with cols[i+1]:
                course = next((c for c in registered_data.get(semester, {}).values() if (d, str(p)) in get_slot_pairs(c)), None)
                if course:
                    short_name = course['授業名'][:6] + ".." if len(course['授業名']) > 6 else course['授業名']
                    st.markdown(f"<div class='confirmed-cell'>{short_name}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='empty-cell'></div>", unsafe_allow_html=True)

# ==========================================
# 8. ナビゲーション
# ==========================================
nav1, nav2, nav3, nav4 = st.columns(4)
if nav1.button("🗓️", type="primary" if st.session_state.current_page == "tt" else "secondary", use_container_width=True):
    st.session_state.current_page = "tt"
    st.rerun()
if nav2.button("🔍", type="primary" if st.session_state.current_page == "search" else "secondary", use_container_width=True):
    st.session_state.current_page = "search"
    st.rerun()
if nav3.button("⭐", type="primary" if st.session_state.current_page == "bk" else "secondary", use_container_width=True):
    st.session_state.current_page = "bk"
    st.rerun()
if nav4.button("🌍", type="primary" if st.session_state.current_page == "public" else "secondary", use_container_width=True):
    st.session_state.current_page = "public"
    st.rerun()
st.divider()

# ==========================================
# 9. メインUI
# ==========================================

# ------------------------------------------
# 画面1: マイ時間割
# ------------------------------------------
if st.session_state.current_page == "tt":
    col_mode1, col_mode2 = st.columns(2)
    view_mode = st.radio("モード切替", ["🛠️ 編集", "👀 確定表示"], horizontal=True, label_visibility="collapsed")
    
    if 'current_semester' not in st.session_state: 
        st.session_state.current_semester = "春学期"
        
    col_h1, col_h2 = st.columns([3, 2])
    with col_h1:
        semester = st.selectbox("学期", ["春学期", "秋学期"], index=0 if st.session_state.current_semester=="春学期" else 1, label_visibility="collapsed")
        st.session_state.current_semester = semester
    with col_h2: 
        st.write(f"✅ **{get_total_credits(st.session_state.registered[semester]):.1f} 単位**")

    if view_mode == "👀 確定表示":
        draw_confirmed_timetable(st.session_state.registered, semester)
    else:
        if st.session_state.active_slot:
            d = st.session_state.active_slot['day']
            p = st.session_state.active_slot['period']
            col_title, col_close = st.columns([4, 1])
            col_title.subheader(f"⚙️ {d}曜{p}限")
            
            if col_close.button("✖ 戻る", type="primary"):
                st.session_state.active_slot = None
                st.rerun()

            st.write("🔍 **この時間の授業一覧から追加**")
            mask = []
            for _, row in df.iterrows():
                if semester.replace("学期","") in row['学期'] and (d, str(p)) in get_slot_pairs(row):
                    mask.append(True)
                else:
                    mask.append(False)
                    
            slot_courses = df[mask].sort_values('優先度')
            
            if len(slot_courses) == 0: 
                st.info("この時間に開講されているシラバス掲載の授業はありません。")
                
            for _, row in slot_courses.head(30).iterrows():
                with st.container(border=True):
                    st.write(f"**{row['授業コード']} | {row['授業名']}**")
                    st.caption(f"担当: {row['担当教員']} | 単位: {row['単位数']}")
                    b1, b2 = st.columns(2)
                    is_reg = row['授業コード'] in st.session_state.registered[semester]
                    
                    if b1.button("解除" if is_reg else "✅ 本登録", key=f"reg_{row['授業コード']}"):
                        toggle_register(semester, row.to_dict())
                        st.session_state.active_slot = None 
                        save_and_rerun()
                        
                    is_bk = row['授業コード'] in [bk['授業コード'] for bk in st.session_state.bookmarks]
                    
                    if b2.button("外す" if is_bk else "⭐ 候補へ", key=f"bk_{row['授業コード']}"):
                        if not is_bk: 
                            st.session_state.bookmarks.append(row.to_dict())
                        else: 
                            st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b['授業コード'] != row['授業コード']]
                        save_and_rerun()
                        
                    display_links(row.to_dict())

            st.divider()
            st.write("✏️ **リストにない授業を手動で追加**")
            with st.expander("＋ オリジナルの授業を作成する"):
                with st.form(f"custom_course_{d}_{p}"):
                    c_name = st.text_input("授業名（必須）", placeholder="例: 他学部履修科目")
                    c_teacher = st.text_input("担当教員", placeholder="例: 山田 太郎")
                    c_credits = st.number_input("単位数", min_value=0.0, max_value=10.0, value=2.0, step=1.0)
                    
                    if st.form_submit_button("✅ このコマに登録"):
                        if not c_name.strip():
                            st.error("授業名を入力してください")
                        else:
                            custom_id = f"MY_{int(time.time())}"
                            custom_course = {
                                "授業コード": custom_id,
                                "授業名": c_name,
                                "担当教員": c_teacher if c_teacher else "不明",
                                "単位数": f"{c_credits}単位",
                                "曜日": d,
                                "時限": str(p),
                                "学期": semester,
                                "詳細URL": "不明",
                                "みんキャン検索LINK": "不明",
                                "優先度": 99
                            }
                            toggle_register(semester, custom_course)
                            st.session_state.active_slot = None
                            save_and_rerun()

        else:
            days = ["月", "火", "水", "木", "金"]
            cols = st.columns([0.6, 1, 1, 1, 1, 1])
            for i, d in enumerate([""] + days): 
                cols[i].markdown(f"<div class='tt-header'>{d}</div>", unsafe_allow_html=True)
                
            for p in range(1, 7):
                cols = st.columns([0.6, 1, 1, 1, 1, 1])
                cols[0].markdown(f"<div style='text-align:center; margin-top:15px; font-weight:bold;'>{p}</div>", unsafe_allow_html=True)
                for i, d in enumerate(days):
                    with cols[i+1]:
                        with st.container(border=True):
                            bks_in_cell = [b for b in st.session_state.bookmarks if semester.replace("学期","") in b['学期'] and (d, str(p)) in get_slot_pairs(b)]
                            
                            if bks_in_cell:
                                for b in bks_in_cell:
                                    cid = b['授業コード']
                                    is_reg = cid in st.session_state.registered[semester]
                                    btn_label = f"✅{cid}" if is_reg else f"⭐{cid}"
                                    
                                    if cid.startswith("MY_"):
                                        short_name = b['授業名'][:3]
                                        btn_label = f"✅{short_name}" if is_reg else f"⭐{short_name}"
                                        
                                    if st.button(btn_label, key=f"tt_{d}_{p}_{cid}", use_container_width=True, type="primary" if is_reg else "secondary"):
                                        toggle_register(semester, b)
                                        save_and_rerun()
                                        
                                if st.button("＋", key=f"add_{d}_{p}", use_container_width=True):
                                    st.session_state.active_slot = {"day": d, "period": str(p)}
                                    st.rerun()
                            else:
                                if st.button("＋", key=f"empty_{d}_{p}", use_container_width=True):
                                    st.session_state.active_slot = {"day": d, "period": str(p)}
                                    st.rerun()

# ------------------------------------------
# 画面2: 検索画面
# ------------------------------------------
elif st.session_state.current_page == "search":
    st.subheader("🔍 授業検索")
    query = st.text_input("キーワード (授業名・教員・コード)")
    s_sem = st.selectbox("学期", ["春学期", "秋学期", "すべて"])
    col_d, col_p = st.columns(2)
    s_day = col_d.selectbox("曜日", ["すべて", "月", "火", "水", "木", "金"])
    s_per = col_p.selectbox("時限", ["すべて", "1", "2", "3", "4", "5", "6"])

    res = df.copy()
    if s_sem != "すべて": 
        res = res[res['学期'].str.contains(s_sem)]
    if s_day != "すべて": 
        res = res[res['曜日'].str.contains(s_day)]
    if s_per != "すべて": 
        res = res[res['時限'].astype(str).str.contains(s_per)]
    if query:
        res = res[res['授業名'].str.contains(query, case=False) | res['担当教員'].str.contains(query, case=False) | res['授業コード'].str.contains(query, case=False)]

    res = res.sort_values('優先度')
    st.write(f"結果: **{len(res)}件** (50件まで)")
    
    for _, row in res.head(50).iterrows():
        with st.container(border=True):
            t_str = " ".join([f"{d}{p}限" for d, p in get_slot_pairs(row)])
            st.write(f"**{row['授業コード']} | {row['授業名']}**")
            st.caption(f"{row['学期']} | {t_str} | {row['担当教員']} | {row['単位数']}")
            
            c1, c2 = st.columns(2)
            active_sem = "春学期" if "春" in row['学期'] else "秋学期"
            is_reg = row['授業コード'] in st.session_state.registered[active_sem]
            
            if c1.button("解除" if is_reg else "✅ 本登録", key=f"src_reg_{row['授業コード']}"):
                toggle_register(active_sem, row.to_dict())
                save_and_rerun()
                
            is_bk = row['授業コード'] in [b['授業コード'] for b in st.session_state.bookmarks]
            
            if c2.button("外す" if is_bk else "⭐ 候補へ", key=f"src_bk_{row['授業コード']}"):
                if not is_bk: 
                    st.session_state.bookmarks.append(row.to_dict())
                else: 
                    st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b['授業コード'] != row['授業コード']]
                save_and_rerun()
                
            display_links(row.to_dict())

# ------------------------------------------
# 画面3: 候補(ブックマーク)画面
# ------------------------------------------
elif st.session_state.current_page == "bk":
    st.subheader("⭐ 保存した授業 (候補)")
    if not st.session_state.bookmarks: 
        st.info("検索画面から⭐を押して保存してください。")
        
    for b in st.session_state.bookmarks:
        with st.container(border=True):
            t_str = " ".join([f"{d}{p}限" for d, p in get_slot_pairs(b)])
            display_code = "手動入力" if b['授業コード'].startswith("MY_") else b['授業コード']
            st.write(f"**{display_code} | {b['授業名']}**")
            st.caption(f"{b['学期']} | {t_str} | {b['担当教員']}")
            
            c1, c2 = st.columns(2)
            active_sem = "春学期" if "春" in b['学期'] else "秋学期"
            is_reg = b['授業コード'] in st.session_state.registered[active_sem]
            
            if c1.button("解除" if is_reg else "✅ 本登録", key=f"bk_reg_{b['授業コード']}"):
                toggle_register(active_sem, b)
                save_and_rerun()
                
            if c2.button("🗑️ 削除", key=f"bk_del_{b['授業コード']}"):
                st.session_state.bookmarks = [x for x in st.session_state.bookmarks if x['授業コード'] != b['授業コード']]
                if is_reg: 
                    del st.session_state.registered[active_sem][b['授業コード']]
                save_and_rerun()
                
            if not b['授業コード'].startswith("MY_"):
                display_links(b)

# ------------------------------------------
# 画面4: みんなの時間割 (公開タイムライン)
# ------------------------------------------
elif st.session_state.current_page == "public":
    st.subheader("🌍 みんなの時間割")
    st.write("他のユーザーが組んだ時間割を見て、参考にしましょう。")
    
    users = load_users()
    my_id = st.session_state.current_user
    public_users = [u for u in users.keys() if u != my_id]
    
    if not public_users:
        st.info("まだ他のユーザーがいません。")
    else:
        public_users.sort(key=lambda u: len(users[u].get('likes', [])), reverse=True)
        selected_user = st.selectbox("時間割を見るユーザーを選択（人気順）", ["選択してください..."] + public_users)
        
        if selected_user != "選択してください...":
            target_data = users[selected_user]
            likes_list = target_data.get('likes', [])
            
            c_head1, c_head2 = st.columns([3, 2])
            with c_head1:
                p_sem = st.selectbox("表示する学期", ["春学期", "秋学期"])
            with c_head2:
                has_liked = my_id in likes_list
                like_btn_text = f"❤️ {len(likes_list)}" if has_liked else f"🤍 いいね ({len(likes_list)})"
                
                if st.button(like_btn_text, use_container_width=True):
                    if has_liked:
                        target_data['likes'].remove(my_id)
                    else:
                        target_data['likes'].append(my_id)
                    save_users(users)
                    st.rerun()

            st.write(f"👤 **{selected_user}** さんの {p_sem}（計 {get_total_credits(target_data['registered'].get(p_sem, {})):.1f} 単位）")
            draw_confirmed_timetable(target_data['registered'], p_sem)
