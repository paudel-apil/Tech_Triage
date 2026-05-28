import httpx, asyncio
import reflex as rx
import time, json



from .ui import (
    mono, ACCENT, CHART_BLUE,
    ACCENT, BORDER, MUTED, TEXT, SURFACE, SANS, MONO, RADIUS,
    HIGH, MED, LOW_C, HIGH_BG, MED_BG, LOW_BG,
)

API_BASE = "http://localhost:8000/api/v1/tickets"
API_BASE_V1 = "http://localhost:8000/api/v1"
TIMEOUT = 60.0
PAGE_SIZE = 12


class TicketState(rx.State):

    # ── Submit ─────────────────────────────────────────────────────────────
    description: str = ""
    submitting: bool = False
    submit_error: str = ""
    result: dict[str, object] = {}
    sim_threshold: float = 0.60

    # ── Tickets list ───────────────────────────────────────────────────────
    tickets: list[dict] = []
    total: int = 0
    page: int = 0
    list_loading: bool = False
    list_error: str = ""
    department_filter: str = ""
    departments: list[str] = []

    # ── Modal ──────────────────────────────────────────────────────────────
    modal_ticket: dict = {}
    modal_open: bool = False

    # ── Search ─────────────────────────────────────────────────────────────
    query: str = ""
    search_results: list[dict] = []
    search_loading: bool = False
    search_error: str = ""
    searched: bool = False

    # ── Stats ──────────────────────────────────────────────────────────────
    stats: dict = {}
    stats_loading: bool = False
    stats_error: str = ""

    all_departments: list[str] = [
        "Access & Permissions",
        "AI / ML",
        "Application Development",
        "CI/CD & Build Systems",
        "Data Streaming & Pipeline",
        "Database & Data Engineering",
        "Deployment & IaC",
        "Developer Experience & Tooling",
        "DevOps / Platform Engineering",
        "External Integrations & API Management",
        "Hardware / IT Support",
        "Monitoring & Observability",
        "Networking & Connectivity",
        "Security",
    ]


    # ── UI state ───────────────────────────────────────────────────────────
    active_tab: str = "submit"
    expanded: list[int] = []   # ticket ids with solution open

  # ── Feedback ───────────────────────────────────────────────────────
    show_feedback: bool = False
    feedback_type: str = ""
    selected_correction: str = ""
    feedback_submitted: bool = False

    # ── Computed ───────────────────────────────────────────────────────────
    @rx.var
    def char_count(self) -> int:
        return len(self.description)

    @rx.var
    def can_submit(self) -> bool:
        return self.char_count >= 20 and not self.submitting

    @rx.var
    def has_result(self) -> bool:
        return bool(self.result)

    @rx.var
    def total_pages(self) -> int:
        if self.total == 0:
            return 1
        return (self.total + PAGE_SIZE - 1) // PAGE_SIZE
    
    @rx.var
    def result_similar_tickets(self) -> list[dict]:
        """Return the similar tickets from the latest classification result, or an empty list."""
        return self.result.get("similar_tickets", [])

    @rx.var
    def on_first_page(self) -> bool:
        return self.page == 0

    @rx.var
    def on_last_page(self) -> bool:
        return self.page >= self.total_pages - 1
    
    @rx.var
    def has_similar_tickets(self) -> bool:
        return len(self.result.get("similar_tickets", [])) > 0

    @rx.var
    def has_search_results(self) -> bool:
        return len(self.search_results) > 0
    
    @rx.var
    def source_medoid_count(self) -> int:
        return self.stats.get("source_breakdown", {}).get("medoid", 0)

    @rx.var
    def source_llm_count(self) -> int:
        return self.stats.get("source_breakdown", {}).get("llm_fallback", 0)

    @rx.var
    def source_error_count(self) -> int:
        return self.stats.get("source_breakdown", {}).get("error", 0)

    @rx.var
    def stats_total_classified(self) -> int:
        return self.stats.get("total_classified", 0)

    @rx.var
    def stats_medoids(self) -> int:
        return self.stats.get("medoids", 0)
    
    @rx.var
    def threshold_pct(self) -> str:
        return f"{self.sim_threshold:.0%}"

    @rx.var
    def avg_confidence_pct(self) -> str:
        raw = self.stats.get("avg_confidence", 0.0)
        return f"{raw * 100:.3f}%"

    @rx.var
    def stats_top_labels(self) -> list[dict]:
        raw = self.stats.get("top_labels", [])  
        filtered = []
        for item in raw:
            lbl = item.get("label", "Unknown")
            if lbl.lower() in ("uncategorized", "uncategorised"):
                continue
            filtered.append(item)
        return filtered[:5]
        
    @rx.var
    def stats_department_breakdown(self) -> list[dict]:
        raw = self.stats.get("department_breakdown", [])
        merged = {}
        for item in raw:
            dept = item.get("department", "Unknown")
            count = item.get("count", 0)
            if dept.lower() in ("uncategorized", "uncategorised"):
                continue         
            merged[dept] = merged.get(dept, 0) + count
        return [{"department": k, "count": v} for k, v in sorted(merged.items())]
    
    @rx.var
    def uncategorised_count(self) -> int:
        raw = self.stats.get("department_breakdown", [])
        return sum(
            item.get("count", 0)
            for item in raw
            if item.get("department", "").lower() in ("uncategorized", "uncategorised")
        )

    # ── Submit handlers ────────────────────────────────────────────────────
    def set_description(self, value: str):
        self.description = value

    def set_sim_threshold(self, value: float):
        self.sim_threshold = value

    @rx.var
    def department_options(self) -> list[str]:
        return ["All departments"] + self.departments

    async def submit_ticket(self):
        if not self.can_submit:
            return
        self.submitting = True
        self.feedback_submitted = False
        self.show_feedback = False
        self.feedback_type = ""
        self.selected_correction = ""
        self.submit_error = ""
        self.result = {}
        yield
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                r = await client.post(API_BASE + "/", json={"description": self.description,
                                                            "sim_threshold": self.sim_threshold,},)
                r.raise_for_status()
                self.result = r.json()
        except httpx.HTTPStatusError as e:
            self.submit_error = e.response.text
        except Exception as e:
            self.submit_error = str(e)
        finally:
            self.submitting = False

    def clear_submit(self):
        self.description = ""
        self.result = {}
        self.submit_error = ""
        self.feedback_submitted = False
        self.show_feedback = False
        self.feedback_type = ""
        self.selected_correction = ""

    # ── Tickets list ───────────────────────────────────────────────────────
    async def load_department(self):
        try:
            async with httpx.AsyncClient(timeout = 10) as client:
                r = await client.get(API_BASE + "/departments")
                r.raise_for_status()
                self.departments = r.json().get("departments", [])
        except Exception:
            pass
    
    def set_department_filter(self, value: str):
        self.department_filter = value
        self.page = 0
    
    async def apply_department_filter(self, value: str):
        if value == "All departments":
            value = ""
        self.department_filter = value
        self.page = 0
        async for u in self.load_tickets():
            yield u

    # ── List handlers ──────────────────────────────────────────────────────
    async def load_tickets(self):
        self.list_loading = True
        self.list_error = ""
        yield
        try:
            params: dict = {
                "limit": PAGE_SIZE,
                "offset": self.page * PAGE_SIZE,
            }
            if self.department_filter:
                params["department"] = self.department_filter

            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(
                    API_BASE + "/",
                    params=params,
                )
                r.raise_for_status()
                data = r.json()
                self.tickets = data.get("tickets", [])
                self.total = data.get("total", 0)
        except Exception as e:
            self.list_error = str(e)
        finally:
            self.list_loading = False

    async def next_page(self):
        if not self.on_last_page:
            self.page += 1
            async for u in self.load_tickets():
                yield u

    async def prev_page(self):
        if not self.on_first_page:
            self.page -= 1
            async for u in self.load_tickets():
                yield u

    # ── Modal ──────────────────────────────────────────────────────────────
    def open_modal(self, ticket: dict):
        self.modal_ticket = ticket
        self.modal_open = True
 
    def close_modal(self):
        self.modal_open = False
        self.modal_ticket = {}

    # ── Search handlers ────────────────────────────────────────────────────
    def set_query(self, value: str):
        self.query = value

    async def run_search(self):
        if not self.query.strip():
            return
        self.search_loading = True
        self.search_error = ""
        self.search_results = []
        self.searched = False
        yield
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    API_BASE + "/search",
                    json={"query": self.query.strip()},
                )
                r.raise_for_status()
                self.search_results = r.json().get("results", [])
                self.searched = True
        except Exception as e:
            self.search_error = str(e)
        finally:
            self.search_loading = False

    def clear_search(self):
        self.query = ""
        self.search_results = []
        self.searched = False
        self.search_error = ""

    # ── Stats ──────────────────────────────────────────────────────────────
    async def load_stats(self):
        self.stats_loading = True
        self.stats_error = ""
        yield
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(API_BASE + "/stats")
                r.raise_for_status()
                self.stats = r.json()
        except Exception as e:
            self.stats_error = str(e)
        finally:
            self.stats_loading = False
 

    # ── Tab nav ────────────────────────────────────────────────────────────
    async def go_to(self, tab: str):
        self.active_tab = tab
        if tab == "tickets":
            self.page = 0
            await self.load_department()
            async for u in self.load_tickets():
                yield u
        elif tab == "stats":
            async for u in self.load_stats():
                yield u

    # ── Expand/collapse solution ───────────────────────────────────────────
    def toggle_expanded(self, tid: int):
        if tid in self.expanded:
            self.expanded = [i for i in self.expanded if i != tid]
        else:
            self.expanded = self.expanded + [tid]

    async def thumb_up(self):
        self.feedback_type = "thumbs_up"
        self.show_feedback = False
        await self.submit_feedback()

    async def thumb_down(self):
        self.feedback_type = "thumbs_down"
        self.show_feedback = True   # show the label dropdown

    def set_correction(self, value: str):
        self.selected_correction = value

    async def submit_feedback(self):
        if not self.result.get("id"):
            return
        ticket_id = self.result["id"]
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    f"{API_BASE}/{ticket_id}/feedback",
                    json={
                        "feedback_type": self.feedback_type,
                        "corrected_label": self.selected_correction if self.feedback_type == "thumbs_down" else None
                    }
                )
            self.feedback_submitted = True
            self.show_feedback = False
        except Exception as e:
            self.submit_error = str(e)


