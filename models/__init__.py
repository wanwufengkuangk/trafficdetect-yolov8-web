"""Custom model extensions for YOLOv8 training."""

from .loss import WIoUBboxLoss
from .register import register_all

__all__ = ["WIoUBboxLoss", "register_all"]

