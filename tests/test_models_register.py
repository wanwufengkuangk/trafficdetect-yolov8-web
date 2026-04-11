import unittest

import ultralytics.nn.tasks as tasks
from ultralytics.utils import loss as loss_module

from models.loss import WIoUBboxLoss
from models.register import register_all


class RegisterAllTests(unittest.TestCase):
    def test_register_all_injects_cbam(self) -> None:
        original_cbam = getattr(tasks, "CBAM", None)
        try:
            if hasattr(tasks, "CBAM"):
                delattr(tasks, "CBAM")
            register_all(use_wiou=False)
            self.assertTrue(hasattr(tasks, "CBAM"))
        finally:
            if original_cbam is None:
                if hasattr(tasks, "CBAM"):
                    delattr(tasks, "CBAM")
            else:
                tasks.CBAM = original_cbam

    def test_register_all_replaces_bbox_loss_when_enabled(self) -> None:
        original_bbox_loss = loss_module.BboxLoss
        try:
            register_all(use_wiou=True)
            self.assertIs(loss_module.BboxLoss, WIoUBboxLoss)
        finally:
            loss_module.BboxLoss = original_bbox_loss


if __name__ == "__main__":
    unittest.main()
