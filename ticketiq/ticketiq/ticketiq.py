"""TicketIQ - ML-powered support triage frontend."""

import reflex as rx

from rxconfig import config
from ticketiq.state import TicketState
from ticketiq.submit import submit_page
from ticketiq.tickets_list import tickets_page
from ticketiq.search import search_page
from ticketiq.stats import stats_page
from .pages.trends import trends_page
from .pages.playground import playground_page
from .pages.stream_page import stream_page
from ticketiq.ui import (
    BG, SURFACE, BORDER, BORDER_HI, ACCENT, ACCENT_BG,
    MUTED, TEXT, SANS, MONO, RADIUS,
)


app = rx.App(
    style={"font_family": "Inter, sans-serif"},
    theme=rx.theme(appearance="light", accent_color="blue"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@300;400;500;600&display=swap",
    ],
)

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=JetBrains+Mono:wght@400;500;700"
    "&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;"
    "0,9..40,500;0,9..40,600&display=swap"
)

NAV = [
    ("submit",  "ticket-check", "Submit"),
    ("tickets", "list-filter",  "Tickets"),
    ("search",  "search",       "Search"),
    ("stats",   "bar-chart-2",  "Stats"),
    ("trends", "trending-up", "Trends"),
    ("playground", "flask-conical", "Playground"),
    ("stream", "radio", "Live"),

]


# ── Sidebar ───────────────────────────────────────────────────────────────────

def nav_item(tab: str, icon_name: str, label: str) -> rx.Component:
    active = TicketState.active_tab == tab
    return rx.button(
        rx.icon(icon_name, size=15),
        rx.text(label, font_size="13px"),
        on_click=TicketState.go_to(tab),
        width="100%",
        display="flex",
        align_items="center",
        justify_content="flex-start",
        gap="10px",
        padding="9px 12px",
        border_radius="6px",
        border="none",
        font_weight=rx.cond(active, "600", "400"),
        color=rx.cond(active, ACCENT, MUTED),
        background=rx.cond(active, ACCENT_BG, "transparent"),
        cursor="pointer",
        font_family=SANS,
        margin_bottom="2px",
        transition="all 0.15s",
        _hover={
            "background": rx.cond(active, ACCENT_BG, "rgba(255,255,255,0.04)"),
            "color": rx.cond(active, ACCENT, TEXT),
        },
    )


def sidebar() -> rx.Component:
    return rx.box(
        # logo
        rx.hstack(
            rx.box(
                rx.icon("cpu", size=16, color=TEXT),
                width="30px", height="30px",
                background=ACCENT, border_radius="6px",
                display="flex", align_items="center", justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text("TicketIQ", font_size="13px", font_weight="600",
                        line_height="1.2", color=TEXT),
                rx.text("ML-powered triage", font_size="10px", color=MUTED,
                        font_family=MONO, line_height="1.2"),
                gap="0", align="start",
            ),
            align="center", gap="10px",
            padding="0 20px 28px",
        ),

        # nav
        rx.box(
            *[nav_item(tab, icon, label) for tab, icon, label in NAV],
            flex="1",
            padding="0 10px",
        ),

        # footer (with toggle button)
        rx.box(
            rx.icon_button(
                rx.cond(rx.color_mode == "dark", rx.icon("sun", size=16), rx.icon("moon", size=16)),
                on_click=rx.toggle_color_mode,
                background="transparent",
                border=f"1px solid {BORDER}",
                border_radius="6px",
                color=MUTED,
                cursor="pointer",
                size="2",
                variant="ghost",
                margin_bottom="10px",
            ),
            rx.text(
                "BGE-M3 · HDBSCAN · XGBoost · Groq",
                font_size="10px", color=MUTED, font_family=MONO,
            ),
            padding="16px 20px",
            border_top=f"1px solid {BORDER}",
        ),

        # shell
        width="220px",
        flex_shrink="0",
        background=SURFACE,
        border_right=f"1px solid {BORDER}",
        display="flex",
        flex_direction="column",
        padding_top="24px",
        height="100vh",
        position="sticky",
        top="0",
        overflow="hidden",
    )


