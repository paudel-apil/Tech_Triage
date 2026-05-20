"""Submit & classify a new ticket."""
import reflex as rx
from .state import TicketState
from .card import ticket_card
from .ui import (
    error_banner, section_label,
    ACCENT, ACCENT_BG, BORDER, BORDER_HI, MUTED, TEXT, SURFACE, SANS, MONO, RADIUS, LOW_C, HIGH
)


def _threshold_slider() -> rx.Component:
    """Slider that controls the medoid similarity threshold."""
    # compare the float value, not a list
    color = rx.cond(
        TicketState.sim_threshold >= 0.75, LOW_C,
        rx.cond(TicketState.sim_threshold >= 0.50, ACCENT, HIGH),
    )
    label = rx.cond(
        TicketState.sim_threshold >= 0.75,
        "Strict — fewer LLM fallbacks",
        rx.cond(TicketState.sim_threshold >= 0.50, "Balanced", "Loose — more LLM fallbacks"),
    )

    return rx.box(
        rx.hstack(
            rx.text("Confidence threshold", font_size="12px", color=MUTED),
            rx.spacer(),
            rx.hstack(
                rx.text(
                    TicketState.threshold_pct,
                    font_family=MONO, font_size="13px",
                    font_weight="600", color=color,
                ),
                rx.text("·", font_size="12px", color=MUTED),
                rx.text(label, font_size="12px", color=MUTED),
                gap="6px", align="center",
            ),
            align="center", margin_bottom="8px",
        ),
        rx.slider(
            value=[TicketState.sim_threshold],          # list for Radix slider
            on_change=lambda vals: TicketState.set_sim_threshold(vals[0]),
            min=0.30, max=0.90, step=0.05,
            width="100%",
            color_scheme="amber",
        ),
        rx.hstack(
            rx.text("0.30  More LLM", font_size="10px", color=MUTED, font_family=MONO),
            rx.spacer(),
            rx.text("0.90  More KNN", font_size="10px", color=MUTED, font_family=MONO),
        ),
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="14px 16px",
        margin_bottom="16px",
    )
 