class TrendsState(rx.State):
    # Accelerating categories
    accelerating: list[dict] = []
    # Priority timeline
    priority_timeline: list[dict] = []
    # Fallback rate
    fallback_timeline: list[dict] = []
    # Department load
    department_load: list[dict] = []
    # New labels
    new_labels: list[dict] = []

    loading: bool = False
    error: str = ""

    async def load_all(self):
        self.loading = True
        self.error = ""
        yield
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Fetch all endpoints concurrently
                res_acc = await client.get(f"{API_BASE}/trends/accelerating")
                res_pri = await client.get(f"{API_BASE}/trends/priority-timeline?days=7&granularity=hour")
                res_fb  = await client.get(f"{API_BASE}/trends/fallback-rate?days=14")
                res_dep = await client.get(f"{API_BASE}/trends/department-load?days=14")
                res_new = await client.get(f"{API_BASE}/trends/new-labels")

            self.accelerating = res_acc.json()["categories"]
            self.priority_timeline = res_pri.json()["timeline"]
            self.fallback_timeline = res_fb.json()["timeline"]
            self.department_load = res_dep.json()["timeline"]
            self.new_labels = res_new.json()["labels"]
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False

class PlaygroundState(rx.State):
    probe_text: str = ""
    probe_results: list[dict] = []

    sweep_text: str = ""
    sweep_medoid: dict = {}             
    sweep_llm: dict = {}                
    transition_threshold: float = 0.0

    medoids: list[dict] = []

    batch_text: str = ""
    batch_results: list[dict] = []


    def set_probe_text(self, value: str):
        self.probe_text = value

    def set_sweep_text(self, value: str):
        self.sweep_text = value

    def set_batch_text(self, value: str):
        self.batch_text = value

    async def probe(self):
        if not self.probe_text.strip():
            return
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{API_BASE_V1}/dev/probe",
                json={"text": self.probe_text.strip()}
            )
            data = resp.json()
            self.probe_results = data["matches"]

    async def sweep(self):
        if not self.sweep_text.strip():
            return
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{API_BASE_V1}/dev/threshold-sweep",
                json={"text": self.sweep_text.strip()}
            )
            data = resp.json()
            self.sweep_medoid = data.get("medoid", {})
            self.sweep_llm = data.get("llm_fallback", {})
            self.transition_threshold = data.get("transition_threshold", 0.0)

    async def load_medoids(self):
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(f"{API_BASE_V1}/dev/medoids")
            data = resp.json()
            self.medoids = data["medoids"]

    async def batch(self):
        lines = [line.strip() for line in self.batch_text.split("\n") if line.strip()]
        if not lines:
            return
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{API_BASE_V1}/dev/batch",
                json={"texts": lines}
            )
            data = resp.json()
            self.batch_results = data["results"]

    network_url: str = ""  

    async def show_network(self):
        if not self.probe_text.strip():
            return
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{API_BASE_V1}/dev/probe-tickets-graph",
                json={"text": self.probe_text.strip()}
            )
            data = resp.json()
            self.network_url = data["url"]
        

