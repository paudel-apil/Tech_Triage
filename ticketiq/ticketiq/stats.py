"""Stats dashboard page."""
import reflex as rx
from .state import TicketState
from .ui import (
    mono, section_label, empty_state,
    ACCENT, ACCENT_BG, BORDER, MUTED, TEXT, SURFACE,
    HIGH, HIGH_BG, LOW_C, LOW_BG, MED, MED_BG, SANS, MONO, RADIUS,
)

# PIE_COLORS – using CSS variables works fine here because they're passed directly as fill values
PIE_COLORS = [ACCENT, "#60a5fa", LOW_C, "#a78bfa", HIGH, "#f472b6", "#34d399"]

# ── Stat card (unchanged) ────────────────────────────────────────────────────

def stat_card(label: str, value: rx.Var, sub: str = "") -> rx.Component:
    return rx.box(
        rx.text(label, font_size="11px", color=MUTED,
                font_family=MONO, letter_spacing="0.06em", margin_bottom="6px"),
        rx.text(value, font_size="28px", font_weight="700",
                color=TEXT, letter_spacing="-0.02em", line_height="1"),
        rx.cond(sub != "", rx.text(sub, font_size="11px", color=MUTED, margin_top="4px")),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="20px",
        flex="1",
        min_width="140px",
    )


# ── Priority donut (unchanged) ──────────────────────────────────────────────

def priority_donut() -> rx.Component:
    stats = TicketState.stats
    pb = stats["priority_breakdown"].to(dict)

    high_count   = pb["high"].to(int)
    med_count    = pb["medium"].to(int)
    low_count    = pb["low"].to(int)

    data = [
        {"name": "High",   "value": high_count,   "fill": HIGH},
        {"name": "Medium", "value": med_count,     "fill": MED},
        {"name": "Low",    "value": low_count,     "fill": LOW_C},
    ]

    return rx.box(
        section_label("PRIORITY BREAKDOWN"),
        rx.recharts.pie_chart(
            rx.recharts.pie(
                rx.recharts.label_list(
                    data_key="name",
                    position="outside",
                    style={"fill": MUTED, "fontSize": "11px", "fontFamily": MONO},
                ),
                data=data,
                data_key="value",
                cx="50%", cy="50%",
                inner_radius="55%",
                outer_radius="80%",
                padding_angle=3,
            ),
            rx.recharts.legend(
                icon_type="circle",
                icon_size=8,
                wrapper_style={"fontSize": "12px", "color": MUTED, "fontFamily": SANS},
            ),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "6px",
                    "fontSize": "12px",
                    "color": TEXT,
                }
            ),
            width="100%",
            height=220,
        ),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="20px",
        flex="1",
    )


# ── Source donut (unchanged) ────────────────────────────────────────────────

def source_donut() -> rx.Component:
    stats = TicketState.stats
    sb = stats["source_breakdown"].to(dict)

    medoid_count = sb["medoid"].to(int)
    llm_count    = sb["llm_fallback"].to(int)

    data = [
        {"name": "Medoid (KNN)", "value": medoid_count, "fill": ACCENT},
        {"name": "LLM fallback", "value": llm_count,    "fill": "#60a5fa"},
    ]

    return rx.box(
        section_label("CLASSIFICATION SOURCE"),
        rx.recharts.pie_chart(
            rx.recharts.pie(
                data=data,
                data_key="value",
                cx="50%", cy="50%",
                inner_radius="55%",
                outer_radius="80%",
                padding_angle=3,
            ),
            rx.recharts.legend(
                icon_type="circle",
                icon_size=8,
                wrapper_style={"fontSize": "12px", "color": MUTED, "fontFamily": SANS},
            ),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "6px",
                    "fontSize": "12px",
                    "color": TEXT,
                }
            ),
            width="100%",
            height=220,
        ),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="20px",
        flex="1",
    )


# ── Top labels bar chart – FIXED TICK COLORS ────────────────────────────────

def top_labels_chart() -> rx.Component:
    return rx.box(
        section_label("TOP 5 CATEGORIES"),
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="count",
                fill=rx.cond(rx.color_mode == "dark", "#f59e0b", "#d97706"),
                radius=[0, 4, 4, 0],
            ),
            rx.recharts.x_axis(
                type_="number",
                tick={"fontSize": 10, "fill": rx.cond(rx.color_mode == "dark", "#ccc", "#555"), "fontFamily": MONO},
            ),
            rx.recharts.y_axis(
                data_key="label",
                type_="category",
                tick={"fontSize": 10, "fill": rx.cond(rx.color_mode == "dark", "#ccc", "#555"), "fontFamily": MONO},
                width=200,
            ),
            rx.recharts.cartesian_grid(
                stroke_dasharray="3 3",
                stroke=BORDER,
                horizontal=False,
            ),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "6px",
                    "fontSize": "12px",
                    "color": TEXT,
                },
                cursor={"fill": rx.cond(rx.color_mode == "dark", "rgba(245,158,11,0.06)", "rgba(217,119,6,0.06)")},
            ),
            layout="vertical",
            data=TicketState.stats_top_labels,
            width="100%",
            height=280,
            margin={"top": 8, "right": 16, "left": 0, "bottom": 8},
        ),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="20px",
        width="100%",
    )