def submit_page() -> rx.Component:
    chars_ok = TicketState.char_count >= 20

    return rx.box(
        # ── header ───────────────────────────────────────────────────────
        rx.vstack(
            rx.heading(
                "Submit Ticket", size="6", weight="bold",
                letter_spacing="-0.02em", color=TEXT,
            ),
            rx.text(
                "Describe the issue in detail. The system classifies, "
                "prioritises, and generates a resolution plan.",
                font_size="13px", color=MUTED, line_height="1.6",
            ),
            align="start", gap="6px", margin_bottom="28px",
        ),

        # ── textarea ─────────────────────────────────────────────────────
        rx.box(
            rx.text_area(
                value=TicketState.description,
                on_change=TicketState.set_description,
                placeholder=(
                    "e.g. The Kafka consumer group for fraud-scoring is lagging by "
                    "2 million messages because the downstream ML service is timing "
                    "out on every request…"
                ),
                rows="7",
                width="100%",
                font_size="13px",
                line_height="1.65",
                font_family=SANS,
                background=SURFACE,
                color=TEXT,
                border=rx.cond(chars_ok, f"1px solid {BORDER_HI}", f"1px solid {BORDER}"),
                border_radius=RADIUS,
                padding="14px 16px",
                resize="vertical",
                outline="none",
                _focus={
                    "border_color": ACCENT,
                    "box_shadow": f"0 0 0 2px {ACCENT_BG}",
                },
                _placeholder={"color": MUTED},
                transition="border-color 0.2s",
            ),
            rx.hstack(
                rx.text(
                    rx.cond(
                        chars_ok,
                        "Ready to submit",
                        (20 - TicketState.char_count).to_string() + " more characters needed",
                    ),
                    font_size="11px",
                    color=rx.cond(chars_ok, "#22c55e", MUTED),
                ),
                rx.spacer(),
                rx.text(
                    TicketState.char_count.to_string(),
                    font_size="11px", color=MUTED, font_family=MONO,
                ),
                width="100%", margin_top="6px",
            ),
            width="100%", margin_bottom="16px",
        ),

        # ── threshold slider ──────────────────────────────────────────────
        _threshold_slider(),

        # ── action buttons ────────────────────────────────────────────────
        rx.hstack(
            rx.button(
                rx.cond(
                    TicketState.submitting,
                    rx.spinner(size="1"),
                    rx.icon("send", size=14),
                ),
                rx.text(
                    rx.cond(TicketState.submitting, "Classifying…", "Classify Ticket"),
                    font_size="13px",
                ),
                on_click=TicketState.submit_ticket,
                disabled=~TicketState.can_submit,
                background=rx.cond(TicketState.can_submit, ACCENT, SURFACE),
                color=rx.cond(TicketState.can_submit, "#0a0a0b", MUTED),
                border=rx.cond(
                    TicketState.can_submit,
                    f"1px solid {ACCENT}",
                    f"1px solid {BORDER}",
                ),
                border_radius=RADIUS,
                padding="10px 20px",
                font_weight="600",
                font_family=SANS,
                cursor=rx.cond(TicketState.can_submit, "pointer", "not-allowed"),
                display="flex", align_items="center", gap="8px",
                transition="all 0.15s",
                _hover={"opacity": rx.cond(TicketState.can_submit, "0.85", "1")},
            ),
            rx.cond(
                TicketState.has_result,
                rx.button(
                    rx.icon("rotate-ccw", size=13),
                    rx.text("Clear", font_size="13px"),
                    on_click=TicketState.clear_submit,
                    background=SURFACE,
                    border=f"1px solid {BORDER}",
                    border_radius=RADIUS,
                    padding="10px 16px",
                    color=MUTED,
                    cursor="pointer",
                    font_family=SANS,
                    display="flex", align_items="center", gap="6px",
                ),
            ),
            gap="8px", align="center",
        ),

        # ── error ─────────────────────────────────────────────────────────
        error_banner(TicketState.submit_error),

        # ── result card ───────────────────────────────────────────────────
        rx.cond(
            TicketState.has_result,
            rx.box(
                section_label("CLASSIFICATION RESULT"),
                ticket_card(TicketState.result, show_similar=True),
                margin_top="28px",
            ),
        ),

        # ── feedback ──────────────────────────────────────────────────────
        rx.cond(
            TicketState.has_result & ~TicketState.feedback_submitted,
            rx.card(
                rx.vstack(
                    rx.text("Was this classification helpful?", font_size="13px", color=MUTED),
                    rx.hstack(
                        rx.button(
                            rx.icon("thumbs-up", size=16),
                            rx.text("Yes", font_size="13px"),
                            on_click=TicketState.thumb_up,
                            color_scheme="green",
                            variant="soft",
                            is_disabled=TicketState.feedback_submitted,
                        ),
                        rx.button(
                            rx.icon("thumbs-down", size=16),
                            rx.text("No", font_size="13px"),
                            on_click=TicketState.thumb_down,
                            color_scheme="red",
                            variant="soft",
                            is_disabled=TicketState.feedback_submitted,
                        ),
                        gap="12px",
                    ),
                    rx.cond(
                        TicketState.show_feedback,
                        rx.vstack(
                            rx.select(
                                TicketState.all_departments,
                                value=TicketState.selected_correction,
                                on_change=TicketState.set_correction,
                                placeholder="Select the correct label",
                                width="100%",
                            ),
                            rx.button(
                                "Submit Correction",
                                on_click=TicketState.submit_feedback,
                                is_disabled=(TicketState.selected_correction == ""),
                            ),
                            gap="8px",
                            width="100%",
                        ),
                    ),
                    gap="8px",
                    width="100%",
                ),
                margin_top="16px",
                width="100%",
            ),
        ),
        rx.cond(
            TicketState.feedback_submitted,
            rx.text("Thank you for your feedback!", font_size="12px", color=LOW_C),
        ),

        # ── page container ────────────────────────────────────────────────
        max_width="720px", margin="0 auto",
        padding="40px 24px", width="100%",
    )