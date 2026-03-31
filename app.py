import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
import json
import hashlib
import os
import time
import html
import extra_streamlit_components as stx

# ==========================================
# 1. ページ設定とスマホ向け究極CSS (完全分離版)
# ==========================================
st.set_page_config(page_title="C-krat", layout="centered", initial_sidebar_state="collapsed")

components.html(
    """
    <script>
    const meta = window.parent.document.querySelector('meta[name="viewport"]');
    if (meta) {
        meta.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
    }
    </script>
    """,
    height=0
)

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    @media (prefers-color-scheme: dark) { .stApp { background-color: #0e1117; } }

    /* ヘッダー非表示 */
    header { visibility: hidden; height: 0px !important; }
    
    @media screen and (max-width: 768px) {
        /* ドロップダウンが上に開くのを防ぐため、画面下部に広大な余白を確保 */
        .block-container { 
            padding-top: 0.5rem !important; 
            padding-bottom: 250px !important; 
            padding-left: 0.2rem !important; 
            padding-right: 0.2rem !important; 
            max-width: 100% !important; 
        }
    }

    /* 縦の隙間を完全に消す */
    div[data-testid="stVerticalBlockBorderWrapper"] > div { gap: 0px !important; }

    @media screen and (max-width: 768px) {
        /* スマホ幅では横並び要素を絶対に縦に積まない */
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 2px !important;
            margin-bottom: 4px !important;
        }
    }

    /* =========================================
       ★ 5列：ナビゲーションバー（メニュー）の美しいデザイン
       ========================================= */
    /* 5列のブロックを特定 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5),
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) ~ div {
        width: 20% !important; 
        min-width: 20% !important;
        padding: 0 2px !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) div.stButton {
        width: 100% !important; margin: 0 !important; padding: 0 !important;
    }

    /* ナビゲーションのボタン本体（アプリのタブバー風） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) button,
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) ~ div button {
        width: 100% !important;
        height: 48px !important;
        border: none !important;
        border-radius: 12px !important; /* 丸くて可愛い形に */
        background-color: #ffffff !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important; /* ふんわり浮かせる */
        padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) button p,
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) ~ div button p {
        font-size: 20px !important; /* 絵文字を大きく */
        margin: 0 !important;
    }

    /* 選択中（アクティブ）のタブ */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) button[kind="primary"],
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) ~ div button[kind="primary"] {
        background-color: #e0f2fe !important; /* 薄い水色 */
        box-shadow: inset 0 0 0 1.5px #56CCF2 !important; /* 枠線を光らせる */
    }

    /* =========================================
       ★ 6列：時間割グリッドの完全固定＆鮮やかデザイン
       ========================================= */
    /* 1列目（時限：10%） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) {
        width: 10% !important; flex: 0 0 10% !important; min-width: 10% !important;
        padding: 0 !important; display: flex; align-items: center; justify-content: center;
    }
    /* 2〜6列目（月〜金：18%） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div {
        width: 18% !important; flex: 0 0 18% !important; min-width: 18% !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div div.stButton {
        width: 100% !important; height: 100% !important; margin: 0 !important; padding: 0 !important;
    }

    /* 時間割セル（ボタン）の本体 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button {
        width: 100% !important;
        height: 75px !important; /* 高さを完全固定 */
        border: none !important;
        border-radius: 8px !important; /* 角丸 */
        padding: 2px !important; 
        margin: 0 !important;
        box-shadow: none !important;
    }

    /* セル内のテキスト（1行5文字） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button p {
        font-size: 10px !important; 
        font-weight: 700 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.5px !important;
        margin: 0 !important;
        white-space: normal !important;
        word-break: break-all !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 4 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
    }

    /* 登録済みのコマ（鮮やか青紫グラデーション） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button[kind="primary"] {
        background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important; 
    }

    /* 空きコマ（点線枠） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px dashed #d0d0d0 !important;
        color: #d0d0d0 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button[kind="secondary"] p {
        font-size: 14px !important; 
    }

    /* タップアニメーション */
    div[data-testid="stHorizontalBlock"] button:active { transform: scale(0.95) !important; }

    /* ダークモード対応 */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) button, div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) ~ div button { background-color: #222 !important; box-shadow: none !important; }
        div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) button[kind="primary"], div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(5) ~ div button[kind="primary"] { background-color: #333 !important; box-shadow: inset 0 0 0 1.5px #56CCF2 !important; }
        div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button[kind="primary"] { background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%) !important; }
        div[data-testid="stHorizontalBlock"] > div:nth-child(1):nth-last-child(6) ~ div button[kind="secondary"] { border-color: #555 !important; color: #555 !important; }
    }

    /* 時限ラベルの文字デザイン */
    .tt-header { text-align: center; font-size: 11px; font-weight: bold; color: #666; padding-bottom: 2px; border-bottom: 2px solid #eee; margin-bottom: 2px; }
    .tt-time { text-align: center; font-size: 11px; font-weight: bold; color: #aaa; margin-top: 20px; }

    /* その他の汎用ボタン */
    div.stButton > button:not(div[data-testid="stHorizontalBlock"] button) {
        border-radius: 10px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        font-weight: 600 !important; padding: 6px 4px !important; min-height: 44px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 状態管理（Session State）初期化
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'registered' not in st.session_state: st.session_state.registered = {"春学期": {}, "秋学期": {}}
if 'bookmarks' not in st.session_state: st.session_state.bookmarks = []
if 'active_slot' not in st.session_state: st.session_state.active_slot = None
if 'current_page' not in st.session_state: st.session_state.current_page = "tt"

if 'pending_logout' not in st.session_state: st.session_state.pending_logout = False
if 'pending_login_set' not in st.session_state: st.session_state.pending_login_set = None
if 'pending_rename_set' not in st.session_state: st.session_state.pending_rename_set = None
if 'manual_logout' not in st.session_state: st.session_state.manual_logout = False

# ==========================================
# 3. データベース（JSON）とクッキー管理
# ==========================================
USER_FILE = 'users_data.json'

def load_users():
    if not os.path.exists(USER_FILE): return {}
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
        for u_data in users.values():
            if "likes" not in u_data: u_data["likes"] = []
            if "department" not in u_data: u_data["department"] = "未設定"
            if "gender" not in u_data: u_data["gender"] = "未設定"
        return users

def save_users(users):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_and_rerun():
    if st.session_state.current_user:
        users = load_users()
        u_name = st.session_state.current_user
        if u_name in users:
            users[u_name]['registered'] = st.session_state.registered
            users[u_name]['bookmarks'] = st.session_state.bookmarks
            save_users(users)
    st.rerun()

cookie_manager = stx.CookieManager()

if st.session_state.pending_logout:
    cookie_manager.delete("current_user", key="logout_del")
    st.session_state.pending_logout = False
    st.session_state.manual_logout = True

if st.session_state.pending_login_set:
    cookie_manager.set("current_user", st.session_state.pending_login_set, max_age=2592000, key="login_set")
    st.session_state.pending_login_set = None

if st.session_state.pending_rename_set:
    cookie_manager.set("current_user", st.session_state.pending_rename_set, max_age=2592000, key="rename_set")
    st.session_state.pending_rename_set = None

# ==========================================
# 4. データの準備
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
# 5. アカウント画面
# ==========================================
if not st.session_state.logged_in:
    cached_user = cookie_manager.get(cookie="current_user")
    if cached_user and not st.session_state.manual_logout:
        users = load_users()
        if cached_user in users:
            st.session_state.logged_in = True
            st.session_state.current_user = cached_user
            st.session_state.registered = users[cached_user]["registered"]
            st.session_state.bookmarks = users[cached_user]["bookmarks"]
            st.rerun()

    st.title("🥐 C-krat")
    st.write("中央大学 商学部向け 時間割＆シラバス検索ツール")
    
    auth_mode = st.radio("メニュー", ["ログイン", "新規登録"], horizontal=True)
    user_input = st.text_input("ユーザーネーム (公開されます)")
    pass_input = st.text_input("パスワード", type="password")
    
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
                        "likes": [],
                        "department": "未設定",
                        "gender": "未設定"
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
                st.session_state.manual_logout = False 
                st.session_state.pending_login_set = user_input
                st.rerun()
            else:
                st.error("⚠️ 間違っています")
    st.stop()

# ==========================================
# 6. 共通関数
# ==========================================
def get_slot_pairs(course):
    d_list = str(course['曜日']).split()
    p_list = str(course['時限']).split()
    return list(zip(d_list, p_list))

def toggle_register(semester, course):
    if isinstance(course, pd.Series): course = course.to_dict()
    cid = course['授業コード']
    if cid not in [b['授業コード'] for b in st.session_state.bookmarks]:
        st.session_state.bookmarks.append(course)
        
    reg = st.session_state.registered[semester]
    if cid in reg:
        del reg[cid]
        return
        
    target_slots = get_slot_pairs(course)
    conflicts = [r_cid for r_cid, r_course in reg.items() if any(s in get_slot_pairs(r_course) for s in target_slots)]
    for c in conflicts:
        del reg[c]
        st.toast("⚠️ 重複授業を仮登録に戻しました")
    reg[cid] = course

def get_total_credits(semester_data):
    total = 0
    for c in semester_data.values():
        match = re.search(r'(\d+\.?\d*)', str(c.get('単位数', '0')))
        if match: total += float(match.group(1))
    return total

def display_links(course):
    l1, l2 = st.columns(2)
    with l1:
        if course.get('詳細URL') and course['詳細URL'] != "不明": 
            st.link_button("📄 シラバス", course['詳細URL'], use_container_width=True)
    with l2:
        if course.get('みんキャン検索LINK') and course['みんキャン検索LINK'] != "不明": 
            st.link_button("🗣️ みんキャン", course['みんキャン検索LINK'], use_container_width=True)

# ダウンロード画像と「みんなの時間割」も鮮やかなグラデーションに統一
def render_image_download_button(semester, registered_data):
    days = ["月", "火", "水", "木", "金"]
    html_str = '<div id="timetable-capture-area" style="background-color: #ffffff; padding: 15px; border-radius: 12px; font-family: \'Helvetica Neue\', Arial, \'Hiragino Kaku Gothic ProN\', \'Hiragino Sans\', Meiryo, sans-serif; position: absolute; top: -9999px; left: -9999px; width: 1024px;">'
    html_str += f'<div style="text-align: center; margin-bottom: 15px; font-weight: bold; color: #333; font-size: 24px; letter-spacing: 1px;"><span style="margin-right: 8px;">🥐</span>C-krat Timetable ({semester})</div>'
    html_str += '<table style="width: 100%; border-collapse: collapse; table-layout: fixed;"><tr><th style="width: 30px;"></th>'
    for d in days: html_str += f'<th style="color: #666; font-size: 16px; padding: 8px 0; border-bottom: 2px solid #ddd;">{d}</th>'
    html_str += '</tr>'
    
    for p in range(1, 7):
        html_str += f'<tr><td style="color: #999; font-weight: bold; font-size: 16px; text-align: right; padding-right: 8px;">{p}</td>'
        for d in days:
            course = next((c for c in registered_data.get(semester, {}).values() if (d, str(p)) in get_slot_pairs(c)), None)
            if course:
                safe_name = html.escape(course['授業名'][:19])
                safe_teacher = html.escape(course['担当教員'].split()[0] if course['担当教員'] != "不明" else "")
                html_str += f'<td style="border: 1px dashed #e0e0e0; height: 100px; padding: 4px;"><div style="background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%); border-radius: 10px; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="font-size: 14px; font-weight: bold; line-height: 1.2; text-align: center; color: #ffffff; letter-spacing: -0.5px; word-break: break-all;">{safe_name}</div><div style="font-size: 11px; color: #ffffff; margin-top:3px; opacity: 0.9;">{safe_teacher}</div></div></td>'
            else:
                html_str += '<td style="border: 1px dashed #e0e0e0; height: 100px; padding: 4px;"></td>'
        html_str += '</tr>'
    html_str += '</table></div>'
    st.markdown(html_str, unsafe_allow_html=True)

    components.html(
        """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <div style="text-align: center; padding: 5px;">
            <button onclick="takeScreenshot()" style="
                background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); color: #fff; font-weight: bold; border: none; padding: 10px 24px;
                border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; font-size: 13px; transition: 0.2s;
            ">📸 時間割を画像で保存 (シェア用)</button>
        </div>
        <script>
        function takeScreenshot() {
            const doc = window.parent.document;
            const target = doc.getElementById('timetable-capture-area');
            if (target) {
                target.style.position = 'static'; 
                html2canvas(target, { scale: 2, backgroundColor: '#ffffff', useCORS: true }).then(canvas => {
                    let link = doc.createElement('a');
                    link.download = 'Ckrat_Timetable.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                    target.style.position = 'absolute'; 
                });
            } else { alert("画像の生成に失敗しました。"); }
        }
        </script>
        """,
        height=60
    )


# ==========================================
# 7. ナビゲーションバー (美しい5列)
# ==========================================
nav1, nav2, nav3, nav4, nav5 = st.columns(5)
if nav1.button("🗓️", type="primary" if st.session_state.current_page == "tt" else "secondary", use_container_width=True, help="マイ時間割"):
    st.session_state.current_page = "tt"
    st.rerun()
if nav2.button("🔍", type="primary" if st.session_state.current_page == "search" else "secondary", use_container_width=True, help="検索"):
    st.session_state.current_page = "search"
    st.rerun()
if nav3.button("⭐", type="primary" if st.session_state.current_page == "bk" else "secondary", use_container_width=True, help="候補"):
    st.session_state.current_page = "bk"
    st.rerun()
if nav4.button("🌍", type="primary" if st.session_state.current_page == "public" else "secondary", use_container_width=True, help="みんなの時間割"):
    st.session_state.current_page = "public"
    st.rerun()
if nav5.button("👤", type="primary" if st.session_state.current_page == "mypage" else "secondary", use_container_width=True, help="マイページ"):
    st.session_state.current_page = "mypage"
    st.rerun()
st.divider()

# ==========================================
# 8. メインUI
# ==========================================

# ------------------------------------------
# 画面1: マイ時間割
# ------------------------------------------
if st.session_state.current_page == "tt":
    if 'current_semester' not in st.session_state: st.session_state.current_semester = "春学期"
        
    if st.session_state.active_slot is None:
        col_h1, col_h2 = st.columns([3, 2])
        with col_h1:
            semester = st.selectbox("学期", ["春学期", "秋学期"], index=0 if st.session_state.current_semester=="春学期" else 1, label_visibility="collapsed")
            st.session_state.current_semester = semester
        with col_h2: 
            st.write(f"✅ **{get_total_credits(st.session_state.registered[semester]):.1f} 単位**")

        days = ["月", "火", "水", "木", "金"]
        
        # ヘッダー行（必ず6列）
        cols = st.columns(6)
        cols[0].markdown("") 
        for i, d in enumerate(days): 
            cols[i+1].markdown(f"<div class='tt-header'>{d}</div>", unsafe_allow_html=True)
            
        # データ行（1〜6限）
        for p in range(1, 7):
            cols = st.columns(6)
            cols[0].markdown(f"<div class='tt-time'>{p}</div>", unsafe_allow_html=True)
            
            for i, d in enumerate(days):
                with cols[i+1]:
                    course = next((c for c in st.session_state.registered.get(semester, {}).values() if (d, str(p)) in get_slot_pairs(c)), None)
                    if course:
                        # 教員名非表示・授業名のみ
                        label = course['授業名'][:11]
                        if st.button(label, key=f"cell_{d}_{p}", type="primary", use_container_width=True):
                            st.session_state.active_slot = {'day': d, 'period': p, 'course': course}
                            st.rerun()
                    else:
                        if st.button("＋", key=f"cell_{d}_{p}", type="secondary", use_container_width=True):
                            st.session_state.active_slot = {'day': d, 'period': p, 'course': None}
                            st.rerun()

        render_image_download_button(semester, st.session_state.registered)

    else:
        d = st.session_state.active_slot['day']
        p = st.session_state.active_slot['period']
        course = st.session_state.active_slot['course']
        semester = st.session_state.current_semester

        col_title, col_close = st.columns([4, 1])
        col_title.subheader(f"⚙️ {d}曜{p}限")
        if col_close.button("✖ 戻る", type="primary"):
            st.session_state.active_slot = None
            st.rerun()

        if course:
            st.success(f"✅ 現在登録中: **{course['授業名']}**")
            st.write(f"担当: {course['担当教員']} | 単位: {course['単位数']}")
            display_links(course)
            st.divider()
            st.write("このコマの授業を変更・削除する場合は下から選んでください。")

        mask = []
        for _, row in df.iterrows():
            if semester.replace("学期","") in row['学期'] and (d, str(p)) in get_slot_pairs(row): mask.append(True)
            else: mask.append(False)
                
        slot_courses = df[mask].sort_values('優先度')
        if len(slot_courses) == 0: st.info("この時間に開講されているシラバス掲載の授業はありません。")
            
        for _, row in slot_courses.head(30).iterrows():
            with st.container(border=True):
                st.write(f"**{row['授業名']}**")
                st.caption(f"コード: {row['授業コード']} | 担当: {row['担当教員']} | 単位: {row['単位数']}")
                b1, b2 = st.columns(2)
                is_reg = row['授業コード'] in st.session_state.registered[semester]
                
                if b1.button("解除" if is_reg else "✅ 本登録", key=f"reg_{row['授業コード']}"):
                    toggle_register(semester, row.to_dict())
                    st.session_state.active_slot = None 
                    save_and_rerun()
                    
                is_bk = row['授業コード'] in [bk['授業コード'] for bk in st.session_state.bookmarks]
                if b2.button("外す" if is_bk else "⭐ 候補へ", key=f"bk_{row['授業コード']}"):
                    if not is_bk: st.session_state.bookmarks.append(row.to_dict())
                    else: st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b['授業コード'] != row['授業コード']]
                    save_and_rerun()
                    
                display_links(row.to_dict())

        st.divider()
        with st.expander("＋ オリジナルの授業を作成する"):
            with st.form(f"custom_course_{d}_{p}"):
                c_name = st.text_input("授業名（必須）")
                c_teacher = st.text_input("担当教員")
                c_credits = st.number_input("単位数", value=2.0)
                if st.form_submit_button("✅ このコマに登録"):
                    if not c_name.strip(): st.error("入力してください")
                    else:
                        toggle_register(semester, {
                            "授業コード": f"MY_{int(time.time())}", "授業名": c_name, "担当教員": c_teacher if c_teacher else "不明",
                            "単位数": f"{c_credits}単位", "曜日": d, "時限": str(p), "学期": semester, "詳細URL": "不明", "みんキャン検索LINK": "不明", "優先度": 99
                        })
                        st.session_state.active_slot = None
                        save_and_rerun()

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
    if s_sem != "すべて": res = res[res['学期'].str.contains(s_sem)]
    if s_day != "すべて": res = res[res['曜日'].str.contains(s_day)]
    if s_per != "すべて": res = res[res['時限'].astype(str).str.contains(s_per)]
    if query: res = res[res['授業名'].str.contains(query, case=False) | res['担当教員'].str.contains(query, case=False) | res['授業コード'].str.contains(query, case=False)]

    res = res.sort_values('優先度')
    st.write(f"結果: **{len(res)}件** (50件まで)")
    
    for _, row in res.head(50).iterrows():
        with st.container(border=True):
            t_str = " ".join([f"{d}{p}限" for d, p in get_slot_pairs(row)])
            st.write(f"**{row['授業名']}**")
            st.caption(f"コード: {row['授業コード']} | {row['学期']} | {t_str} | {row['担当教員']}")
            
            c1, c2 = st.columns(2)
            active_sem = "春学期" if "春" in row['学期'] else "秋学期"
            is_reg = row['授業コード'] in st.session_state.registered[active_sem]
            
            if c1.button("解除" if is_reg else "✅ 本登録", key=f"src_reg_{row['授業コード']}"):
                toggle_register(active_sem, row.to_dict())
                save_and_rerun()
                
            is_bk = row['授業コード'] in [b['授業コード'] for b in st.session_state.bookmarks]
            if c2.button("外す" if is_bk else "⭐ 候補へ", key=f"src_bk_{row['授業コード']}"):
                if not is_bk: st.session_state.bookmarks.append(row.to_dict())
                else: st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b['授業コード'] != row['授業コード']]
                save_and_rerun()
                
            display_links(row.to_dict())

# ------------------------------------------
# 画面3: 候補(ブックマーク)画面
# ------------------------------------------
elif st.session_state.current_page == "bk":
    st.subheader("⭐ 保存した授業 (候補)")
    if not st.session_state.bookmarks: st.info("検索画面から⭐を押して保存してください。")
        
    for b in st.session_state.bookmarks:
        with st.container(border=True):
            t_str = " ".join([f"{d}{p}限" for d, p in get_slot_pairs(b)])
            st.write(f"**{b['授業名']}**")
            display_code = "手動入力" if b['授業コード'].startswith("MY_") else b['授業コード']
            st.caption(f"コード: {display_code} | {b['学期']} | {t_str} | {b['担当教員']}")
            
            c1, c2 = st.columns(2)
            active_sem = "春学期" if "春" in b['学期'] else "秋学期"
            is_reg = b['授業コード'] in st.session_state.registered[active_sem]
            
            if c1.button("解除" if is_reg else "✅ 本登録", key=f"bk_reg_{b['授業コード']}"):
                toggle_register(active_sem, b)
                save_and_rerun()
                
            if c2.button("🗑️ 削除", key=f"bk_del_{b['授業コード']}"):
                st.session_state.bookmarks = [x for x in st.session_state.bookmarks if x['授業コード'] != b['授業コード']]
                if is_reg: del st.session_state.registered[active_sem][b['授業コード']]
                save_and_rerun()
                
            if not b['授業コード'].startswith("MY_"): display_links(b)

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
            target_dept = target_data.get('department', '未設定')
            target_gender = target_data.get('gender', '未設定')
            
            c_head1, c_head2 = st.columns([3, 2])
            with c_head1: p_sem = st.selectbox("表示する学期", ["春学期", "秋学期"])
            with c_head2:
                has_liked = my_id in likes_list
                like_btn_text = f"❤️ {len(likes_list)}" if has_liked else f"🤍 いいね ({len(likes_list)})"
                if st.button(like_btn_text, use_container_width=True):
                    if has_liked: target_data['likes'].remove(my_id)
                    else: target_data['likes'].append(my_id)
                    save_users(users)
                    st.rerun()

            st.write(f"👤 **{selected_user}** ({target_dept} / {target_gender}) さんの {p_sem}（計 {get_total_credits(target_data['registered'].get(p_sem, {})):.1f} 単位）")
            
            days = ["月", "火", "水", "木", "金"]
            html_str = '<table style="width: 100%; border-collapse: collapse; table-layout: fixed;"><tr><th style="width: 20px;"></th>'
            for d in days: html_str += f'<th style="color: #666; font-size: 11px; padding: 4px 0; border-bottom: 2px solid #ddd; text-align:center;">{d}</th>'
            html_str += '</tr>'
            for p in range(1, 7):
                html_str += f'<tr><td style="color: #999; font-weight: bold; font-size: 11px; text-align: right; padding-right: 4px;">{p}</td>'
                for d in days:
                    course = next((c for c in target_data['registered'].get(p_sem, {}).values() if (d, str(p)) in get_slot_pairs(c)), None)
                    if course:
                        # みんなの時間割も同じグラデーションに
                        safe_name = html.escape(course['授業名'][:15])
                        html_str += f'<td style="border: 1px dashed #e0e0e0; height: 60px; padding: 1px;"><div style="background: linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%); border-radius: 6px; height: 100%; display: flex; align-items: center; justify-content: center; padding: 2px;"><div style="font-size: 8px; font-weight: bold; line-height: 1.1; text-align: center; color: #ffffff;">{safe_name}</div></div></td>'
                    else: html_str += '<td style="border: 1px dashed #e0e0e0; height: 60px; padding: 1px;"></td>'
                html_str += '</tr>'
            html_str += '</table>'
            st.markdown(html_str, unsafe_allow_html=True)

# ------------------------------------------
# 画面5: マイページ
# ------------------------------------------
elif st.session_state.current_page == "mypage":
    st.subheader("👤 マイページ & 設定")
    
    users = load_users()
    user_data = users.get(st.session_state.current_user, {})
    current_dept = user_data.get("department", "未設定")
    current_gender = user_data.get("gender", "未設定")
    
    st.write(f"**ユーザー名:** {st.session_state.current_user}")
    
    with st.expander("📝 プロフィール設定", expanded=True):
        dept_options = ["未設定", "経営", "会計", "金融", "国マ"]
        gender_options = ["未設定", "男性", "女性", "その他"]
        
        new_dept = st.selectbox("学科・プログラム", dept_options, index=dept_options.index(current_dept) if current_dept in dept_options else 0)
        new_gender = st.selectbox("性別", gender_options, index=gender_options.index(current_gender) if current_gender in gender_options else 0)
        
        if st.button("属性を保存", use_container_width=True):
            users[st.session_state.current_user]["department"] = new_dept
            users[st.session_state.current_user]["gender"] = new_gender
            save_users(users)
            st.success("✅ 保存しました！")
            time.sleep(1)
            st.rerun()

    with st.expander("⚙️ アカウント設定"):
        new_username = st.text_input("新しいユーザー名", placeholder="新しい名前を入力", label_visibility="collapsed")
        if st.button("ユーザー名を変更", use_container_width=True):
            if not new_username: st.error("入力してください")
            else:
                if new_username in users: st.error("既に使われています")
                else:
                    old_username = st.session_state.current_user
                    users[new_username] = users.pop(old_username)
                    for u_data in users.values():
                        if "likes" in u_data and old_username in u_data["likes"]:
                            u_data["likes"].remove(old_username)
                            u_data["likes"].append(new_username)
                    save_users(users)
                    st.session_state.current_user = new_username
                    st.session_state.pending_rename_set = new_username
                    st.success("✅ 変更しました！")
                    time.sleep(1)
                    st.rerun()
        
        st.divider()
        st.warning("⚠️ 一度削除すると復旧できません")
        if st.button("🗑️ アカウント削除", type="primary", use_container_width=True):
            user_to_del = st.session_state.current_user
            if user_to_del in users:
                del users[user_to_del]
                for u_data in users.values():
                    if "likes" in u_data and user_to_del in u_data["likes"]:
                        u_data["likes"].remove(user_to_del)
                save_users(users)
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.pending_logout = True
            st.rerun()
    
    st.divider()
    if st.button("🚪 ログアウト", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.pending_logout = True
        st.rerun()
