from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "default.yaml"
CONFIG_ENV_VAR = "TRAFFICDETECT_CONFIG"


@dataclass(frozen=True)
class ModuleConfig:
    key: str
    title: str
    subtitle: str
    class_names: list[str]
    class_names_zh: list[str]
    best_weight_name: str
    task: str
    supports_batch: bool
    supports_stream: bool
    supports_boxes: bool
    supports_masks: bool
    supports_sequence_input: bool
    sequence_input_mode: str | None
    sequence_playback_mode: str | None


@dataclass(frozen=True)
class RuntimeConfig:
    root_dir: Path
    project_name: str
    web_title: str
    weights_dir: Path
    results_dir: Path
    dataset_dir: Path
    obstacle_dataset_dir: Path
    default_conf: float
    default_iou: float
    default_module: str
    base_weight_name: str
    modules: dict[str, ModuleConfig]

    @property
    def traffic_module(self) -> ModuleConfig:
        return self.modules["traffic"]

    @property
    def obstacle_module(self) -> ModuleConfig:
        return self.modules["obstacle"]

    @property
    def class_names(self) -> list[str]:
        return self.traffic_module.class_names

    @property
    def class_names_zh(self) -> list[str]:
        return self.traffic_module.class_names_zh

    @property
    def best_weight_name(self) -> str:
        return self.traffic_module.best_weight_name

    @property
    def base_weight_path(self) -> Path:
        return self.weights_dir / self.base_weight_name

    @property
    def best_weight_path(self) -> Path:
        return self.weights_dir / self.best_weight_name

    def module_weight_path(self, module_key: str) -> Path:
        return self.weights_dir / self.modules[module_key].best_weight_name


def _resolve_root_dir(config_path: Path) -> Path:
    if config_path.parent.name == "configs":
        return config_path.parent.parent
    return config_path.parent


def _coerce_strings(values: Any) -> list[str]:
    return [str(value) for value in values or []]


def _coerce_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _build_module(
    key: str,
    module_meta: dict[str, Any],
    class_names: list[str],
    class_names_zh: list[str],
    fallback_title: str,
    fallback_subtitle: str,
    fallback_weight: str,
    fallback_task: str,
    fallback_supports_batch: bool,
    fallback_supports_stream: bool,
    fallback_supports_boxes: bool,
    fallback_supports_masks: bool,
    fallback_supports_sequence_input: bool,
    fallback_sequence_input_mode: str | None = None,
    fallback_sequence_playback_mode: str | None = None,
) -> ModuleConfig:
    sequence_input_mode = module_meta.get("sequence_input_mode", fallback_sequence_input_mode)
    sequence_playback_mode = module_meta.get("sequence_playback_mode", fallback_sequence_playback_mode)
    return ModuleConfig(
        key=key,
        title=str(module_meta.get("title", fallback_title)),
        subtitle=str(module_meta.get("subtitle", fallback_subtitle)),
        class_names=class_names,
        class_names_zh=class_names_zh,
        best_weight_name=str(module_meta.get("best_model", fallback_weight)),
        task=str(module_meta.get("task", fallback_task)),
        supports_batch=_coerce_bool(module_meta.get("supports_batch"), fallback_supports_batch),
        supports_stream=_coerce_bool(module_meta.get("supports_stream"), fallback_supports_stream),
        supports_boxes=_coerce_bool(module_meta.get("supports_boxes"), fallback_supports_boxes),
        supports_masks=_coerce_bool(module_meta.get("supports_masks"), fallback_supports_masks),
        supports_sequence_input=_coerce_bool(module_meta.get("supports_sequence_input"), fallback_supports_sequence_input),
        sequence_input_mode=str(sequence_input_mode) if sequence_input_mode is not None else None,
        sequence_playback_mode=str(sequence_playback_mode) if sequence_playback_mode is not None else None,
    )


