"""Ticket card component."""
import reflex as rx
from .state import TicketState
from .ui import (
    priority_badge, source_badge, confidence_bar, section_label,
    mono, ACCENT, ACCENT_BG, BORDER, BORDER_HI,
    MUTED, TEXT, SURFACE, SANS, MONO, RADIUS,
)


def _similar_row(s: dict) -> rx.Component:
    pct = (s["similarity"].to(float) * 100).to(int)
    return rx.hstack(
        mono(pct.to_string() + "%", font_size="11px", color=ACCENT, min_width="34px"),
        rx.text(
            s["description"],
            font_size="12px", color=MUTED, line_height="1.5",
            no_of_lines=2, flex="1",
        ),
        align="start", gap="10px", width="100%", margin_bottom="6px",
    )


def ticket_card(ticket: dict, show_similar: bool = True) -> rx.Component:
    tid = ticket["id"]
    is_open = TicketState.expanded.contains(tid)

    return rx.box(
        # ── id + description ─────────────────────────────────────────────
        rx.hstack(
            mono(
                "#" + tid.to_string(),
                font_size="11px", color=MUTED,
                min_width="34px", padding_top="2px", flex_shrink="0",
            ),
            rx.text(
                ticket["description"],
                font_size="13px", line_height="1.6", color=TEXT,
                no_of_lines=3, flex="1",
            ),
            align="start", gap="12px", margin_bottom="14px",
        ),

        # ── label / department ───────────────────────────────────────────
        rx.box(
            mono(
                ticket["label"],
                font_size="11px", color=ACCENT,
                letter_spacing="0.02em", no_of_lines=1,
            ),
            rx.cond(
                ticket["department"] != "Uncategorised",
                rx.text(ticket["department"], font_size="11px", color=MUTED),
            ),
            margin_bottom="12px",
        ),

        # ── badges + timestamp ───────────────────────────────────────────
        rx.hstack(
            priority_badge(ticket["priority"]),
            source_badge(ticket["source"]),
            rx.spacer(),
            rx.hstack(
                rx.icon("clock", size=10, color=MUTED),
                mono(ticket["created_at"], font_size="11px", color=MUTED),
                gap="4px", align="center",
            ),
            align="center", gap="8px", flex_wrap="wrap", margin_bottom="12px",
        ),

        # ── confidence ───────────────────────────────────────────────────
        rx.box(
            rx.text("Confidence", font_size="11px", color=MUTED, margin_bottom="4px"),
            confidence_bar(ticket["confidence"].to(float)),
            margin_bottom="14px",
        ),

        # ── solution toggle ───────────────────────────────────────────────
        rx.box(
            rx.button(
                rx.icon(rx.cond(is_open, "chevron-up", "chevron-down"), size=12),
                rx.icon("zap", size=12),
                rx.text("Solution", font_size="12px", font_family=SANS),
                on_click=TicketState.toggle_expanded(tid),
                display="flex", align_items="center", gap="5px",
                background=rx.cond(is_open, ACCENT_BG, "transparent"),
                color=rx.cond(is_open, ACCENT, MUTED),
                border=rx.cond(is_open, f"1px solid {ACCENT}", f"1px solid {BORDER}"),
                border_radius="4px", padding="5px 10px",
                cursor="pointer", font_family=SANS,
                transition="all 0.15s",
            ),
            rx.cond(
                is_open,
                rx.box(
                    rx.text(
                        ticket["solution"],
                        font_size="13px", line_height="1.75",
                        color=TEXT, white_space="pre-wrap",
                    ),
                    margin_top="10px", padding="14px 16px",
                    background="rgba(245,166,35,0.04)",
                    border=f"1px solid {BORDER}",
                    border_left=f"3px solid {ACCENT}",
                    border_radius="4px",
                ),
            ),
            margin_bottom=rx.cond(
                show_similar & TicketState.has_similar_tickets, "14px", "0"
            ),
        ),

        # ── similar tickets ───────────────────────────────────────────────
        rx.cond(
            show_similar & TicketState.has_similar_tickets,
            rx.box(
                rx.divider(border_color=BORDER, margin_bottom="12px"),
                section_label("SIMILAR TICKETS"),
                rx.foreach(
                    TicketState.result_similar_tickets,
                    _similar_row,
                ),
            ),
        ),

        # ── card shell ────────────────────────────────────────────────────
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="20px",
        width="100%",
        _hover={"border_color": BORDER_HI},
        transition="border-color 0.2s",
    )