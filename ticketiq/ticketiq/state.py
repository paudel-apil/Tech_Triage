import httpx
import reflex as rx

API_BASE = "http://localhost:8000/api/v1/tickets"
TIMEOUT = 60.0
PAGE_SIZE = 12


class TicketState(rx.State):

    # ── Submit ─────────────────────────────────────────────────────────────
    description: str = ""
    submitting: bool = False
    submit_error: str = ""
    result: dict[str, object] = {}

    # ── Tickets list ───────────────────────────────────────────────────────
    tickets: list[dict] = []
    total: int = 0
    page: int = 0
    list_loading: bool = False
    list_error: str = ""

    # ── Search ─────────────────────────────────────────────────────────────
    query: str = ""
    search_results: list[dict] = []
    search_loading: bool = False
    search_error: str = ""
    searched: bool = False

    # ── UI state ───────────────────────────────────────────────────────────
    active_tab: str = "submit"
    expanded: list[int] = []   # ticket ids with solution open

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

    # ── Submit handlers ────────────────────────────────────────────────────
    def set_description(self, value: str):
        self.description = value

    async def submit_ticket(self):
        if not self.can_submit:
            return
        self.submitting = True
        self.submit_error = ""
        self.result = {}
        yield
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                r = await client.post(API_BASE + "/", json={"description": self.description})
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

    # ── List handlers ──────────────────────────────────────────────────────
    async def load_tickets(self):
        self.list_loading = True
        self.list_error = ""
        yield
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(
                    API_BASE + "/",
                    params={"limit": PAGE_SIZE, "offset": self.page * PAGE_SIZE},
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

    # ── Tab nav ────────────────────────────────────────────────────────────
    async def go_to(self, tab: str):
        self.active_tab = tab
        if tab == "tickets":
            self.page = 0
            async for u in self.load_tickets():
                yield u

    # ── Expand/collapse solution ───────────────────────────────────────────
    def toggle_expanded(self, tid: int):
        if tid in self.expanded:
            self.expanded = [i for i in self.expanded if i != tid]
        else:
            self.expanded = self.expanded + [tid]