def load_runtime_config(config_path: str | Path | None = None) -> RuntimeConfig:
    resolved_config = config_path or os.getenv(CONFIG_ENV_VAR) or DEFAULT_CONFIG_PATH
    config_path = Path(resolved_config).resolve()
    root_dir = _resolve_root_dir(config_path)

    with config_path.open("r", encoding="utf-8") as handle:
        raw_config: dict[str, Any] = yaml.safe_load(handle)

    paths = raw_config.get("paths", {})
    web = raw_config.get("web", {})
    model = raw_config.get("model", {})
    web_modules = web.get("modules", {})

    traffic_names = _coerce_strings(raw_config.get("classes", {}).get("names"))
    traffic_names_zh = _coerce_strings(raw_config.get("classes", {}).get("ch_names"))
    obstacle_names = _coerce_strings(raw_config.get("obstacle_classes", {}).get("names")) or ["animal"]
    obstacle_names_zh = _coerce_strings(raw_config.get("obstacle_classes", {}).get("ch_names")) or ["道路动物"]

    traffic_module = _build_module(
        key="traffic",
        module_meta=web_modules.get("traffic", {}),
        class_names=traffic_names,
        class_names_zh=traffic_names_zh,
        fallback_title="交通目标检测",
        fallback_subtitle="BDD100K 交通目标识别",
        fallback_weight=str(web.get("best_model", "best.pt")),
        fallback_task="detect",
        fallback_supports_batch=False,
        fallback_supports_stream=True,
        fallback_supports_boxes=True,
        fallback_supports_masks=False,
        fallback_supports_sequence_input=False,
    )
    obstacle_meta = dict(web_modules.get("obstacle", {}))
    obstacle_meta.setdefault("task", raw_config.get("obstacle_task", "detect"))
    obstacle_meta.setdefault("supports_batch", raw_config.get("obstacle_supports_batch", True))
    obstacle_meta.setdefault("supports_stream", raw_config.get("obstacle_supports_stream", False))
    obstacle_meta.setdefault("supports_boxes", raw_config.get("obstacle_supports_boxes", True))
    obstacle_meta.setdefault("supports_masks", raw_config.get("obstacle_supports_masks", False))
    obstacle_meta.setdefault("supports_sequence_input", raw_config.get("obstacle_supports_sequence_input", True))
    obstacle_meta.setdefault("sequence_input_mode", "folder")
    obstacle_meta.setdefault("sequence_playback_mode", "sync_during_processing")
    obstacle_module = _build_module(
        key="obstacle",
        module_meta=obstacle_meta,
        class_names=obstacle_names,
        class_names_zh=obstacle_names_zh,
        fallback_title="道路动物识别",
        fallback_subtitle="IDD animal 单类检测",
        fallback_weight="animal_best.pt",
        fallback_task="detect",
        fallback_supports_batch=True,
        fallback_supports_stream=False,
        fallback_supports_boxes=True,
        fallback_supports_masks=False,
        fallback_supports_sequence_input=True,
        fallback_sequence_input_mode="folder",
        fallback_sequence_playback_mode="sync_during_processing",
    )

    return RuntimeConfig(
        root_dir=root_dir,
        project_name=str(raw_config["project"]["name"]),
        web_title=str(web.get("title", raw_config["project"]["name"])),
        weights_dir=root_dir / paths.get("weights_dir", "weights"),
        results_dir=root_dir / paths.get("results_dir", "results"),
        dataset_dir=root_dir / paths.get("dataset_dir", "datasets"),
        obstacle_dataset_dir=root_dir / paths.get("obstacle_dataset_dir", "datasets/idd_animal_yolo"),
        default_conf=float(web.get("default_conf", 0.25)),
        default_iou=float(web.get("default_iou", 0.45)),
        default_module=str(web.get("default_module", "traffic")),
        base_weight_name=str(model.get("base", "yolov8s.pt")),
        modules={
            "traffic": traffic_module,
            "obstacle": obstacle_module,
        },
    )
