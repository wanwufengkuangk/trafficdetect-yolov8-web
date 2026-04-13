from __future__ import annotations

import argparse
import os
import random
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MIN_BOX_WIDTH = 20
MIN_BOX_HEIGHT = 20
MIN_BOX_AREA = 900


@dataclass(frozen=True)
class IDDAnimalBox:
    xmin: int
    ymin: int
    xmax: int
    ymax: int
    image_width: int
    image_height: int


def read_split_entries(source_root: Path) -> list[str]:
    entries: list[str] = []
    for split_name in ("train", "val", "test"):
        split_path = source_root / f"{split_name}.txt"
        if not split_path.exists():
            continue
        lines = [line.strip() for line in split_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        entries.extend(lines)
    return sorted(set(entries))


def extract_animal_boxes(xml_path: Path) -> list[tuple[int, int, int, int, int, int]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find("size")
    if size is None:
        raise ValueError(f"missing size node in {xml_path}")

    image_width = int(size.findtext("width", "0"))
    image_height = int(size.findtext("height", "0"))
    if image_width <= 0 or image_height <= 0:
        raise ValueError(f"invalid image size in {xml_path}")

    boxes: list[tuple[int, int, int, int, int, int]] = []
    for obj in root.findall("object"):
        if (obj.findtext("name") or "").strip() != "animal":
            continue
        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue

        xmin = int(float(bndbox.findtext("xmin", "0")))
        ymin = int(float(bndbox.findtext("ymin", "0")))
        xmax = int(float(bndbox.findtext("xmax", "0")))
        ymax = int(float(bndbox.findtext("ymax", "0")))

        xmin = max(0, min(xmin, image_width - 1))
        ymin = max(0, min(ymin, image_height - 1))
        xmax = max(0, min(xmax, image_width))
        ymax = max(0, min(ymax, image_height))
        if xmax <= xmin or ymax <= ymin:
            continue
        box_width = xmax - xmin
        box_height = ymax - ymin
        box_area = box_width * box_height
        if box_width < MIN_BOX_WIDTH or box_height < MIN_BOX_HEIGHT or box_area < MIN_BOX_AREA:
            continue

        boxes.append((xmin, ymin, xmax, ymax, image_width, image_height))

    return boxes


def repartition_entries(entries: list[str], train_ratio: float, val_ratio: float, seed: int) -> dict[str, list[str]]:
    if not entries:
        return {"train": [], "val": [], "test": []}

    shuffled = entries[:]
    random.Random(seed).shuffle(shuffled)

    total = len(shuffled)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)

    if total >= 3:
        train_count = max(train_count, 1)
        val_count = max(val_count, 1)
        if train_count + val_count >= total:
            val_count = max(1, total - train_count - 1)
        test_count = total - train_count - val_count
        if test_count <= 0:
            test_count = 1
            if train_count > val_count and train_count > 1:
                train_count -= 1
            elif val_count > 1:
                val_count -= 1
    else:
        train_count = max(total - 1, 1)
        val_count = total - train_count
        test_count = 0

    train_split = shuffled[:train_count]
    val_split = shuffled[train_count : train_count + val_count]
    test_split = shuffled[train_count + val_count :]

    return {"train": train_split, "val": val_split, "test": test_split}


def flatten_stem(relative_entry: str) -> str:
    return relative_entry.replace("/", "__").replace("\\", "__")


def resolve_image_path(images_root: Path, relative_entry: str) -> Path:
    for extension in IMAGE_EXTENSIONS:
        candidate = images_root / (relative_entry.replace("/", os.sep) + extension)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"missing image for {relative_entry}")


def resolve_xml_path(annotations_root: Path, relative_entry: str) -> Path:
    xml_path = annotations_root / (relative_entry.replace("/", os.sep) + ".xml")
    if not xml_path.exists():
        raise FileNotFoundError(f"missing annotation for {relative_entry}")
    return xml_path


def materialize_image(source_path: Path, target_path: Path, image_mode: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if image_mode == "hardlink":
        if target_path.exists():
            return
        os.link(source_path, target_path)
        return
    if image_mode == "copy":
        shutil.copy2(source_path, target_path)
        return
    raise ValueError(f"unsupported image mode: {image_mode}")


def yolo_row_from_box(box: tuple[int, int, int, int, int, int]) -> str:
    xmin, ymin, xmax, ymax, image_width, image_height = box
    x_center = ((xmin + xmax) / 2.0) / image_width
    y_center = ((ymin + ymax) / 2.0) / image_height
    box_width = (xmax - xmin) / image_width
    box_height = (ymax - ymin) / image_height
    return f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"


def convert_dataset(
    source_root: Path,
    dataset_root: Path,
    image_mode: str = "copy",
    seed: int = 42,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
) -> dict[str, dict[str, int]]:
    source_root = source_root.resolve()
    dataset_root = dataset_root.resolve()

    all_entries = read_split_entries(source_root)
    repartitioned = repartition_entries(all_entries, train_ratio=train_ratio, val_ratio=val_ratio, seed=seed)

    images_root = source_root / "JPEGImages"
    annotations_root = source_root / "Annotations"

    if dataset_root.exists():
        shutil.rmtree(dataset_root)

    summary: dict[str, dict[str, int]] = {}
    total_images = 0
    total_boxes = 0

    for split_name, entries in repartitioned.items():
        image_count = 0
        box_count = 0
        images_dir = dataset_root / "images" / split_name
        labels_dir = dataset_root / "labels" / split_name
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)

        for relative_entry in entries:
            image_path = resolve_image_path(images_root, relative_entry)
            xml_path = resolve_xml_path(annotations_root, relative_entry)
            boxes = extract_animal_boxes(xml_path)
            if not boxes:
                continue

            flat_stem = flatten_stem(relative_entry)
            target_image_path = images_dir / f"{flat_stem}{image_path.suffix.lower()}"
            target_label_path = labels_dir / f"{flat_stem}.txt"

            materialize_image(image_path, target_image_path, image_mode=image_mode)
            rows = [yolo_row_from_box(box) for box in boxes]
            target_label_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

            image_count += 1
            box_count += len(rows)

        summary[split_name] = {"images": image_count, "boxes": box_count}
        total_images += image_count
        total_boxes += box_count

    summary["all"] = {"images": total_images, "boxes": total_boxes}
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert the filtered IDD animal subset into YOLO detection format.")
    parser.add_argument("--source-root", type=Path, default=Path("datasets_raw/IDD_Detection"))
    parser.add_argument("--dataset-root", type=Path, default=Path("datasets/idd_animal_yolo"))
    parser.add_argument("--image-mode", choices=["copy", "hardlink"], default="copy")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = convert_dataset(
        source_root=args.source_root,
        dataset_root=args.dataset_root,
        image_mode=args.image_mode,
        seed=args.seed,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
    )
    for split_name, values in summary.items():
        print(f"[{split_name}] images={values['images']} boxes={values['boxes']}")


if __name__ == "__main__":
    main()
