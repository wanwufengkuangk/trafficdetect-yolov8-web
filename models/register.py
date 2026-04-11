from __future__ import annotations

import ultralytics.nn.tasks as tasks
from ultralytics.nn.modules.conv import CBAM
from ultralytics.utils import loss as loss_module

from models.loss import WIoUBboxLoss


def register_all(use_wiou: bool = True) -> None:
    """Register custom modules into the Ultralytics runtime."""

    tasks.CBAM = CBAM
    if use_wiou:
        loss_module.BboxLoss = WIoUBboxLoss
