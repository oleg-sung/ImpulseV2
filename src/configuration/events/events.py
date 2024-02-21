from dataclasses import dataclass

from fastapi import FastAPI


@dataclass(frozen=True)
class Events:
    events: tuple

    def register_startup_events(self, app: FastAPI):
        for event in self.events:
            app.add_event_handler("startup", event)
