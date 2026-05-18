"""Shared UI atoms."""
import reflex as rx

# ── palette ───────────────────────────────────────────────────────────────────
BG       = "#0a0a0b"
SURFACE  = "#111114"
BORDER   = "#1e1e24"
BORDER_HI= "#2e2e38"
TEXT     = "#e8e8f0"
MUTED    = "#5a5a70"
ACCENT   = "#f5a623"
ACCENT_BG= "rgba(245,166,35,0.10)"

HIGH     = "#ef4444"
HIGH_BG  = "rgba(239,68,68,0.10)"
MED      = "#f5a623"
MED_BG   = "rgba(245,166,35,0.10)"
LOW_C    = "#22c55e"
LOW_BG   = "rgba(34,197,94,0.10)"

MONO = "'JetBrains Mono', monospace"
SANS = "'DM Sans', sans-serif"
RADIUS = "6px"


def mono(text, **props) -> rx.Component:
    return rx.text(text, font_family=MONO, **props)


# ── Priority badge ─────────────────────────────────────────────────────────────

def _pill(label: str, color: str, bg: str) -> rx.Component:
    return rx.text(
        label,
        font_family=MONO, font_size="10px", font_weight="700",
        letter_spacing="0.08em", color=color,
        background=bg, border=f"1px solid {color}",
        padding="2px 8px", border_radius="3px",
    )


def priority_badge(priority: rx.Var) -> rx.Component:
    return rx.match(
        priority,
        ("high",   _pill("HIGH", HIGH,  HIGH_BG)),
        ("medium", _pill("MED",  MED,   MED_BG)),
        ("low",    _pill("LOW",  LOW_C, LOW_BG)),
        _pill("?", MUTED, BORDER),
    )


# ── Source badge ───────────────────────────────────────────────────────────────

def source_badge(source: rx.Var) -> rx.Component:
    return rx.match(
        source,
        ("medoid",       _src("KNN", MUTED,   BORDER)),
        ("llm_fallback", _src("LLM", ACCENT,  ACCENT_BG)),
        ("error",        _src("ERR", HIGH,    HIGH_BG)),
        _src("?", MUTED, BORDER),
    )


def _src(label: str, color: str, bg: str) -> rx.Component:
    return rx.text(
        label,
        font_family=MONO, font_size="10px", font_weight="500",
        color=color, background=bg, border=f"1px solid {color}",
        padding="2px 8px", border_radius="3px",
    )


# ── Confidence bar ─────────────────────────────────────────────────────────────

def confidence_bar(value: rx.Var) -> rx.Component:
    pct = (value.to(float) * 100).to(int)
    return rx.hstack(
        rx.box(
            rx.box(
                width=pct.to_string() + "%",
                height="3px",
                background=ACCENT,
                border_radius="2px",
                transition="width 0.4s ease",
            ),
            width="100%", height="3px",
            background=BORDER, border_radius="2px",
            overflow="hidden",
        ),
        mono(
            pct.to_string() + "%",
            font_size="11px", color=MUTED,
            min_width="36px", text_align="right",
        ),
        width="100%", align="center", gap="8px",
    )


# ── Error banner ───────────────────────────────────────────────────────────────

def error_banner(msg: rx.Var) -> rx.Component:
    return rx.cond(
        msg != "",
        rx.hstack(
            rx.icon("circle-alert", size=14, color=HIGH, flex_shrink="0"),
            rx.text(msg, font_size="13px", color=HIGH, line_height="1.5"),
            padding="12px 16px",
            background=HIGH_BG,
            border=f"1px solid {HIGH}",
            border_radius=RADIUS,
            align="start",
            gap="10px",
            width="100%",
            margin_top="14px",
        ),
    )


# ── Empty state ────────────────────────────────────────────────────────────────

def empty_state(icon: str, title: str, body: str) -> rx.Component:
    return rx.vstack(
        rx.icon(icon, size=40, color=MUTED, opacity="0.35"),
        rx.text(title, font_size="15px", font_weight="600", color=TEXT),
        rx.text(body, font_size="13px", color=MUTED, text_align="center", max_width="340px"),
        padding="64px 24px", align="center", gap="12px", width="100%",
    )


# ── Section label ──────────────────────────────────────────────────────────────

def section_label(text: str) -> rx.Component:
    return rx.text(
        text,
        font_family=MONO, font_size="11px", font_weight="600",
        letter_spacing="0.07em", color=MUTED, margin_bottom="10px",
    )


# ── Ghost button ───────────────────────────────────────────────────────────────

def ghost_btn(*children, on_click=None, disabled: bool = False, **props) -> rx.Component:
    return rx.button(
        *children,
        on_click=on_click,
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        color=MUTED,
        cursor="pointer" if not disabled else "not-allowed",
        opacity="0.45" if disabled else "1",
        font_family=SANS,
        disabled=disabled,
        **props,
    )