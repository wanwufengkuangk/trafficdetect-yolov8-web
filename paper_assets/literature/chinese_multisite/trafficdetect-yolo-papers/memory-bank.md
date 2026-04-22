# Paper Memory Bank
Last updated: 2026-04-21

### [bdd100k] BDD100K: A Diverse Driving Dataset for Heterogeneous Multitask Learning
- **Authors**: Fisher Yu, Haofeng Chen, Xin Wang, Wenqi Xian, Yingying Chen, Fangchen Liu, Vashisht Madhavan, Trevor Darrell
- **Venue**: CVPR 2020
- **URL**: https://openaccess.thecvf.com/content_CVPR_2020/html/Yu_BDD100K_A_Diverse_Driving_Dataset_for_Heterogeneous_Multitask_Learning_CVPR_2020_paper.html
- **Citations**: not checked
- **Status**: discovered
- **Topics**: dataset, autonomous-driving, traffic-detection
- **Abstract**: 大规模自动驾驶多任务数据集论文，覆盖检测、分割、跟踪等任务。
- **Notes**: 对应你项目模块一的核心数据来源，写项目背景和数据集设计时几乎必引。
---

### [idd] IDD: A Dataset for Exploring Problems of Autonomous Navigation in Unconstrained Environments
- **Authors**: Girish Varma, Anbumani Subramanian, Anoop M. Namboodiri, Manmohan Chandraker, C. V. Jawahar
- **Venue**: WACV 2019
- **URL**: https://arxiv.org/abs/1811.10200
- **Citations**: not checked
- **Status**: discovered
- **Topics**: dataset, autonomous-driving, unstructured-road, animal-detection
- **Abstract**: 面向非结构化道路环境的自动驾驶数据集论文，强调复杂路况与类间差异。
- **Notes**: 对应你项目模块二所依赖的 IDD 系列数据背景，可用于解释“道路动物识别”任务来源。
---

### [cbam] CBAM: Convolutional Block Attention Module
- **Authors**: Sanghyun Woo, Jongchan Park, Joon-Young Lee, In So Kweon
- **Venue**: ECCV 2018
- **URL**: https://openaccess.thecvf.com/content_ECCV_2018/html/Sanghyun_Woo_Convolutional_Block_Attention_ECCV_2018_paper.html
- **Citations**: not checked
- **Status**: discovered
- **Topics**: attention, feature-enhancement, detection-backbone
- **Abstract**: 提出轻量级通道-空间联合注意力模块，可无缝嵌入 CNN。
- **Notes**: 你项目模块一已经显式引入 CBAM，这篇就是最直接的理论来源。
---

### [fpn] Feature Pyramid Networks for Object Detection
- **Authors**: Tsung-Yi Lin, Piotr Dollar, Ross Girshick, Kaiming He, Bharath Hariharan, Serge Belongie
- **Venue**: CVPR 2017
- **URL**: https://openaccess.thecvf.com/content_cvpr_2017/html/Lin_Feature_Pyramid_Networks_CVPR_2017_paper.html
- **Citations**: not checked
- **Status**: discovered
- **Topics**: multi-scale, feature-pyramid, small-object-detection
- **Abstract**: 经典多尺度检测论文，提出自顶向下特征金字塔结构。
- **Notes**: 你的 P2 小目标检测头可以从 FPN 理论脉络去解释其必要性与合理性。
---

### [panet] Path Aggregation Network for Instance Segmentation
- **Authors**: Shu Liu, Lu Qi, Haifang Qin, Jianping Shi, Jiaya Jia
- **Venue**: CVPR 2018
- **URL**: https://openaccess.thecvf.com/content_cvpr_2018/html/Liu_Path_Aggregation_Network_CVPR_2018_paper.html
- **Citations**: not checked
- **Status**: discovered
- **Topics**: neck, feature-fusion, multi-scale
- **Abstract**: 在 FPN 基础上加强自底向上的路径聚合，提高多尺度特征传递效率。
- **Notes**: 适合放在你项目里解释 neck/特征融合强化的技术背景。
---

### [wiseiou] Wise-IoU: Bounding Box Regression Loss with Dynamic Focusing Mechanism
- **Authors**: Zanjia Tong, Yuhang Chen, Zewei Xu, Rong Yu
- **Venue**: CoRR / arXiv 2023
- **URL**: https://arxiv.org/abs/2301.10051
- **Citations**: not checked
- **Status**: discovered
- **Topics**: loss-function, box-regression, localization
- **Abstract**: 提出带动态聚焦机制的边框回归损失，抑制异常样本干扰。
- **Notes**: 你项目中的 WIoU 替换就是直接基于这篇论文。
---

