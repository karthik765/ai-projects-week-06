"""Explainable, dependency-free model selection."""

from .catalog import Model, default_catalog
from .policy import RouteRequest, RoutingError, route

__all__ = ["Model", "RouteRequest", "RoutingError", "default_catalog", "route"]
