from datetime import date
from contextlib import contextmanager
from html import escape
import re
import streamlit as st

from bucketly.database import (
    create_item,
    delete_item,
    get_profile,
    init_db,
    list_items,
    save_feedback,
    save_profile,
    update_item,
    update_status,
)

st.set_page_config(
    page_title="Bucketly",
    page_icon="🪂",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

CATEGORIES = [
    "🌍 Travel", "🏔️ Adventure", "❤️ Relationships", "👨‍👩‍👧 Family",
    "🎓 Learning", "💼 Career", "🏠 Home", "🏍️ Vehicles",
    "🎨 Creative", "🏋️ Fitness", "🍜 Food", "🎉 Experiences", "✨ Personal"
]
STATUSES = ["Dream", "Planned", "In Progress", "Completed"]
PAGES = [
    "🏠 Dashboard", "🪣 My Bucket", "➕ Add Experience", "📸 Memories",
    "⚙️ Settings", "ℹ️ About & Contact",
]
PROFILE_AVATARS = {
    "compass": ("🧭", "Compass"),
    "mountain": ("🏔️", "Mountain"),
    "sunrise": ("🌅", "Sunrise"),
    "wave": ("🌊", "Wave"),
    "forest": ("🌿", "Forest"),
    "camera": ("📸", "Camera"),
    "airplane": ("✈️", "Traveler"),
    "star": ("🌟", "Star"),
}
STATUS_BADGES = {
    "Dream": ("✧", "dream"),
    "Planned": ("◷", "planned"),
    "In Progress": ("↗", "in-progress"),
    "Completed": ("✓", "completed"),
}


def navigate_to(page):
    st.session_state["page"] = page


def change_status(item_id, item_title):
    status = st.session_state[f"status_{item_id}"]
    update_status(item_id, status)
    queue_toast(f"{item_title} saved as {status}.")


def queue_toast(message, icon="✅"):
    st.session_state["bucketly_toast"] = (message, icon)


def show_queued_toast():
    notification = st.session_state.pop("bucketly_toast", None)
    if notification:
        st.toast(notification[0], icon=notification[1])


def parse_date(value):
    return date.fromisoformat(value) if value else None


def format_date(value):
    if not value:
        return ""
    try:
        parsed = date.fromisoformat(value)
        return f"{parsed:%b} {parsed.day}, {parsed.year}"
    except ValueError:
        return value


def app_button(label, *, primary=False, key=None, on_click=None, args=(), use_container_width=False):
    return st.button(
        label,
        type="primary" if primary else "secondary",
        key=key,
        on_click=on_click,
        args=args,
        use_container_width=use_container_width,
    )


@contextmanager
def app_card():
    with st.container(border=True):
        yield


def status_badge(status):
    icon, style = STATUS_BADGES.get(status, ("•", "dream"))
    st.markdown(
        f'<span class="status-badge status-{style}"><span>{icon}</span>{escape(status)}</span>',
        unsafe_allow_html=True,
    )


def inject_css():
    st.markdown("""
    <style>
    :root {
        --teal: #2D5C5C;
        --teal-deep: #1F4D4D;
        --gold: #D4A574;
        --gold-hover: #BD8C59;
        --cream: #F9F7F3;
        --surface: #FFFEFB;
        --ink: #2C3E3E;
        --muted: #887A70;
        --line: #E6DED4;
        --shadow: 0 8px 24px rgba(44, 62, 62, .07);
    }
    .block-container { max-width: 1200px; padding: 32px 32px 56px; }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: Inter, "Segoe UI", Roboto, sans-serif;
        color: var(--ink);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    p, label, input, textarea, button, [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"] {
        font-family: Inter, "Segoe UI", Roboto, sans-serif !important;
        line-height: 1.6 !important;
    }
    h1, h2, h3 {
        color: var(--teal-deep);
        font-family: Georgia, Garamond, serif !important;
        line-height: 1.25;
    }
    [data-testid="stAppViewContainer"] {
        background-color: var(--cream);
        background-image:
            repeating-radial-gradient(ellipse at 96% 4%, transparent 0 44px, rgba(45, 92, 92, .045) 45px, transparent 46px 86px),
            linear-gradient(135deg, #F9F7F3 0%, #F6F1E9 56%, #EFF4F0 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] {
        width: 250px !important;
        min-width: 250px !important;
        background: linear-gradient(180deg, var(--teal) 0%, var(--teal-deep) 100%);
        border-right: 1px solid rgba(31, 77, 77, .25);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--teal) 0%, var(--teal-deep) 100%);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] h2 { color: #FFFFFF; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 6px;
        padding: 8px 10px;
        transition: background-color .2s ease, color .2s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.1); }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: var(--gold);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
        color: var(--teal-deep) !important;
        font-weight: 700;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 32px;
        border: 1px solid rgba(255,255,255,.2);
        border-radius: 8px;
        background: linear-gradient(118deg, #1F4D4D, #2D5C5C 70%, #3B7070);
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 14px 30px rgba(31, 77, 77, .18);
    }
    .hero h1 { margin: 6px 0 0; color: #FFFFFF; font-size: 2.15rem; }
    .hero p { color: #F4F7F4; font-size: 1rem; margin: 10px 0 0; }
    .hero-tag {
        display: inline-block;
        padding: 5px 9px;
        border: 1px solid rgba(212, 165, 116, .7);
        border-radius: 4px;
        color: #F1D6B7;
        font-family: Inter, "Segoe UI", sans-serif;
        font-size: .75rem;
        font-weight: 700;
    }
    .metric-card {
        position: relative;
        overflow: hidden;
        padding: 20px 20px 18px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
        min-height: 112px;
        box-shadow: 0 5px 16px rgba(44, 62, 62, .055);
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
    .metric-card::before {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        width: 4px;
        background: var(--gold);
        content: "";
    }
    .metric-number { font-size: 1.8rem; line-height: 1.2; font-weight: 700; color: var(--teal-deep); }
    .metric-label { color: var(--muted); font-size: .9rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line);
        border-radius: 8px;
        background: var(--surface);
        box-shadow: 0 6px 18px rgba(44, 62, 62, .06);
        transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        border-color: rgba(45, 92, 92, .36);
        box-shadow: var(--shadow);
    }
    [data-testid="stForm"] {
        padding: 24px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--surface);
        box-shadow: var(--shadow);
    }
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] > div {
        border-color: #D8CEC0 !important;
        border-radius: 4px !important;
        background: var(--cream) !important;
    }
    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] textarea:focus,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 2px rgba(45, 92, 92, .16) !important;
    }
    [data-testid="stBaseButton-primary"] {
        border: 1px solid var(--gold) !important;
        border-radius: 6px !important;
        background: var(--gold) !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
        transition: background-color .2s ease, transform .2s ease, box-shadow .2s ease !important;
    }
    [data-testid="stBaseButton-primary"]:hover {
        border-color: var(--gold-hover) !important;
        background: var(--gold-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(44, 62, 62, .12);
    }
    [data-testid="stBaseButton-secondary"] {
        border: 1px solid var(--teal) !important;
        border-radius: 6px !important;
        background: transparent !important;
        color: var(--teal-deep) !important;
        transition: background-color .2s ease, transform .2s ease !important;
    }
    [data-testid="stBaseButton-secondary"]:hover {
        background: rgba(45, 92, 92, .08) !important;
        transform: translateY(-1px);
    }
    [data-testid="stAppViewContainer"] [role="radiogroup"] label:has(input:checked) {
        border-radius: 5px;
        background: var(--teal);
    }
    [data-testid="stAppViewContainer"] [role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 700;
    }
    [data-testid="stAppViewContainer"] [data-baseweb="input"] input,
    [data-testid="stAppViewContainer"] [data-baseweb="textarea"] textarea {
        color: var(--ink) !important;
    }
    [data-testid="stAppViewContainer"] [data-baseweb="select"] div {
        color: var(--ink);
    }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    [role="radiogroup"] label { border-radius: 5px; }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: .82rem;
        font-weight: 600;
    }
    .status-dream { background: #EAE7E0; color: #625D53; }
    .status-planned { background: #F5E8CF; color: #795A2A; }
    .status-in-progress { background: #DDEBE8; color: #285B58; }
    .status-completed { background: #E3EBDD; color: #426044; }
    [data-testid="stAlert"] { border-radius: 6px; }
    [data-testid="stAlertContentSuccess"] {
        border-left: 4px solid var(--gold);
        border-radius: 5px;
        background: #F7EEDC;
        color: var(--teal-deep);
    }
    [data-testid="stAlertContentError"] {
        border-left: 4px solid #C96F68;
        border-radius: 5px;
        background: #F9E8E5;
        color: #713F3B;
    }
    [data-testid="stAlertContentSuccess"] [data-testid="stMarkdownContainer"],
    [data-testid="stAlertContentError"] [data-testid="stMarkdownContainer"] {
        color: inherit;
    }
    [data-testid="stToast"] {
        animation: toast-dismiss 3s ease forwards;
    }
    @keyframes toast-dismiss {
        0%, 82% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-8px); visibility: hidden; }
    }
    [data-testid="stExpander"] details,
    [data-testid="stPopover"] button {
        border-color: var(--line);
        border-radius: 6px;
    }
    .stAppViewContainer main > div { animation: page-enter .28s ease-out both; }
    @keyframes page-enter {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }
    @media (max-width: 640px) {
        .block-container { padding: 16px 16px 32px; }
        section[data-testid="stSidebar"] { min-width: min(250px, 85vw) !important; }
        .hero { padding: 24px; }
        .hero h1 { font-size: 1.55rem; }
        [data-testid="stForm"] { padding: 16px; }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_css()
    show_queued_toast()
    items = list_items()
    profile = get_profile()

    with st.sidebar:
        st.markdown("## 🪂 Bucketly")
        st.caption("Dream. Plan. Experience. Remember.")
        avatar, _ = PROFILE_AVATARS.get(profile["avatar_id"], PROFILE_AVATARS["compass"])
        profile_summary = st.empty()
        profile_summary.write(f"{avatar}  {profile['name'] or 'Set up your profile'}")
        username_summary = st.empty()
        if profile["username"]:
            username_summary.caption(f"@{profile['username']}")
        page = st.radio(
            "Navigation",
            PAGES,
            label_visibility="collapsed",
            key="page",
        )
        st.divider()
        st.caption(f"{len(items)} experiences in your bucket")

    if page == "⚙️ Settings":
        st.title("Profile & settings")
        st.caption("Add the details you want associated with your Bucketly profile.")

        with st.form("profile_settings"):
            st.subheader("Your profile")
            st.caption(":red[*] Required field")
            name = st.text_input("Name :red[*]", value=profile["name"], key="profile_name")
            username = st.text_input(
                "Username", value=profile["username"], placeholder="e.g. sam.rivera",
                key="profile_username",
            )
            email = st.text_input(
                "Email address", value=profile["email"], placeholder="name@example.com",
                key="profile_email",
            )
            contact_number = st.text_input(
                "Contact number", value=profile["contact_number"], placeholder="Optional",
                key="profile_contact",
            )

            avatar_col, preview_col = st.columns([2, 1])
            with avatar_col:
                avatar_id = st.selectbox(
                    "Default profile avatar",
                    list(PROFILE_AVATARS),
                    index=list(PROFILE_AVATARS).index(profile["avatar_id"])
                    if profile["avatar_id"] in PROFILE_AVATARS else 0,
                    format_func=lambda key: f"{PROFILE_AVATARS[key][0]}  {PROFILE_AVATARS[key][1]}",
                    key="profile_avatar",
                )
            with preview_col:
                st.caption("Avatar preview")
                st.markdown(f"## {PROFILE_AVATARS[avatar_id][0]}")

            is_public = st.toggle(
                "Make my profile visible", value=bool(profile["is_public"]),
                key="profile_is_public",
            )
            st.caption(
                "Visibility is saved as a preference. Bucketly is currently local-only "
                "and does not publish profile details."
            )
            submitted = st.form_submit_button("Save profile", type="primary", use_container_width=True)

            if submitted:
                clean_name = name.strip()
                clean_username = username.strip().removeprefix("@").casefold()
                clean_email = email.strip()
                clean_contact = contact_number.strip()
                errors = []
                if not clean_name:
                    errors.append("Name is required.")
                if clean_username and not re.fullmatch(r"[a-z0-9_.-]{2,30}", clean_username):
                    errors.append("Username must be 2–30 characters using letters, numbers, dots, underscores, or hyphens.")
                if clean_email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean_email):
                    errors.append("Enter a valid email address or leave the field empty.")
                if clean_contact and not re.fullmatch(r"[+()\d .-]{7,25}", clean_contact):
                    errors.append("Enter a valid contact number or leave the field empty.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    save_profile(
                        clean_username, clean_name, clean_contact, clean_email,
                        is_public, avatar_id,
                    )
                    avatar, _ = PROFILE_AVATARS[avatar_id]
                    profile_summary.write(f"{avatar}  {clean_name}")
                    if clean_username:
                        username_summary.caption(f"@{clean_username}")
                    else:
                        username_summary.empty()
                    st.toast("Profile saved.", icon="✅")

        return

    if page == "ℹ️ About & Contact":
        st.title("About & Contact")
        st.caption("The story behind Bucketly, and a place to leave feedback.")

        st.markdown("""
        <div class="hero">
            <div class="hero-tag">BUCKETLY · A LIFE EXPERIENCES JOURNAL</div>
            <h1>Keep the things you want to live.</h1>
            <p>Bucketly helps you collect meaningful experiences, plan your next step, and keep a record of what you have done.</p>
        </div>
        """, unsafe_allow_html=True)

        about_col, maintainer_col = st.columns([1.5, 1])
        with about_col:
            st.subheader("What Bucketly is for")
            st.write(
                "A personal place for the trips, challenges, skills, and small moments "
                "you hope to make time for. Organize ideas by category, move them from "
                "dream to done, and add a reflection when they become memories."
            )
            st.subheader("Built around your list")
            st.write("Capture ideas, set a priority or target date, track progress, and keep reflections with completed experiences.")
        with maintainer_col:
            st.subheader("Maintainer")
            st.write("githubofkrishnadhas")
            st.caption("Project identity shown from the repository author history.")
            st.caption("Bucketly is an independent, local-first project. No maintainer email is configured in this app.")

        st.divider()
        st.subheader("Send feedback")
        st.caption("Share an idea, report a problem, or leave a note about your experience.")
        with st.form("feedback_form", clear_on_submit=True):
            feedback_type = st.selectbox(
                "Feedback type", ["General feedback", "Feature idea", "Bug report", "Other"]
            )
            feedback_name = st.text_input("Name (optional)", value=profile["name"])
            feedback_email = st.text_input("Email (optional)", value=profile["email"])
            feedback_message = st.text_area(
                "Message :red[*]", placeholder="What would you like us to know?"
            )
            st.caption(":red[*] Required field")
            feedback_submitted = st.form_submit_button(
                "Save feedback", type="primary", use_container_width=True
            )
            if feedback_submitted:
                clean_message = feedback_message.strip()
                clean_email = feedback_email.strip()
                if not clean_message:
                    st.error("Please add a message before submitting.")
                elif clean_email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean_email):
                    st.error("Enter a valid email address or leave the field empty.")
                else:
                    save_feedback(
                        feedback_type, feedback_name.strip(), clean_email, clean_message
                    )
                    st.toast("Feedback saved locally.", icon="✅")

        return

    if page == "➕ Add Experience":
        st.title("Add an experience")
        st.caption("Start with something you genuinely want to do.")

        with st.form("add_experience", clear_on_submit=True):
            title = st.text_input("What do you want to do?", placeholder="e.g. Trek the Himalayas")
            description = st.text_area("A little more about it", placeholder="Why does this matter to you?")
            c1, c2, c3 = st.columns(3)
            with c1:
                category = st.selectbox("Category", CATEGORIES)
            with c2:
                priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            with c3:
                status = st.selectbox("Status", STATUSES, index=0)

            c4, c5 = st.columns(2)
            with c4:
                location = st.text_input("Location", placeholder="Optional")
            with c5:
                target_date = st.date_input("Target date", value=None)
            reflection = st.text_area("Reflection (optional)", placeholder="A note to remember this by")

            submitted = st.form_submit_button("Add to bucket", type="primary", use_container_width=True)

            if submitted:
                if not title.strip():
                    st.error("Give your experience a name first.")
                else:
                    create_item(
                        title.strip(), description.strip(), category, priority,
                        location.strip(), target_date.isoformat() if target_date else None,
                        status, reflection.strip(),
                    )
                    queue_toast(f"Saved {title.strip()} to your bucket.")
                    st.rerun()

        return

    if page == "🪣 My Bucket":
        st.title("My bucket")
        st.caption("Search, sort, and shape your next experience.")
        app_button("Add an experience", primary=True, on_click=navigate_to, args=("➕ Add Experience",))
        if not items:
            st.info("Your bucket is empty. Add the first thing you want to experience.")
            app_button("Add your first experience", on_click=navigate_to, args=("➕ Add Experience",))
            return

        search_col, status_col, category_col = st.columns([2, 1, 1])
        with search_col:
            search = st.text_input("Search", placeholder="Title, note, or location")
        with status_col:
            status_filter = st.selectbox("Status", ["All statuses", *STATUSES], key="filter_status")
        with category_col:
            saved_categories = [item["category"] for item in items if item["category"]]
            category_options = ["All categories", *dict.fromkeys([*CATEGORIES, *saved_categories])]
            category_filter = st.selectbox(
                "Category", category_options, key="filter_category"
            )
        search_term = search.casefold().strip()
        filtered = [
            item for item in items
            if (not search_term or search_term in " ".join(
                (item["title"] or "", item["description"] or "", item["location"] or "")
            ).casefold())
            and (status_filter == "All statuses" or item["status"] == status_filter)
            and (
                category_filter == "All categories"
                or (item["category"] or "").strip().casefold() == category_filter.strip().casefold()
            )
        ]
        st.caption(f"{len(filtered)} experience{'s' if len(filtered) != 1 else ''}")

        if not filtered:
            st.info("No experiences match those filters.")

        for item in filtered:
            with app_card():
                st.subheader(item["title"])
                st.caption(f"{item['category']}  ·  {item['priority']} priority")
                if item["description"]:
                    st.write(item["description"])
                if item["location"]:
                    st.caption(f"Location: {item['location']}")
                if item["target_date"]:
                    st.caption(f"Target: {format_date(item['target_date'])}")
                status_badge(item["status"])
                st.radio(
                    "Update status", STATUSES,
                    index=STATUSES.index(item["status"])
                    if item["status"] in STATUSES else 0,
                    key=f"status_{item['id']}",
                    on_change=change_status,
                    args=(item["id"], item["title"]),
                    horizontal=True,
                )

                with st.expander("Edit experience"):
                    category_index = CATEGORIES.index(item["category"]) if item["category"] in CATEGORIES else 0
                    with st.form(f"edit_{item['id']}"):
                        edited_title = st.text_input("Title", item["title"], key=f"title_{item['id']}")
                        edited_description = st.text_area(
                            "Description", item["description"] or "", key=f"description_{item['id']}"
                        )
                        edit_left, edit_right = st.columns(2)
                        with edit_left:
                            edited_category = st.selectbox(
                                "Category", CATEGORIES, index=category_index, key=f"category_{item['id']}"
                            )
                            edited_priority = st.selectbox(
                                "Priority", ["Low", "Medium", "High"],
                                index=["Low", "Medium", "High"].index(item["priority"])
                                if item["priority"] in ["Low", "Medium", "High"] else 1,
                                key=f"priority_{item['id']}",
                            )
                        with edit_right:
                            edited_location = st.text_input(
                                "Location", item["location"] or "", key=f"location_{item['id']}"
                            )
                            edited_target = st.date_input(
                                "Target date", value=parse_date(item["target_date"]), key=f"target_{item['id']}"
                            )
                        edited_reflection = st.text_area(
                            "Memory / reflection", item["reflection"] or "", key=f"reflection_{item['id']}"
                        )
                        save = st.form_submit_button("Save changes", type="primary")
                        if save:
                            if not edited_title.strip():
                                st.error("An experience needs a title.")
                            else:
                                update_item(
                                    item["id"], edited_title.strip(), edited_description.strip(),
                                    edited_category, edited_priority, edited_location.strip(),
                                    edited_target.isoformat() if edited_target else None,
                                    edited_reflection.strip(),
                                )
                                queue_toast(f"Changes to {edited_title.strip()} saved.")
                                st.rerun()

                with st.popover("Delete"):
                    st.write(f"Delete **{item['title']}** permanently?")
                    if app_button("Confirm delete", key=f"delete_{item['id']}", primary=True):
                        delete_item(item["id"])
                        st.rerun()
        return

    if page == "📸 Memories":
        memories = [item for item in items if item["status"] == "Completed"]
        st.title("Memories")
        st.caption("The things you made happen, and what you want to remember about them.")
        if not memories:
            st.info("Completed experiences will appear here.")
            app_button("Explore your bucket", on_click=navigate_to, args=("🪣 My Bucket",))
            return
        for item in memories:
            with app_card():
                st.subheader(item["title"])
                status_badge(item["status"])
                meta = [item["category"]]
                if item["completed_at"]:
                    meta.append(f"Completed {format_date(item['completed_at'])}")
                if item["location"]:
                    meta.append(item["location"])
                st.caption(" · ".join(meta))
                if item["reflection"]:
                    st.write(item["reflection"])
                else:
                    st.caption("Add a reflection from the experience editor in My Bucket.")
        return

    st.markdown("""
    <div class="hero">
        <div class="hero-tag">YOUR EXPERIENCE JOURNAL</div>
        <h1>Make room for the memorable.</h1>
        <p>Keep your ideas close, give them a next step, and remember the ones you made real.</p>
    </div>
    """, unsafe_allow_html=True)

    total = len(items)
    planned = sum(i["status"] in ("Planned", "In Progress") for i in items)
    completed = sum(i["status"] == "Completed" for i in items)
    dreams = sum(i["status"] == "Dream" for i in items)

    cols = st.columns(4)
    metrics = [
        ("🪣", total, "Bucket items"),
        ("📅", planned, "Planned"),
        ("✅", completed, "Completed"),
        ("✨", dreams, "Still dreaming"),
    ]
    for col, (icon, value, label) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div>{icon}</div>'
                f'<div class="metric-number">{value}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("Recently added")
        if not items:
            st.info("Your bucket is ready for its first idea.")
            app_button("Add your first experience", primary=True, on_click=navigate_to, args=("➕ Add Experience",))
        else:
            for item in items[:5]:
                with app_card():
                    st.markdown(f"**{item['title']}**")
                    st.caption(f"{item['category']}  ·  {item['priority']} priority")
                    status_badge(item["status"])

    with right:
        st.subheader("Your next step")
        st.write("A good list starts with one thing you would be glad you did.")
        app_button(
            "Add an experience", primary=True, use_container_width=True,
            on_click=navigate_to, args=("➕ Add Experience",),
        )
        if completed:
            st.write(f"You have **{completed}** experience{'s' if completed != 1 else ''} to look back on.")
            app_button("Open memories", use_container_width=True,
                       on_click=navigate_to, args=("📸 Memories",))

if __name__ == "__main__":
    main()