### [sahi] Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection
- **Authors**: Fatih Cagatay Akyon, Sinan Onur Altinuc, Alptekin Temizel
- **Venue**: ICIP 2022 / arXiv 2022
- **URL**: https://arxiv.org/abs/2202.06934
- **Citations**: not checked
- **Status**: discovered
- **Topics**: small-object-detection, inference, tiling
- **Abstract**: 针对远距离小目标提出切片推理与微调策略，显著提升小目标检测精度。
- **Notes**: 如果你后续还想继续提升远距离行人、交通灯、交通标志效果，这篇很有用。
---

### [yolo-mxanet] Small Object Detection in Traffic Scenes Based on YOLO-MXANet
- **Authors**: Xiaowei He, Rao Cheng, Zhonglong Zheng, Zeji Wang
- **Venue**: Sensors 2021
- **URL**: https://www.mdpi.com/1424-8220/21/21/7422
- **Citations**: not checked
- **Status**: discovered
- **Topics**: traffic-scenes, small-object-detection, lightweight
- **Abstract**: 面向交通场景小目标检测的改进 YOLO 方法，兼顾复杂背景和实时性。
- **Notes**: 这是“交通场景 + 小目标 + 改进 YOLO”方向的早期代表作，适合写相关工作。
---

### [stc-yolo] STC-YOLO: Small Object Detection Network for Traffic Signs in Complex Environments
- **Authors**: Huaqing Lai, Liangyan Chen, Weihua Liu, Zi Yan, Sheng Ye
- **Venue**: Sensors 2023
- **URL**: https://www.mdpi.com/1424-8220/23/11/5307
- **Citations**: not checked
- **Status**: discovered
- **Topics**: traffic-sign, small-object-detection, complex-environment
- **Abstract**: 面向复杂环境交通标志检测，聚焦多尺度融合、损失函数与增强策略。
- **Notes**: 你的类别里包含 traffic sign，这篇对模块一很贴。
---

### [sano-yolov7] A Small Object Detection Algorithm for Traffic Signs Based on Improved YOLOv7
- **Authors**: Songjiang Li, Shilong Wang, Peng Wang
- **Venue**: Sensors 2023
- **URL**: https://www.mdpi.com/1424-8220/23/16/7145
- **Citations**: not checked
- **Status**: discovered
- **Topics**: traffic-sign, small-object-layer, dynamic-conv
- **Abstract**: 在 YOLOv7 中加入小目标检测层、动态卷积与改进距离度量。
- **Notes**: 和你项目的 P2 小目标层思路很接近，适合在答辩时做横向对照。
---

### [mst-yolo] MST-YOLO: Small Object Detection Model for Autonomous Driving
- **Authors**: Mingjing Li, Xinyang Liu, Shuang Chen, Le Yang, Qingyu Du, Ziqing Han, Junshuai Wang
- **Venue**: Sensors 2024
- **URL**: https://www.mdpi.com/1424-8220/24/22/7347
- **Citations**: not checked
- **Status**: discovered
- **Topics**: yolov8, autonomous-driving, p2, small-object-detection
- **Abstract**: 基于 YOLOv8 的自动驾驶小目标检测模型，加入 P2 检测层和多种特征增强模块。
- **Notes**: 这是与你当前“YOLOv8 + P2 小目标头”最接近的一篇现成参考文献。
---

### [amw-yolov8n] AMW-YOLOv8n: Road Scene Object Detection Based on an Improved YOLOv8
- **Authors**: Donghao Wu, Chao Fang, Xiaogang Zheng, Jue Liu, Shengchun Wang, Xinyu Huang
- **Venue**: Electronics 2024
- **URL**: https://www.mdpi.com/2079-9292/13/20/4121
- **Citations**: not checked
- **Status**: discovered
- **Topics**: yolov8, road-scene, attention, multi-scale
- **Abstract**: 面向道路场景检测的改进 YOLOv8，强化不同尺度目标的特征表达。
- **Notes**: 和你“道路交通场景识别”这个任务表述高度一致，适合作为直接对标工作。
---

### [rso-yolo] RSO-YOLO: A Real-Time Detector for Small and Occluded Objects in Autonomous Driving Scenarios
- **Authors**: Quanxiang Wang, Zhaofa Zhou, Zhili Zhang
- **Venue**: Sensors 2025
- **URL**: https://www.mdpi.com/1424-8220/25/21/6703
- **Citations**: not checked
- **Status**: discovered
- **Topics**: autonomous-driving, small-object-detection, occlusion, p2
- **Abstract**: 针对自动驾驶中的小目标与遮挡问题，加入 P2 检测头和增强模块。
- **Notes**: 这篇很新，而且明确在 BDD100K 上做了实验，和你的主线非常接近。
---
