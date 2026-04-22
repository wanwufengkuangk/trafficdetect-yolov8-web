from __future__ import annotations

import argparse
import csv
import random
import shutil
import sys
from collections import Counter
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.register import register_all


CLASS_NAMES_ZH = [
    "行人",
    "骑行者",
    "小汽车",
    "卡车",
    "公交车",
    "列车",
    "摩托车",
    "自行车",
    "交通灯",
    "交通标志",
]

PRIORITY_CLASSES = {
    0,  # pedestrian
    1,  # rider
    3,  # truck
    4,  # bus
    6,  # motorcycle
    7,  # bicycle
    8,  # traffic light
    9,  # traffic sign
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select high-quality BDD100K images for demo.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT, help="Project root directory.")
    parser.add_argument("--split", default="val", choices=("train", "val"), help="BDD100K split to sample from.")
    parser.add_argument("--candidates", type=int, default=1000, help="Number of sampled images to score.")
    parser.add_argument("--limit", type=int, default=30, help="Number of demo images to export.")
    parser.add_argument("--seed", type=int, default=20260422, help="Random seed for reproducible sampling.")
    parser.add_argument("--conf", type=float, default=0.25, help="YOLO confidence threshold.")
    parser.add_argument("--iou", type=float, default=0.45, help="YOLO IoU threshold.")
    parser.add_argument("--batch", type=int, default=16, help="Prediction batch size.")
    parser.add_argument("--imgsz", type=int, default=640, help="Prediction image size.")
    parser.add_argument("--weights", type=Path, default=Path("weights/best.pt"), help="Model checkpoint path.")
    parser.add_argument("--output", type=Path, default=Path("datasets/bdd100k_demo"), help="Output demo dataset path.")
    return parser.parse_args()


def score_prediction(classes: list[int], confidences: list[float]) -> float:
    if not confidences:
        return 0.0
    detection_count = len(confidences)
    class_diversity = len(set(classes))
    mean_conf = sum(confidences) / detection_count
    max_conf = max(confidences)
    priority_count = sum(1 for class_id in classes if class_id in PRIORITY_CLASSES)

    # Demo images should look convincing: many boxes, high confidence, and varied traffic categories.
    return (
        detection_count * 1.2
        + class_diversity * 2.0
        + priority_count * 1.1
        + mean_conf * 4.0
        + max_conf * 3.0
    )


def class_summary(classes: list[int]) -> str:
    counter = Counter(classes)
    return "；".join(f"{CLASS_NAMES_ZH[class_id]}:{count}" for class_id, count in sorted(counter.items()))


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    image_dir = root / "datasets" / "bdd100k" / "images" / args.split
    label_dir = root / "datasets" / "bdd100k" / "labels" / args.split
    weights_path = (root / args.weights).resolve()
    output_dir = (root / args.output).resolve()

    if not image_dir.exists():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    if not weights_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {weights_path}")
    if output_dir.exists() and any(path.is_file() for path in output_dir.rglob("*")):
        raise FileExistsError(f"Output directory already has files, please move it first: {output_dir}")

    images = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not images:
        raise RuntimeError(f"No images found in: {image_dir}")

    random.Random(args.seed).shuffle(images)
    candidates = images[: min(args.candidates, len(images))]

    register_all(use_wiou=False)
    model = YOLO(str(weights_path))
    device = 0 if torch.cuda.is_available() else "cpu"

    scored_rows: list[dict[str, object]] = []
    for start in range(0, len(candidates), args.batch):
        batch_paths = candidates[start : start + args.batch]
        results = model.predict(
            source=[str(path) for path in batch_paths],
            imgsz=args.imgsz,
            conf=args.conf,
            iou=args.iou,
            device=device,
            verbose=False,
        )
        for source_path, result in zip(batch_paths, results):
            classes = [int(value) for value in result.boxes.cls.cpu().tolist()]
            confidences = [float(value) for value in result.boxes.conf.cpu().tolist()]
            if len(confidences) < 2 or max(confidences, default=0.0) < 0.35:
                continue
            scored_rows.append(
                {
                    "path": source_path,
                    "score": round(score_prediction(classes, confidences), 6),
                    "detection_count": len(confidences),
                    "class_diversity": len(set(classes)),
                    "max_confidence": round(max(confidences), 6),
                    "mean_confidence": round(sum(confidences) / len(confidences), 6),
                    "classes_zh": class_summary(classes),
                }
            )

    if len(scored_rows) < args.limit:
        raise RuntimeError(f"Only {len(scored_rows)} candidate images passed filters; reduce --limit or thresholds.")

    selected = sorted(scored_rows, key=lambda row: (-float(row["score"]), str(row["path"])))[: args.limit]

    out_images = output_dir / "images"
    out_labels = output_dir / "labels"
    out_predictions = output_dir / "predictions"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)
    out_predictions.mkdir(parents=True, exist_ok=True)

    metadata_rows: list[dict[str, object]] = []
    for index, row in enumerate(selected, start=1):
        source_path = Path(row["path"])
        export_name = f"{index:02d}_{source_path.name}"
        image_target = out_images / export_name
        shutil.copy2(source_path, image_target)

        source_label = label_dir / f"{source_path.stem}.txt"
        if source_label.exists():
            shutil.copy2(source_label, out_labels / f"{Path(export_name).stem}.txt")

        rendered = model.predict(
            source=str(source_path),
            imgsz=args.imgsz,
            conf=args.conf,
            iou=args.iou,
            device=device,
            verbose=False,
        )[0].plot()
        cv2.imwrite(str(out_predictions / export_name), rendered)

        metadata_rows.append(
            {
                "rank": index,
                "file_name": export_name,
                "source_split": args.split,
                "source_path": str(source_path.relative_to(root)),
                "detection_count": row["detection_count"],
                "class_diversity": row["class_diversity"],
                "max_confidence": row["max_confidence"],
                "mean_confidence": row["mean_confidence"],
                "score": row["score"],
                "classes_zh": row["classes_zh"],
            }
        )

    with (output_dir / "metadata.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metadata_rows[0]))
        writer.writeheader()
        writer.writerows(metadata_rows)

    (output_dir / "README.md").write_text(
        "\n".join(
            [
                "# BDD100K 答辩演示测试集",
                "",
                f"- 来源：`datasets/bdd100k/images/{args.split}`",
                f"- 权重：`{args.weights.as_posix()}`",
                f"- 候选图数量：{len(candidates)}",
                f"- 最终图片数量：{len(selected)}",
                f"- 筛选规则：优先选择检测框数量多、置信度高、类别更丰富，并包含行人/骑行者/交通灯/交通标志等更适合展示的样例。",
                "",
                "## 目录说明",
                "",
                "- `images/`：筛选后的原始图片，可直接用于 Web 端上传演示。",
                "- `labels/`：对应 YOLO 标签，便于后续测试或复核。",
                "- `predictions/`：当前模型生成的可视化预测图，便于答辩前快速预览展示效果。",
                "- `metadata.csv`：每张图的检测数量、类别、置信度和综合评分。",
            ]
        ),
        encoding="utf-8",
    )

    print(f"已生成演示测试集：{output_dir}")
    print(f"图片数量：{len(selected)}")
    print(f"可视化结果：{out_predictions}")


if __name__ == "__main__":
    main()
