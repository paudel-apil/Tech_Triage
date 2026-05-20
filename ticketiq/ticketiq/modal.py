"""Ticket detail modal — slide-in panel on card click."""
import reflex as rx
from .state import TicketState
from .ui import (
    priority_badge, source_badge, confidence_bar, section_label, mono,
    ACCENT, ACCENT_BG, BORDER, BORDER_HI, HIGH, HIGH_BG,
    LOW_C, MUTED, TEXT, SURFACE, SANS, MONO, RADIUS,
)

OVERLAY = "rgba(0,0,0,0.65)"
PANEL_W = "520px"


def _similar_row(s: dict) -> rx.Component:
    pct = (s["similarity"].to(float) * 100).to(int)
    color = rx.cond(
        s["similarity"].to(float) >= 0.80, LOW_C,
        rx.cond(s["similarity"].to(float) >= 0.60, ACCENT, MUTED),
    )
    return rx.hstack(
        rx.box(
            mono(pct.to_string() + "%", font_size="11px", color=color),
            min_width="38px",
        ),
        rx.text(
            s["description"],
            font_size="12px", color=MUTED, line_height="1.55",
            no_of_lines=2, flex="1",
        ),
        align="start", gap="10px", width="100%",
        padding="8px 0",
        border_bottom=f"1px solid {BORDER}",
    )


def ticket_modal() -> rx.Component:
    t = TicketState.modal_ticket
    sim_list = t["similar_tickets"].to(list[dict])

    return rx.cond(
        TicketState.modal_open,
        rx.box(
            # ── backdrop ────────────────────────────────────────────────
            rx.box(
                on_click=TicketState.close_modal,
                position="fixed", top="0", left="0",
                width="100vw", height="100vh",
                background=OVERLAY,
                z_index="40",
            ),

            # ── panel ────────────────────────────────────────────────────
            rx.box(
                # header
                rx.hstack(
                    rx.vstack(
                        mono(
                            "#" + t["id"].to_string(),
                            font_size="11px", color=MUTED,
                        ),
                        rx.text(
                            "Ticket Detail",
                            font_size="15px", font_weight="600", color=TEXT,
                        ),
                        gap="2px", align="start",
                    ),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("x", size=16),
                        on_click=TicketState.close_modal,
                        background="transparent",
                        border=f"1px solid {BORDER}",
                        border_radius="6px",
                        color=MUTED,
                        cursor="pointer",
                        size="2",
                        variant="ghost",
                    ),
                    align="center",
                    padding="20px 24px",
                    border_bottom=f"1px solid {BORDER}",
                ),

                # scrollable body
                rx.box(
                    # description
                    rx.box(
                        section_label("DESCRIPTION"),
                        rx.text(
                            t["description"],
                            font_size="13px", line_height="1.7",
                            color=TEXT, white_space="pre-wrap",
                        ),
                        margin_bottom="20px",
                    ),

                    # label + department
                    rx.box(
                        section_label("CATEGORY"),
                        mono(
                            t["label"],
                            font_size="12px", color=ACCENT,
                            letter_spacing="0.02em",
                        ),
                        rx.cond(
                            t["department"] != "Uncategorised",
                            rx.text(
                                t["department"],
                                font_size="12px", color=MUTED, margin_top="2px",
                            ),
                        ),
                        margin_bottom="20px",
                    ),

                    # badges + confidence
                    rx.hstack(
                        priority_badge(t["priority"]),
                        source_badge(t["source"]),
                        gap="8px",
                        margin_bottom="12px",
                    ),
                    rx.box(
                        rx.text("Confidence", font_size="11px", color=MUTED, margin_bottom="4px"),
                        confidence_bar(t["confidence"]),
                        margin_bottom="20px",
                    ),

                    # solution
                    rx.box(
                        rx.hstack(
                            section_label("SOLUTION"),
                            rx.spacer(),
                            rx.button(
                                rx.icon("copy", size=12),
                                rx.text("Copy", font_size="11px"),
                                on_click=rx.set_clipboard(t["solution"]),
                                background=ACCENT_BG,
                                border=f"1px solid {ACCENT}",
                                border_radius="4px",
                                padding="3px 10px",
                                color=ACCENT,
                                cursor="pointer",
                                font_family=SANS,
                                display="flex",
                                align_items="center",
                                gap="4px",
                                margin_bottom="10px",
                                _hover={"opacity": "0.8"},
                            ),
                            align="center",
                        ),
                        rx.box(
                            rx.text(
                                t["solution"],
                                font_size="13px", line_height="1.75",
                                color=TEXT, white_space="pre-wrap",
                            ),
                            padding="14px 16px",
                            background="rgba(245,166,35,0.04)",
                            border=f"1px solid {BORDER}",
                            border_left=f"3px solid {ACCENT}",
                            border_radius="4px",
                        ),
                        margin_bottom="20px",
                    ),

                    # similar tickets
                    rx.cond(
                        sim_list.length() > 0,
                        rx.box(
                            section_label("SIMILAR TICKETS"),
                            rx.foreach(sim_list, _similar_row),
                        ),
                    ),

                    padding="20px 24px",
                    overflow_y="auto",
                    flex="1",
                ),

                # panel shell
                position="fixed",
                top="0", right="0",
                width=PANEL_W,
                max_width="95vw",
                height="100vh",
                background=SURFACE,
                border_left=f"1px solid {BORDER_HI}",
                z_index="50",
                display="flex",
                flex_direction="column",
                box_shadow="-8px 0 32px rgba(0,0,0,0.4)",
            ),
        ),
    )