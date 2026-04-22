# Mind Graph
Last updated: 2026-04-21

### 交通目标检测综述
- **Description**: 从整体上理解 YOLO 在智能交通中的研究脉络、评价指标和问题边界。
- **Related topics**: 交通标志检测, 交通灯检测, 小目标检测
- **Key papers**:
  - [zju-traffic-yolo-review] 交通目标YOLO检测技术的研究进展 (浙江大学学报(工学版) 2025) — 可作为中文综述总入口

### 交通标志检测
- **Description**: 面向自动驾驶和道路场景中的交通标志定位与识别。
- **Related topics**: 小目标检测, 轻量化部署, 损失函数优化
- **Key papers**:
  - [emt-yolov8-traffic-sign-small-object] 基于改进的小目标交通标志检测算法研究 (电子测量技术 2025) — 小目标交通标志检测代表性工作
  - [hit-ghost-yolov8-traffic-sign] 基于YOLOv8s-CGSA交通标志检测算法 (智能计算机与应用 2025) — 兼顾精度和嵌入式部署
  - [sdie-yolov8-traffic-sign-autonomous-driving] 基于改进YOLOv8的自动驾驶交通标志检测算法 (信息技术与信息化 2025) — CBAM 和 WIoU 改进较贴近工程实现
- **Other relevant papers**:
  - [hans-improved-yolov8-traffic-sign] 基于改进Yolov8的交通标志检测算法 — 可作为补充中文材料

### 交通灯检测
- **Description**: 处理体积小、颜色敏感、背景复杂的交通信号灯检测问题。
- **Related topics**: 小目标检测, 多尺度特征融合
- **Key papers**:
  - [rjdk-traffic-light-yolov5-multiscale] 多尺度YOLOv5的交通灯检测算法 (软件导刊 2022) — 多尺度设计非常典型
  - [hans-traffic-light-yolov5s] 基于改进YOLOv5s的交通信号灯检测算法 — 适合补充交通灯场景细节

### 小目标与航拍场景
- **Description**: 从无人机、小目标和高分辨率特征利用角度借鉴检测增强策略。
- **Related topics**: P2检测层, 注意力机制, 多尺度融合
- **Key papers**:
  - [cjournal-yolov8-uav-small-object] 基于改进YOLOv8的无人机影像小目标检测算法 (云南民族大学学报(自然科学版) 2025) — P2 检测层、DyHead、SimAM 都很有借鉴性
  - [hans-asf-wiou-yolov8-uav] 基于ASF-WIoU-YOLOv8的无人机航拍图像多目标检测算法 — WIoU 和多尺度融合可复用

### 交通多目标与轻量化
- **Description**: 面向车辆、标志、信号灯等综合目标场景下的轻量化检测。
- **Related topics**: 轻量化部署, 多类别交通感知
- **Key papers**:
  - [hans-lightweight-traffic-multitarget-yolov8] 多机制融合的轻量化交通多目标检测算法 — 适合参考轻量化和多目标联合检测思路
