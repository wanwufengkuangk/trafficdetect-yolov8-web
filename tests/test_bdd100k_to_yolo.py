import unittest

from data.bdd100k_to_yolo import (
    BDD100K_CLASS_MAP,
    convert_annotation_record,
    convert_box2d_to_yolo,
)


class BDD100KToYOLOTests(unittest.TestCase):
    def test_convert_box2d_to_yolo_clamps_coordinates(self) -> None:
        values = convert_box2d_to_yolo(
            box2d={"x1": -10.0, "y1": 20.0, "x2": 1290.0, "y2": 740.0},
            image_width=1280,
            image_height=720,
        )

        self.assertEqual(values, (0.5, 0.513889, 1.0, 0.972222))

    def test_convert_annotation_record_filters_non_detection_objects(self) -> None:
        sample = {
            "name": "sample-frame",
            "frames": [
                {
                    "objects": [
                        {
                            "category": "traffic light",
                            "box2d": {"x1": 100, "y1": 20, "x2": 140, "y2": 80},
                        },
                        {
                            "category": "lane/road curb",
                            "poly2d": [[0, 0, "L"], [1, 1, "L"]],
                        },
                        {
                            "category": "unknown-object",
                            "box2d": {"x1": 10, "y1": 10, "x2": 20, "y2": 20},
                        },
                    ]
                }
            ],
        }

        converted = convert_annotation_record(sample)

        self.assertEqual(converted.file_stem, "sample-frame")
        self.assertEqual(converted.total_objects, 3)
        self.assertEqual(converted.mapped_objects, 1)
        self.assertEqual(converted.class_counts, {"traffic light": 1})
        self.assertEqual(
            converted.yolo_rows,
            [f"{BDD100K_CLASS_MAP['traffic light']} 0.093750 0.069444 0.031250 0.083333"],
        )

    def test_convert_annotation_record_maps_bdd_aliases_to_project_classes(self) -> None:
        sample = {
            "name": "alias-frame",
            "frames": [
                {
                    "objects": [
                        {
                            "category": "person",
                            "box2d": {"x1": 320, "y1": 200, "x2": 352, "y2": 300},
                        },
                        {
                            "category": "bike",
                            "box2d": {"x1": 400, "y1": 240, "x2": 460, "y2": 320},
                        },
                        {
                            "category": "motor",
                            "box2d": {"x1": 600, "y1": 240, "x2": 680, "y2": 340},
                        },
                    ]
                }
            ],
        }

        converted = convert_annotation_record(sample)

        self.assertEqual(converted.class_counts["pedestrian"], 1)
        self.assertEqual(converted.class_counts["bicycle"], 1)
        self.assertEqual(converted.class_counts["motorcycle"], 1)
        self.assertEqual(converted.mapped_objects, 3)


if __name__ == "__main__":
    unittest.main()
