import textwrap
import unittest
from pathlib import Path
import shutil
import uuid

from app.config import load_runtime_config


class AppConfigTests(unittest.TestCase):
    def test_load_runtime_config_returns_project_classes(self) -> None:
        root = Path("results") / "test_runtime_config" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))

        config_path = root / "default.yaml"
        config_path.write_text(
            textwrap.dedent(
                """
                project:
                  name: "TrafficDetect"
                paths:
                  weights_dir: "weights"
                  results_dir: "results"
                  dataset_dir: "datasets"
                classes:
                  names: ["pedestrian", "car"]
                  ch_names: ["行人", "小汽车"]
                web:
                  title: "TrafficDetect Web"
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

        runtime = load_runtime_config(config_path)

        self.assertEqual(runtime.project_name, "TrafficDetect")
        self.assertEqual(runtime.web_title, "TrafficDetect Web")
        self.assertEqual(runtime.class_names, ["pedestrian", "car"])
        self.assertEqual(runtime.class_names_zh, ["行人", "小汽车"])
        self.assertEqual(runtime.weights_dir, root.resolve() / "weights")


if __name__ == "__main__":
    unittest.main()
