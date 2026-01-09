"""
Domain Events scaffolding.

Provides a minimal domain events system to enable decoupled side effects.
This module is pure Python and has no infrastructure dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Generic, List, Protocol, Type, TypeVar

E = TypeVar("E", bound="DomainEvent")


@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events emitted by services/entities."""

    name: str
    occurred_at: datetime
    payload: Dict[str, object]


class EventPublisher(Protocol, Generic[E]):
    """Protocol for event publisher implementations."""

    def publish(self, event: E) -> None:
        ...

    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        ...


class InMemoryPublisher(EventPublisher[DomainEvent]):
    """Simple in-process event bus for development and unit tests."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[DomainEvent], None]]] = {}

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(event.name, []):
            handler(event)

    def subscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        name = event_type.__name__
        self._handlers.setdefault(name, []).append(handler)
