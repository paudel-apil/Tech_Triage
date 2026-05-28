import reflex as rx
from ..state import StreamState
from ..ui import (
    ACCENT, BORDER, MUTED, TEXT, SURFACE, SANS, RADIUS, LOW_C,
)

def stream_page() -> rx.Component:
    return rx.box(
        # Live indicator
        rx.hstack(
            rx.box(
                width="8px", height="8px", border_radius="50%", background=LOW_C,
                style={"animation": "pulse 1.5s infinite"},
            ),
            rx.text("LIVE", font_size="24px", font_weight="bold", color=ACCENT),
            rx.text("●", font_size="14px", color=LOW_C),
            rx.text(
                StreamState.live_tickets.length().to_string() + " tickets",
                font_size="14px", color=MUTED,
            ),
            gap="8px", align="center", margin_bottom="24px",
        ),

        # Feed – rendered as HTML (no foreach)
        rx.vstack(
            rx.cond(
                StreamState.live_tickets.length() == 0,
                rx.text("Waiting for tickets…", font_size="14px", color=MUTED, padding="40px"),
                rx.html(StreamState.feed_html),
            ),
            width="100%",
        ),

        # Animations
        rx.el.style("""
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50%      { opacity: 0.4; }
            }
        """),

        max_width="900px", margin="0 auto",
        padding="30px 24px", width="100%",
        on_mount=StreamState.start_stream,
        on_unmount=StreamState.stop_stream,
    )