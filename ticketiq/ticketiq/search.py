"""Semantic search page."""
import reflex as rx
from .state import TicketState
from .card import ticket_card
from .ui import (
    error_banner, empty_state,
    ACCENT, ACCENT_BG, BORDER, MUTED, TEXT, SURFACE, SANS, RADIUS,
)


def search_page() -> rx.Component:
    can_search = (TicketState.query != "") & ~TicketState.search_loading

    return rx.box(
        # ── header ───────────────────────────────────────────────────────
        rx.vstack(
            rx.heading(
                "Search", size="6", weight="bold",
                letter_spacing="-0.02em", color=TEXT,
            ),
            rx.text(
                "Semantic search across all classified tickets.",
                font_size="13px", color=MUTED,
            ),
            align="start", gap="6px", margin_bottom="28px",
        ),

        # ── search bar ────────────────────────────────────────────────────
        rx.hstack(
            rx.icon("search", size=15, color=MUTED, flex_shrink="0"),
            rx.input(
                value=TicketState.query,
                on_change=TicketState.set_query,
                on_key_down=lambda k: rx.cond(
                    k == "Enter", TicketState.run_search(), rx.noop()
                ),
                placeholder="Search by symptom, system, or error…",
                font_size="13px",
                font_family=SANS,
                background="transparent",
                border="none",
                outline="none",
                color=TEXT,
                flex="1",
                _placeholder={"color": MUTED},
            ),
            rx.cond(
                TicketState.query != "",
                rx.icon_button(
                    rx.icon("x", size=13),
                    on_click=TicketState.clear_search,
                    background="transparent",
                    border="none",
                    color=MUTED,
                    cursor="pointer",
                    size="1",
                    variant="ghost",
                ),
            ),
            rx.button(
                rx.cond(
                    TicketState.search_loading,
                    rx.spinner(size="1"),
                    rx.icon("search", size=13),
                ),
                rx.text("Search", font_size="12px"),
                on_click=TicketState.run_search,
                disabled=~can_search,
                background=rx.cond(can_search, ACCENT, BORDER),
                color=rx.cond(can_search, "#0a0a0b", MUTED),
                border="none",
                border_radius="4px",
                padding="8px 16px",
                font_weight="600",
                font_family=SANS,
                cursor=rx.cond(can_search, "pointer", "not-allowed"),
                display="flex", align_items="center", gap="6px",
                transition="all 0.15s",
            ),
            background=SURFACE,
            border=f"1px solid {BORDER}",
            border_radius=RADIUS,
            padding="4px 4px 4px 14px",
            align="center",
            gap="8px",
            width="100%",
            margin_bottom="28px",
            _focus_within={"border_color": ACCENT, "box_shadow": f"0 0 0 2px {ACCENT_BG}"},
            transition="border-color 0.2s, box-shadow 0.2s",
        ),

        # ── error ─────────────────────────────────────────────────────────
        error_banner(TicketState.search_error),

        # ── results ───────────────────────────────────────────────────────
        rx.cond(
            TicketState.search_loading,
            rx.center(rx.spinner(size="3", color=ACCENT), padding="64px"),
            rx.cond(
                TicketState.searched & ~TicketState.has_search_results,
                empty_state(
                    "search-x",
                    "No results",
                    "No tickets matched your query. Try different keywords.",
                ),
                rx.cond(
                    TicketState.has_search_results,
                    rx.vstack(
                        rx.text(
                            TicketState.search_results.length().to_string()
                            + ' results for "'
                            + TicketState.query + '"',
                            font_size="12px", color=MUTED, margin_bottom="14px",
                        ),
                        rx.foreach(
                            TicketState.search_results,
                            lambda t: ticket_card(t, show_similar=False),
                        ),
                        gap="12px", width="100%", align="start",
                    ),
                ),
            ),
        ),

        max_width="760px", margin="0 auto",
        padding="40px 24px", width="100%",
    )