# ── Page router ───────────────────────────────────────────────────────────────

def page_body() -> rx.Component:
    return rx.match(
        TicketState.active_tab,
        ("submit",  submit_page()),
        ("tickets", tickets_page()),
        ("search",  search_page()),
        ("stats", stats_page()),
        ("trends", trends_page()),
        ("playground", playground_page()),
        ("stream", stream_page()),
        submit_page(),
    )


# ── Root layout ───────────────────────────────────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        # Inject Google Fonts
        rx.script(src=GOOGLE_FONTS),

        # Embedded theme styles (dark / light + chart colours)
        rx.el.style("""
            html[data-theme='dark'] {
                --bg: #1a1a20;
                --surface: #242430;
                --border: #343440;
                --border-hi: #4a4a5a;
                --text: #e0e0e8;
                --muted: #7a7a90;
                --accent: #818cf8;
                --accent-bg: rgba(129,140,248,0.12);
                --high: #f87171;
                --high-bg: rgba(248,113,113,0.12);
                --med: #fbbf24;
                --med-bg: rgba(251,191,36,0.12);
                --low: #34d399;
                --low-bg: rgba(52,211,153,0.12);
                --chart-blue: #60a5fa;
                --chart-orange: #f59e0b;
                --chart-purple: #a78bfa;
                --chart-pink: #f472b6;
                --chart-green: #34d399;
                --chart-blue-bg: rgba(96,165,250,0.06);
                --chart-orange-bg: rgba(245,158,11,0.06);
            }
            html[data-theme='light'] {
                --bg: #f8f9fa;
                --surface: #ffffff;
                --border: #dee2e6;
                --border-hi: #adb5bd;
                --text: #212529;
                --muted: #6c757d;
                --accent: #0d6efd;
                --accent-bg: rgba(13,110,253,0.10);
                --high: #dc3545;
                --high-bg: rgba(220,53,69,0.08);
                --med: #fd7e14;
                --med-bg: rgba(253,126,20,0.08);
                --low: #198754;
                --low-bg: rgba(25,135,84,0.08);
                --chart-blue: #60a5fa;
                --chart-orange: #f59e0b;
                --chart-purple: #a78bfa;
                --chart-pink: #f472b6;
                --chart-green: #34d399;
                --chart-blue-bg: rgba(96,165,250,0.06);
                --chart-orange-bg: rgba(245,158,11,0.06);
            }
        """),

        # Sidebar + main content
        rx.hstack(
            sidebar(),
            rx.box(
                page_body(),
                flex="1",
                overflow_y="auto",
                min_height="100vh",
            ),
            align="start",
            gap="0",
            width="100%",
        ),

        # Global styles
        font_family=SANS,
        background=BG,
        color=TEXT,
        min_height="100vh",
        style={
            "background_image": (
                "radial-gradient(ellipse 60% 40% at 80% 0%, "
                "rgba(245,166,35,0.04) 0%, transparent 60%), "
                "radial-gradient(ellipse 40% 30% at 0% 80%, "
                "rgba(245,166,35,0.03) 0%, transparent 50%)"
            ),
        },
    )
# ── App ───────────────────────────────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(appearance="dark", accent_color="amber"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@300;400;500;600&display=swap",
    ],
    style={
        "body":                      {"margin": "0", "padding": "0"},
        "*":                         {"box_sizing": "border-box"},
        "::-webkit-scrollbar":       {"width": "4px", "height": "4px"},
        "::-webkit-scrollbar-track": {"background": SURFACE},
        "::-webkit-scrollbar-thumb": {"background": BORDER_HI, "border_radius": "2px"},
        "::selection":               {"background": ACCENT_BG, "color": ACCENT},
    },
)

app.add_page(index, route="/", title="TicketIQ – ML Triage")