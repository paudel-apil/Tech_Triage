"""Paginated list of classified tickets."""
import reflex as rx
from .state import TicketState
from .card import ticket_card
from .ui import (
    error_banner, empty_state, ghost_btn,
    ACCENT, BORDER, MUTED, TEXT, SURFACE, SANS, MONO, RADIUS,
)


def _pagination() -> rx.Component:
    return rx.cond(
        TicketState.total_pages > 1,
        rx.hstack(
            rx.button(
                rx.icon("chevron-left", size=14),
                rx.text("Prev", font_size="12px"),
                on_click=TicketState.prev_page,
                disabled=TicketState.on_first_page,
                background=SURFACE,
                border=f"1px solid {BORDER}",
                border_radius=RADIUS,
                padding="7px 14px",
                color=rx.cond(TicketState.on_first_page, MUTED, TEXT),
                opacity=rx.cond(TicketState.on_first_page, "0.4", "1"),
                cursor=rx.cond(TicketState.on_first_page, "not-allowed", "pointer"),
                font_family=SANS,
                display="flex", align_items="center", gap="4px",
            ),
            rx.text(
                (TicketState.page + 1).to_string() + " / " + TicketState.total_pages.to_string(),
                font_family=MONO, font_size="12px", color=MUTED,
            ),
            rx.button(
                rx.text("Next", font_size="12px"),
                rx.icon("chevron-right", size=14),
                on_click=TicketState.next_page,
                disabled=TicketState.on_last_page,
                background=SURFACE,
                border=f"1px solid {BORDER}",
                border_radius=RADIUS,
                padding="7px 14px",
                color=rx.cond(TicketState.on_last_page, MUTED, TEXT),
                opacity=rx.cond(TicketState.on_last_page, "0.4", "1"),
                cursor=rx.cond(TicketState.on_last_page, "not-allowed", "pointer"),
                font_family=SANS,
                display="flex", align_items="center", gap="4px",
            ),
            justify="center", align="center", gap="12px", margin_top="28px",
        ),
    )


def tickets_page() -> rx.Component:
    return rx.box(
        # ── header ───────────────────────────────────────────────────────
        rx.hstack(
            rx.vstack(
                rx.heading(
                    "Tickets", size="6", weight="bold",
                    letter_spacing="-0.02em", color=TEXT,
                ),
                rx.text(
                    TicketState.total.to_string() + " classified tickets",
                    font_size="13px", color=MUTED,
                ),
                align="start", gap="4px",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=13),
                rx.text("Refresh", font_size="12px"),
                on_click=TicketState.load_tickets,
                background=SURFACE,
                border=f"1px solid {BORDER}",
                border_radius=RADIUS,
                padding="8px 14px",
                color=MUTED,
                cursor="pointer",
                font_family=SANS,
                display="flex", align_items="center", gap="6px",
            ),
            align="center", margin_bottom="28px",
        ),

        # ── body ─────────────────────────────────────────────────────────
        rx.cond(
            TicketState.list_loading,
            rx.center(rx.spinner(size="3", color=ACCENT), padding="64px"),
            rx.cond(
                TicketState.list_error != "",
                error_banner(TicketState.list_error),
                rx.cond(
                    TicketState.tickets.length() == 0,
                    empty_state(
                        "inbox",
                        "No tickets yet",
                        "Submit your first ticket and it will appear here.",
                    ),
                    rx.vstack(
                        rx.foreach(
                            TicketState.tickets,
                            lambda t: ticket_card(t, show_similar=False),
                        ),
                        gap="12px", width="100%",
                    ),
                ),
            ),
        ),

        _pagination(),

        max_width="760px", margin="0 auto",
        padding="40px 24px", width="100%",
        on_mount=TicketState.load_tickets,
    )