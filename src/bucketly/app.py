from datetime import date
import streamlit as st

from bucketly.database import (
    create_item,
    delete_item,
    init_db,
    list_items,
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
PAGES = ["🏠 Dashboard", "🪣 My Bucket", "➕ Add Experience", "📸 Memories"]


def navigate_to(page):
    st.session_state["page"] = page


def change_status(item_id):
    update_status(item_id, st.session_state[f"status_{item_id}"])


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

def inject_css():
    st.markdown("""
    <style>
    :root {
        --ink: #1e3329;
        --muted: #617269;
        --pine: #173e32;
        --pine-deep: #102f27;
        --copper: #b85c3b;
        --line: #ccd8ce;
        --surface: #fbfcf9;
    }
    .block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 3.5rem; }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif;
        color: var(--ink);
    }
    p, label, input, textarea, button, [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"] {
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif !important;
        font-size: 14pt !important;
    }
    h1, h2, h3 {
        color: var(--ink);
        font-family: "Georgia", "Palatino Linotype", serif !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #e7ede6;
        background-image:
            repeating-radial-gradient(ellipse at 94% 4%, transparent 0 31px, rgba(30, 65, 48, .055) 32px, transparent 33px 58px),
            linear-gradient(140deg, #e5ede5 0%, #eef0e4 54%, #e1ebeb 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: var(--pine);
        border-right: 1px solid var(--pine-deep);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #edf3eb !important;
    }
    [data-testid="stSidebar"] h2 { color: #fffaf0; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 7px;
        padding: .3rem .45rem;
        transition: background-color .16s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.09); }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.1rem 2.25rem;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 10px;
        background: linear-gradient(115deg, #153a30, #245c48 70%, #37745a);
        color: #fffaf0;
        margin-bottom: 1.35rem;
        box-shadow: 0 16px 32px rgba(24, 53, 40, .16);
    }
    .hero h1 { margin: .35rem 0 0; color: #fffaf0; font-size: 2.15rem; }
    .hero p { color: #d9e8dc; font-size: 1rem; margin: .55rem 0 0; }
    .hero-tag {
        display: inline-block;
        padding: .3rem .55rem;
        border: 1px solid rgba(240, 197, 135, .48);
        border-radius: 4px;
        color: #f0c587;
        font-family: "Aptos", "Segoe UI", sans-serif;
        font-size: .76rem;
        font-weight: 700;
    }
    .metric-card {
        position: relative;
        overflow: hidden;
        padding: 1.1rem 1.2rem 1.05rem;
        border: 1px solid var(--line);
        border-radius: 9px;
        background: var(--surface);
        min-height: 112px;
        box-shadow: 0 5px 16px rgba(31, 59, 44, .06);
    }
    .metric-card::before {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        width: 4px;
        background: var(--copper);
        content: "";
    }
    .metric-number { font-size: 1.8rem; line-height: 1.2; font-weight: 700; color: var(--ink); }
    .metric-label { color: var(--muted); font-size: .9rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line);
        border-radius: 9px;
        background: rgba(251, 252, 249, .94);
        box-shadow: 0 7px 20px rgba(31, 59, 44, .055);
    }
    [data-testid="stForm"] {
        padding: 1.15rem 1.25rem;
        border: 1px solid var(--line);
        border-radius: 9px;
        background: var(--surface);
        box-shadow: 0 8px 24px rgba(31, 59, 44, .07);
    }
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] > div {
        border-color: #bccbc0 !important;
        border-radius: 6px !important;
        background: #fff !important;
    }
    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] textarea:focus,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--pine) !important;
        box-shadow: 0 0 0 2px rgba(37, 93, 71, .16) !important;
    }
    [data-testid="stBaseButton-primary"] {
        border: 1px solid var(--copper) !important;
        border-radius: 6px !important;
        background: var(--copper) !important;
        color: white !important;
        font-weight: 700 !important;
    }
    [data-testid="stBaseButton-primary"]:hover {
        border-color: #99472e !important;
        background: #99472e !important;
    }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    [role="radiogroup"] label { border-radius: 5px; }
    [role="radiogroup"] input:checked + div { color: var(--pine); }
    [data-testid="stExpander"] details,
    [data-testid="stPopover"] button {
        border-color: var(--line);
        border-radius: 6px;
    }
    @media (max-width: 640px) {
        .block-container { padding: 1rem 1rem 2rem; }
        .hero { padding: 1.45rem; }
        .hero h1 { font-size: 1.55rem; }
        [data-testid="stForm"] { padding: .9rem; }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_css()
    items = list_items()

    with st.sidebar:
        st.markdown("## 🪂 Bucketly")
        st.caption("Dream. Plan. Experience. Remember.")
        page = st.radio(
            "Navigation",
            PAGES,
            label_visibility="collapsed",
            key="page",
        )
        st.divider()
        st.caption(f"{len(items)} experiences in your bucket")

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
                    st.success(f"Added {title.strip()} to your bucket.")

        return

    if page == "🪣 My Bucket":
        st.title("My bucket")
        st.caption("Search, sort, and shape your next experience.")
        st.button("Add an experience", type="primary", on_click=navigate_to, args=("➕ Add Experience",))
        if not items:
            st.info("Your bucket is empty. Add the first thing you want to experience.")
            st.button("Add your first experience", on_click=navigate_to, args=("➕ Add Experience",))
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
            with st.container(border=True):
                st.subheader(item["title"])
                st.caption(f"{item['category']}  ·  {item['priority']} priority")
                if item["description"]:
                    st.write(item["description"])
                if item["location"]:
                    st.caption(f"Location: {item['location']}")
                if item["target_date"]:
                    st.caption(f"Target: {format_date(item['target_date'])}")
                st.radio(
                    "Update status", STATUSES,
                    index=STATUSES.index(item["status"])
                    if item["status"] in STATUSES else 0,
                    key=f"status_{item['id']}",
                    on_change=change_status,
                    args=(item["id"],),
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
                                st.success("Changes saved.")
                                st.rerun()

                with st.popover("Delete"):
                    st.write(f"Delete **{item['title']}** permanently?")
                    if st.button("Confirm delete", key=f"delete_{item['id']}", type="primary"):
                        delete_item(item["id"])
                        st.rerun()
        return

    if page == "📸 Memories":
        memories = [item for item in items if item["status"] == "Completed"]
        st.title("Memories")
        st.caption("The things you made happen, and what you want to remember about them.")
        if not memories:
            st.info("Completed experiences will appear here.")
            st.button("Explore your bucket", on_click=navigate_to, args=("🪣 My Bucket",))
            return
        for item in memories:
            with st.container(border=True):
                st.subheader(item["title"])
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
            st.button("Add your first experience", type="primary", on_click=navigate_to, args=("➕ Add Experience",))
        else:
            for item in items[:5]:
                with st.container(border=True):
                    st.markdown(f"**{item['title']}**")
                    st.caption(f"{item['category']}  ·  {item['status']}  ·  {item['priority']} priority")

    with right:
        st.subheader("Your next step")
        st.write("A good list starts with one thing you would be glad you did.")
        st.button("Add an experience", type="primary", use_container_width=True,
                  on_click=navigate_to, args=("➕ Add Experience",))
        if completed:
            st.write(f"You have **{completed}** experience{'s' if completed != 1 else ''} to look back on.")
            st.button("Open memories", use_container_width=True,
                      on_click=navigate_to, args=("📸 Memories",))

if __name__ == "__main__":
    main()
