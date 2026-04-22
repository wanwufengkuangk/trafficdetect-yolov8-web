# Mind Graph
Last updated: 2026-04-21

### 数据集基础
- **Description**: 解释项目两条任务线的数据来源与场景合理性。
- **Related topics**: 小目标检测, 道路场景检测
- **Key papers**:
  - [bdd100k] BDD100K: A Diverse Driving Dataset for Heterogeneous Multitask Learning (CVPR 2020) — 模块一主数据背景
  - [idd] IDD: A Dataset for Exploring Problems of Autonomous Navigation in Unconstrained Environments (WACV 2019) — 模块二数据来源背景
- **Other relevant papers**:
  - [rso-yolo] RSO-YOLO — 也在 BDD100K 上验证

### 小目标检测与多尺度特征
- **Description**: 解释为什么需要 P2 检测头、金字塔融合和切片推理。
- **Related topics**: neck设计, 交通标志检测, 远距离目标
- **Key papers**:
  - [fpn] Feature Pyramid Networks for Object Detection (CVPR 2017) — 多尺度检测理论起点
  - [panet] Path Aggregation Network for Instance Segmentation (CVPR 2018) — 自底向上路径增强
  - [mst-yolo] MST-YOLO (Sensors 2024) — YOLOv8 + P2 的直接近邻工作
- **Other relevant papers**:
  - [sahi] Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection — 推理阶段强化小目标
  - [yolo-mxanet] Small Object Detection in Traffic Scenes Based on YOLO-MXANet — 交通小目标直接相关
  - [stc-yolo] STC-YOLO — 交通标志小目标检测
  - [sano-yolov7] A Small Object Detection Algorithm for Traffic Signs Based on Improved YOLOv7 — 加小目标层的强相关工作
  - [rso-yolo] RSO-YOLO — 小目标和遮挡检测

### 注意力与特征增强
- **Description**: 解释在复杂背景、遮挡、弱纹理目标下为何引入注意力模块。
- **Related topics**: backbone增强, 复杂背景, 遮挡鲁棒性
- **Key papers**:
  - [cbam] CBAM: Convolutional Block Attention Module (ECCV 2018) — 项目中 CBAM 的直接出处
  - [amw-yolov8n] AMW-YOLOv8n (Electronics 2024) — 改进 YOLOv8 的道路场景特征增强
- **Other relevant papers**:
  - [rso-yolo] RSO-YOLO — 小目标和遮挡增强
  - [stc-yolo] STC-YOLO — 多尺度与复杂环境交通标志检测

### 边框回归与损失设计
- **Description**: 解释为什么替换默认框回归损失，以及这样做的收益。
- **Related topics**: box-regression, localization, hard-sample
- **Key papers**:
  - [wiseiou] Wise-IoU: Bounding Box Regression Loss with Dynamic Focusing Mechanism (CoRR 2023) — 项目 WIoU 的理论依据
- **Other relevant papers**:
  - [sano-yolov7] A Small Object Detection Algorithm for Traffic Signs Based on Improved YOLOv7 — 对小目标定位度量也有借鉴意义
