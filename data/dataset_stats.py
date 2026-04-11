from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


def load_dataset_names(dataset_yaml: Path) -> dict[int, str]:
    with dataset_yaml.open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = yaml.safe_load(handle)
    names = data["names"]
    return {int(class_id): name for class_id, name in names.items()}


def collect_split_stats(labels_dir: Path, class_names: dict[int, str]) -> dict[str, Any]:
    class_counts: Counter[str] = Counter()
    empty_files = 0
    total_boxes = 0
    label_files = sorted(labels_dir.glob("*.txt"))
    for label_path in label_files:
        content = label_path.read_text(encoding="utf-8").strip()
        if not content:
            empty_files += 1
            continue
        for line in content.splitlines():
            class_id = int(line.split()[0])
            class_counts[class_names[class_id]] += 1
            total_boxes += 1
    return {
        "label_files": len(label_files),
        "empty_files": empty_files,
        "total_boxes": total_boxes,
        "class_counts": dict(class_counts),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize label distribution for the rebuilt BDD100K dataset.")
    parser.add_argument("--dataset-root", type=Path, default=Path("datasets/bdd100k"))
    parser.add_argument("--dataset-yaml", type=Path, default=Path("configs/dataset_bdd100k.yaml"))
    parser.add_argument("--output", type=Path, default=Path("results/dataset_stats.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    class_names = load_dataset_names(args.dataset_yaml.resolve())
    report = {
        "train": collect_split_stats((args.dataset_root / "labels" / "train").resolve(), class_names),
        "val": collect_split_stats((args.dataset_root / "labels" / "val").resolve(), class_names),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

