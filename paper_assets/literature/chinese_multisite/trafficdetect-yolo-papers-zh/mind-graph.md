# 中文文献 Mind Graph
Last updated: 2026-04-21

### 交通标志与交通灯小目标检测
- **Description**: 支撑项目中 traffic sign、traffic light 等小目标类别的相关工作。
- **Related topics**: 小目标检测, 多尺度检测, 注意力机制
- **Key papers**:
  - [traffic-sign-yolov8] 基于改进Yolov8的交通标志检测算法 — 与改进 YOLOv8 和交通标志直接相关
  - [traffic-light-yolov5s] 基于改进YOLOv5s的交通信号灯检测算法 — 交通灯小目标检测代表
  - [traffic-light-multiscale-yolov5] 多尺度YOLOv5的交通灯检测算法 — 多尺度检测思路可服务 P2 分支解释
- **Other relevant papers**:
  - [traffic-sign-yolov5] 基于改进YOLOv5的交通标志检测算法研究 — 轻量化和 CBAM 参考
  - [traffic-sign-yolov7-tiny] 基于YOLOv7-Tiny的交通标识检测算法研究 — 加检测层和注意力机制参考
  - [traffic-sign-pointcloud] 融合全景影像和车载点云的交通标志信息提取 — 交通标志信息提取补充背景

### 车辆与交通多目标检测
- **Description**: 支撑项目中 car、truck、bus、motorcycle、bicycle 等道路交通目标检测。
- **Related topics**: 智能交通, 车辆检测, 轻量化部署
- **Key papers**:
  - [yolo-vehicle-evaluation] 车辆检测中YOLO模型的综合性能评估与实证分析 — 解释选择 YOLO 系列的依据
  - [lightweight-traffic-multitarget] 多机制融合的轻量化交通多目标检测算法 — 与交通多目标、轻量化、WIoU 直接相关
  - [aerial-vehicle-yolov8] 基于YOLOv8的航拍车辆检测技术研究 — 车辆小目标检测参考

### WIoU 与多尺度机制
- **Description**: 支撑项目中 WIoU 损失替换、P2 小目标头和多尺度融合路线。
- **Related topics**: WIoU, 多尺度特征融合, 小目标检测
- **Key papers**:
  - [asf-wiou-yolov8] 基于ASF-WIoU-YOLOv8的无人机航拍图像多目标检测算法 — 中文 WIoU 与多尺度融合参考
  - [lightweight-traffic-multitarget] 多机制融合的轻量化交通多目标检测算法 — 交通场景下的 WIoU 与轻量化参考
- **Other relevant papers**:
  - [traffic-light-multiscale-yolov5] 多尺度YOLOv5的交通灯检测算法 — 多尺度检测参考
  - [traffic-sign-yolov7-tiny] 基于YOLOv7-Tiny的交通标识检测算法研究 — 增加检测层服务小目标