class ThemeState(rx.State):
    theme: str = "dark"  

    def toggle(self):
        self.theme = "light" if self.theme == "dark" else "dark"

    @rx.var
    def opposite(self) -> str:
        return "light" if self.theme == "dark" else "dark"
    

class StreamState(rx.State):
    live_tickets: list[dict] = []
    last_id: int = 0
    streaming: bool = False

    async def start_stream(self):
        self.streaming = True
        self.last_id = 0
        self.live_tickets = []
        return StreamState.poll

    async def poll(self):
        if not self.streaming:
            return
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"{API_BASE_V1}/stream/latest",
                    params={"since_id": self.last_id, "limit": 20},
                )
                data = r.json()
                new_tickets = data.get("tickets", [])
            if new_tickets:
                self.live_tickets = new_tickets + self.live_tickets
                self.last_id = new_tickets[0]["id"]
                self.live_tickets = self.live_tickets[:50]
        except Exception:
            pass
        await asyncio.sleep(3)
        return StreamState.poll

    async def stop_stream(self):
        self.streaming = False
        self.live_tickets = []
        self.last_id = 0

    @rx.var
    def feed_html(self) -> str:
        """Render the live ticket feed as an HTML string."""
        if not self.live_tickets:
            return ""
        rows = []
        for t in self.live_tickets:
            p = t.get("priority", "low").lower()
            color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}.get(p, "#888")
            bg = {"high": "rgba(239,68,68,0.10)", "medium": "rgba(245,158,11,0.10)", "low": "rgba(34,197,94,0.10)"}.get(p, "transparent")
            rows.append(f"""<div style="background:{bg}; border-left:3px solid {color};
                padding:10px 14px; margin-bottom:6px; border-radius:4px;
                display:flex; align-items:flex-start; gap:10px; animation:slideIn 0.4s ease-out;">
                <div style="width:10px;height:10px;border-radius:50%;background:{color};flex-shrink:0;margin-top:4px;"></div>
                <div style="font-family:monospace;font-size:11px;font-weight:bold;color:{color};min-width:50px;">
                    {t.get('priority','?').upper()}</div>
                <div style="display:flex;flex-direction:column;gap:2px;">
                    <div style="font-size:13px;color:#d0d0d8;line-height:1.4;">{t.get('description','')}</div>
                    <div style="font-size:11px;color:#9090a8;">
                        {t.get('label','')}  ·  {t.get('department','')}  ·  conf: {t.get('confidence',0):.2f}  ·  {t.get('source','')}
                    </div>
                </div>
            </div>""")
        return "".join(rows)