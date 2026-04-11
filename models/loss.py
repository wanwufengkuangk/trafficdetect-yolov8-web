from __future__ import annotations

import torch
import torch.nn.functional as F
from ultralytics.utils.loss import BboxLoss
from ultralytics.utils.metrics import bbox_iou
from ultralytics.utils.tal import bbox2dist


class WIoUBboxLoss(BboxLoss):
    """BboxLoss variant that replaces CIoU with WIoU v3-style weighting."""

    def forward(
        self,
        pred_dist: torch.Tensor,
        pred_bboxes: torch.Tensor,
        anchor_points: torch.Tensor,
        target_bboxes: torch.Tensor,
        target_scores: torch.Tensor,
        target_scores_sum: torch.Tensor,
        fg_mask: torch.Tensor,
        imgsz: torch.Tensor,
        stride: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not fg_mask.any():
            zero = pred_dist.new_tensor(0.0)
            return zero, zero

        weight = target_scores.sum(-1)[fg_mask].unsqueeze(-1)
        pred_fg = pred_bboxes[fg_mask]
        target_fg = target_bboxes[fg_mask]

        iou = bbox_iou(pred_fg, target_fg, xywh=False, CIoU=False)
        diou = bbox_iou(pred_fg, target_fg, xywh=False, DIoU=True)
        distance_penalty = diou - iou

        wise_iou = iou.detach().clamp(min=1e-6)
        wise_scale = torch.exp((1.0 - wise_iou) * (wise_iou / wise_iou.mean()).detach())
        wiou_loss = wise_scale * (1.0 - iou - distance_penalty)
        loss_iou = (wiou_loss * weight).sum() / target_scores_sum

        if self.dfl_loss:
            target_ltrb = bbox2dist(anchor_points, target_bboxes, self.dfl_loss.reg_max - 1)
            loss_dfl = self.dfl_loss(pred_dist[fg_mask].view(-1, self.dfl_loss.reg_max), target_ltrb[fg_mask]) * weight
            loss_dfl = loss_dfl.sum() / target_scores_sum
        else:
            target_ltrb = bbox2dist(anchor_points, target_bboxes)
            target_ltrb = target_ltrb * stride
            target_ltrb[..., 0::2] /= imgsz[1]
            target_ltrb[..., 1::2] /= imgsz[0]
            pred_dist = pred_dist * stride
            pred_dist[..., 0::2] /= imgsz[1]
            pred_dist[..., 1::2] /= imgsz[0]
            loss_dfl = F.l1_loss(pred_dist[fg_mask], target_ltrb[fg_mask], reduction="none").mean(-1, keepdim=True)
            loss_dfl = (loss_dfl * weight).sum() / target_scores_sum

        return loss_iou, loss_dfl

