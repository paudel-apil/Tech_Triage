import reflex as rx

config = rx.Config(
    app_name="ticketiq",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
    ],
    frontend_port = 3000,
    backend_port = 8001,
    api_url="http://localhost:8001",
)