import reflex as rx
from ..state import TrendsState
from ..ui import ACCENT, BORDER, MUTED, TEXT, SURFACE, RADIUS, MONO, section_label

def accelerating_table() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("CATEGORIES WITH ACCELERATING VOLUME"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Label"),
                        rx.table.column_header_cell("This Week"),
                        rx.table.column_header_cell("Last Week"),
                        rx.table.column_header_cell("Change"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        TrendsState.accelerating,
                        lambda item: rx.table.row(
                            rx.table.cell(item["label"]),
                            rx.table.cell(item["this_week"].to_string()),
                            rx.table.cell(item["last_week"].to_string()),
                            rx.table.cell(
                                rx.cond(
                                    item["change_pct"].to(float) > 0,
                                    "+" + item["change_pct"].to_string() + "%",
                                    item["change_pct"].to_string() + "%"
                                ),
                                style=rx.cond(
                                    item["change_pct"].to(float) > 0,
                                    {"color": "red"},
                                    {"color": "green"}
                                )
                            ),
                        ),
                    ),
                ),
                width="100%",
            ),
            width="100%",
        ),
        width="100%",
    )

def priority_timeline_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("PRIORITY DISTRIBUTION (HOURLY, 7 DAYS)"),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="count",
                    name="Priority",
                ),
                rx.recharts.x_axis(data_key="timestamp"),
                rx.recharts.y_axis(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=TrendsState.priority_timeline,
                width="100%",
                height=300,
            ),
            width="100%",
        ),
        width="100%",
    )

def fallback_rate_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("LLM FALLBACK RATE (DAILY, 14 DAYS)"),
            rx.recharts.line_chart(
                rx.recharts.line(data_key="rate", name="Fallback Rate", stroke="#ef4444"),
                rx.recharts.x_axis(data_key="date"),
                rx.recharts.y_axis(tick_formatter=".0%"),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                data=TrendsState.fallback_timeline,
                width="100%",
                height=250,
            ),
            width="100%",
        ),
        width="100%",
    )

def department_load_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("TICKETS PER DEPARTMENT (DAILY, 14 DAYS)"),
            rx.recharts.line_chart(
                rx.recharts.line(data_key="count", name="Tickets"),
                rx.recharts.x_axis(data_key="date"),
                rx.recharts.y_axis(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                # Need to group by department – we'll transform data in a computed var
                data=TrendsState.department_load,
                width="100%",
                height=300,
            ),
            width="100%",
        ),
        width="100%",
    )

def new_labels_section() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("NEW THIS WEEK"),
            rx.foreach(
                TrendsState.new_labels,
                lambda item: rx.hstack(
                    rx.text(item["label"], font_size="12px", color=TEXT),
                    rx.text(
                        rx.cond(
                            item["status"] == "new",
                            "NEW",
                            "+" + item["this_week"].to_string() + " (last week: " + item["last_week"].to_string() + ")"
                        ),
                        font_size="11px", color=MUTED
                    ),
                    gap="8px", margin_bottom="6px",
                ),
            ),
            width="100%",
        ),
        width="100%",
    )

def trends_page() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading("Trends & Intelligence", size="6", weight="bold", color=TEXT),
            rx.spacer(),
            rx.button(
                rx.cond(TrendsState.loading, rx.spinner(size="1"), rx.icon("refresh-cw", size=13)),
                rx.text("Refresh", font_size="12px"),
                on_click=TrendsState.load_all,
                background=SURFACE,
                border=f"1px solid {BORDER}",
                border_radius=RADIUS,
                padding="8px 14px",
                color=MUTED, cursor="pointer",
                display="flex", align_items="center", gap="6px",
            ),
            align="center", margin_bottom="28px",
        ),

        rx.cond(
            TrendsState.error != "",
            rx.callout(TrendsState.error, color_scheme="red", width="100%"),
        ),

        rx.vstack(
            accelerating_table(),
            priority_timeline_chart(),
            department_load_chart(),
            fallback_rate_chart(),
            new_labels_section(),
            gap="16px", width="100%",
        ),

        max_width="960px", margin="0 auto",
        padding="40px 24px", width="100%",
        on_mount=TrendsState.load_all,
    )