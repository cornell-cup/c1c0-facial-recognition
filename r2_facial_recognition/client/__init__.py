__all__ = ['Client']

try:
    from .client import Client
except ImportError:
    from client import Client