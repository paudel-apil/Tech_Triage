import reflex as rx
from ..state import PlaygroundState
from ..ui import (
    mono, ACCENT, BORDER, MUTED, TEXT, SURFACE, SANS, RADIUS, section_label
)

def network_graph_card() -> rx.Component:
    return rx.box(
        # Header + button (outside the iframe)
        rx.vstack(
            section_label("SIMILAR TICKETS NETWORK (DRAGGABLE)"),
            rx.button("Show Network", on_click=PlaygroundState.show_network),
            spacing="3",
            margin_bottom="8px",
        ),
        # Iframe in a dedicated container that forces 100% width
        rx.cond(
            PlaygroundState.network_url != "",
            rx.box(
                rx.html(
                    f'<iframe src="{PlaygroundState.network_url}" '
                    'style="width:100%; height:520px; border:none; display:block;"></iframe>'
                ),
                width="100%",
                # This ensures the box doesn't shrink
                flex="1",
            ),
        ),
        # Card shell
        width="100%",
        background=SURFACE,
        border=f"1px solid {BORDER}",
        border_radius=RADIUS,
        padding="12px",
        margin_top="16px",
    )

def embedding_explorer() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("EMBEDDING EXPLORER"),
            rx.text_area(
                value=PlaygroundState.probe_text,
                on_change=PlaygroundState.set_probe_text,
                placeholder="Paste a ticket description...",
                rows="3",
                width="100%",          # fill card width
            ),
            rx.button("Probe", on_click=PlaygroundState.probe),
            rx.cond(
                PlaygroundState.probe_results.length() > 0,
                network_graph_card(),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Label"),
                            rx.table.column_header_cell("Department"),
                            rx.table.column_header_cell("Similarity"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            PlaygroundState.probe_results,
                            lambda m: rx.table.row(
                                rx.table.cell(m["meta_label"]),
                                rx.table.cell(m["department"]),
                                rx.table.cell(m["similarity"].to_string()),
                            )
                        )
                    ),
                    width="100%",
                ),
            ),
            width="100%",
        ),
        width="100%",
    )

def threshold_sweeper() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("THRESHOLD SWEEP"),
            rx.text_area(
                value=PlaygroundState.sweep_text,
                on_change=PlaygroundState.set_sweep_text,
                placeholder="Paste a ticket...",
                rows="3",
                width="100%",
            ),
            rx.button("Run Sweep", on_click=PlaygroundState.sweep),
            rx.cond(
                (PlaygroundState.sweep_medoid["label"] != "") |
                (PlaygroundState.sweep_llm["label"] != ""),
                rx.vstack(
                    rx.hstack(
                        rx.card(
                            rx.vstack(
                                rx.text("Best Medoid Match", font_weight="bold"),
                                rx.text(PlaygroundState.sweep_medoid["label"]),
                                rx.text(f"Department: {PlaygroundState.sweep_medoid['department']}"),
                                rx.text(f"Confidence: {PlaygroundState.sweep_medoid['confidence']:.2%}"),
                                rx.text(f"First matched at threshold: {PlaygroundState.sweep_medoid['threshold']}"),
                                border=f"1px solid {ACCENT}",
                                padding="12px",
                                border_radius="6px",
                                flex="1",
                            ),
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("LLM Fallback", font_weight="bold"),
                                rx.text(PlaygroundState.sweep_llm["label"]),
                                rx.text(f"Department: {PlaygroundState.sweep_llm['department']}"),
                                rx.text(f"Source: {PlaygroundState.sweep_llm['source']}"),
                                rx.text(f"First fallback at threshold: {PlaygroundState.sweep_llm['threshold']}"),
                                border=f"1px solid {BORDER}",
                                padding="12px",
                                border_radius="6px",
                                flex="1",
                            ),
                        ),
                        gap="12px",
                        width="100%",
                    ),
                    rx.text(
                        f"Transition threshold: {PlaygroundState.transition_threshold}",
                        font_size="13px", color=MUTED,
                    ),
                    width="100%",
                ),
            ),
            width="100%",
        ),
        width="100%",
    )

def medoid_inspector() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("MEDOID INSPECTOR"),
            rx.button("Load Medoids", on_click=PlaygroundState.load_medoids),
            rx.cond(
                PlaygroundState.medoids.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ID"),
                            rx.table.column_header_cell("Label"),
                            rx.table.column_header_cell("Dept"),
                            rx.table.column_header_cell("Count"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            PlaygroundState.medoids,
                            lambda m: rx.table.row(
                                rx.table.cell(m["id"].to_string()),
                                rx.table.cell(m["meta_label"]),
                                rx.table.cell(m["department"]),
                                rx.table.cell(m["ticket_count"].to_string()),
                            )
                        )
                    ),
                    width="100%",
                ),
            ),
            width="100%",
        ),
        width="100%",
    )

def batch_tester() -> rx.Component:
    return rx.card(
        rx.vstack(
            section_label("BATCH TESTER"),
            rx.text_area(
                value=PlaygroundState.batch_text,
                on_change=PlaygroundState.set_batch_text,
                placeholder="One ticket per line...",
                rows="8",
                width="100%",          # fill card width
            ),
            rx.button("Run Batch", on_click=PlaygroundState.batch),
            rx.cond(
                PlaygroundState.batch_results.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Text"),
                            rx.table.column_header_cell("Label"),
                            rx.table.column_header_cell("Dept"),
                            rx.table.column_header_cell("Priority"),
                            rx.table.column_header_cell("Conf"),
                            rx.table.column_header_cell("Source"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            PlaygroundState.batch_results,
                            lambda r: rx.table.row(
                                rx.table.cell(r["text"]),
                                rx.table.cell(r["label"]),
                                rx.table.cell(r["department"]),
                                rx.table.cell(r["priority"]),
                                rx.table.cell(r["confidence"].to_string()),
                                rx.table.cell(r["source"]),
                            )
                        )
                    ),
                    width="100%",
                ),
            ),
            width="100%",
        ),
        width="100%",
    )

def playground_page() -> rx.Component:
    return rx.box(
        rx.heading("ML Playground", size="6", weight="bold", color=TEXT, margin_bottom="24px"),
        rx.vstack(
            embedding_explorer(),
            threshold_sweeper(),
            medoid_inspector(),
            batch_tester(),
            gap="16px",
            width="100%",
        ),
        max_width="1100px", margin="0 auto",
        padding="40px 24px", width="100%",
    )