# ── Department bar chart – FIXED TICK COLORS ────────────────────────────────

def dept_chart() -> rx.Component:
    return rx.box(
        section_label("TICKETS BY DEPARTMENT"),
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="count",
                fill=rx.cond(rx.color_mode == "dark", "#60a5fa", "#2563eb"),
                radius=[0, 4, 4, 0],
            ),
            rx.recharts.x_axis(
                type_="number",
                tick={"fontSize": 10, "fill": rx.cond(rx.color_mode == "dark", "#ccc", "#555"), "fontFamily": MONO},
            ),
            rx.recharts.y_axis(
                data_key="department",
                type_="category",
                tick={"fontSize": 10, "fill": rx.cond(rx.color_mode == "dark", "#ccc", "#555"), "fontFamily": MONO},
                width=180,
            ),
            rx.recharts.cartesian_grid(
                stroke_dasharray="3 3",
                stroke=BORDER,
                horizontal=False,
            ),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": SURFACE,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "6px",
                    "fontSize": "12px",
                    "color": TEXT,
                },
                cursor={"fill": rx.cond(rx.color_mode == "dark", "rgba(96,165,250,0.06)", "rgba(37,99,235,0.06)")},
            ),
            layout="vertical",
            data=TicketState.stats_department_breakdown,
            width="100%",
            height=400,
            margin={"top": 8, "right": 16, "left": 0, "bottom": 8},
        ),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="20px",
        width="100%",
    )


def uncategorised_card() -> rx.Component:
    return rx.box(
        rx.text("Uncategorised", font_size="12px", color=MUTED),
        rx.text(
            TicketState.uncategorised_count.to_string(),
            font_size="24px",
            font_weight="600",
            color=HIGH,
            font_family=MONO,
        ),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="16px",
        text_align="center",
        min_width="120px",
    )


# ── Stats page (unchanged) ──────────────────────────────────────────────────

def stats_page() -> rx.Component:
    s = TicketState.stats

    return rx.box(
        # header
        rx.hstack(
            rx.vstack(
                rx.heading("Stats", size="6", weight="bold",
                           letter_spacing="-0.02em", color=TEXT),
                rx.text("Live metrics from PostgreSQL.",
                        font_size="13px", color=MUTED),
                align="start", gap="4px",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=13),
                rx.text("Refresh", font_size="12px"),
                on_click=TicketState.load_stats,
                background=SURFACE,
                border=f"1px solid {BORDER}",
                border_radius=RADIUS,
                padding="8px 14px",
                color=MUTED, cursor="pointer",
                font_family=SANS,
                display="flex", align_items="center", gap="6px",
            ),
            align="center", margin_bottom="28px",
        ),

        # body
        rx.cond(
            TicketState.stats_loading,
            rx.center(rx.spinner(size="3", color=ACCENT), padding="64px"),
            rx.cond(
                TicketState.stats_error != "",
                rx.box(
                    rx.text(TicketState.stats_error, font_size="13px", color=HIGH),
                    padding="12px 16px", background=HIGH_BG,
                    border=f"1px solid {HIGH}", border_radius=RADIUS,
                ),
                rx.cond(
                    TicketState.stats != {},
                    rx.vstack(
                        # ── top stat cards ────────────────────────────────
                        rx.hstack(
                            stat_card(
                                "TOTAL TICKETS",
                                s["total"].to_string(),
                            ),
                            stat_card(
                                "AVG CONFIDENCE",
                                TicketState.avg_confidence_pct,
                            ),
                            stat_card(
                                "MEDOID MATCHES",
                                TicketState.source_medoid_count.to_string(),
                                "classified by KNN",
                            ),
                            stat_card(
                                "LLM FALLBACKS",
                                TicketState.source_llm_count.to_string(),
                                "classified by Groq",
                            ),
                            gap="12px", flex_wrap="wrap", width="100%",
                        ),

                        # ── donuts row ────────────────────────────────────
                        rx.hstack(
                            priority_donut(),
                            source_donut(),
                            gap="12px", width="100%", flex_wrap="wrap",
                        ),

                        # ── bar charts ────────────────────────────────────
                        top_labels_chart(),
                        dept_chart(),
                        uncategorised_card(),

                        gap="12px", width="100%", align="start",
                    ),
                    empty_state(
                        "bar-chart-2",
                        "No data yet",
                        "Submit some tickets and stats will appear here.",
                    ),
                ),
            ),
        ),

        max_width="900px", margin="0 auto",
        padding="40px 24px", width="100%",
        on_mount=TicketState.load_stats,
    )