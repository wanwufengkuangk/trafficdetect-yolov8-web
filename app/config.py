from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "default.yaml"


@dataclass(frozen=True)
class RuntimeConfig:
    root_dir: Path
    project_name: str
    web_title: str
    weights_dir: Path
    results_dir: Path
    dataset_dir: Path
    class_names: list[str]
    class_names_zh: list[str]
    default_conf: float
    default_iou: float
    base_weight_name: str
    best_weight_name: str

    @property
    def base_weight_path(self) -> Path:
        return self.weights_dir / self.base_weight_name

    @property
    def best_weight_path(self) -> Path:
        return self.weights_dir / self.best_weight_name


def _resolve_root_dir(config_path: Path) -> Path:
    if config_path.parent.name == "configs":
        return config_path.parent.parent
    return config_path.parent


def load_runtime_config(config_path: str | Path | None = None) -> RuntimeConfig:
    config_path = Path(config_path or DEFAULT_CONFIG_PATH).resolve()
    root_dir = _resolve_root_dir(config_path)

    with config_path.open("r", encoding="utf-8") as handle:
        raw_config: dict[str, Any] = yaml.safe_load(handle)

    paths = raw_config.get("paths", {})
    classes = raw_config.get("classes", {})
    web = raw_config.get("web", {})
    model = raw_config.get("model", {})

    return RuntimeConfig(
        root_dir=root_dir,
        project_name=raw_config["project"]["name"],
        web_title=web.get("title", raw_config["project"]["name"]),
        weights_dir=root_dir / paths.get("weights_dir", "weights"),
        results_dir=root_dir / paths.get("results_dir", "results"),
        dataset_dir=root_dir / paths.get("dataset_dir", "datasets"),
        class_names=list(classes.get("names", [])),
        class_names_zh=list(classes.get("ch_names", [])),
        default_conf=float(web.get("default_conf", 0.25)),
        default_iou=float(web.get("default_iou", 0.45)),
        base_weight_name=model.get("base", "yolov8s.pt"),
        best_weight_name=web.get("best_model", "best.pt"),
    )
