# TrafficDetect

## 项目简介
TrafficDetect 是一个面向道路交通场景的双模块智能识别系统，集成了模型训练、命令行推理、FastAPI 后端服务和网页端可视化展示能力。

项目当前最终版本包含两个模块：

- 模块一：基于 BDD100K 的 10 类交通目标检测
- 模块二：基于 IDD animal 子集的道路动物识别

项目定位不是单一模型训练脚本，而是一个可训练、可部署、可演示、可复现的完整工程。

## 当前最终版本说明

### 模块一
- 任务：交通目标检测
- 数据集：BDD100K 重建 YOLO 检测数据集
- 类别：`pedestrian`、`rider`、`car`、`truck`、`bus`、`train`、`motorcycle`、`bicycle`、`traffic light`、`traffic sign`
- 最终主线：改进版 YOLOv8s

### 模块二
- 任务：单类动物检测
- 数据集：`datasets/idd_animal_yolo`
- 类别：`animal`
- 最终模型：`YOLO11n`
- 当前主线：轻量道路动物识别

说明：

- 模块二当前最终方案已经不再采用 SOD 分割作为主线
- 模块二对外展示为“道路动物识别”，但部分内部接口路径仍沿用 `obstacle` 命名，以减少系统改动成本

## 算法优化亮点
本项目最重要的算法优化集中在模块一，模块二则强调轻量化与可部署性。

### 模块一的核心优化
模块一并不是直接使用原始 YOLOv8s，而是在标准模型基础上完成了逐步增强。

#### 1. P2 小目标检测头
对应模型：

- `configs/model_yolov8s_p2.yaml`

优化思路：

- 在原有检测头基础上增加更高分辨率的 P2 检测分支
- 使模型对远距离、小尺寸交通目标更敏感

优化价值：

- 对行人、交通灯、交通标志等小目标更友好
- 缓解原始 YOLOv8s 对小目标漏检的问题

#### 2. CBAM 注意力机制
对应模型：

- `configs/model_yolov8s_custom.yaml`

优化思路：

- 在主干特征提取阶段引入 CBAM
- 同时从通道和空间两个维度增强有效特征响应

优化价值：

- 强化关键区域特征表达
- 减少复杂背景对检测结果的干扰

#### 3. WIoU 边界框损失
对应注册逻辑：

- `models/register.py`

优化思路：

- 在最终 `full` 变体中，将 Ultralytics 默认边框回归损失替换为自定义 WIoU 实现

优化价值：

- 提升框回归质量
- 改善复杂目标下的定位稳定性

#### 4. 逐步对照实验路线
模块一不是一次性堆叠所有改动，而是采用可解释的递进式对照设计：

- `baseline`：标准 YOLOv8s
- `p2`：在 baseline 上增加 P2 小目标头
- `p2_cbam`：在 P2 基础上加入 CBAM
- `full`：在 `p2_cbam` 基础上进一步启用 WIoU

这样设计的好处是：

- 方便做实验对比
- 方便在论文和答辩中说明每一项优化的作用
- 工程实现更加可控

### 模块二的设计取舍
模块二经历过两轮重要方案调整：

- 初版：SOD 道路异物检测
- 第二版：SOD 道路异物分割
- 最终版：IDD animal 单类轻量检测

最终放弃 SOD 分割主线的原因是：

- 小目标异物过小、边界过碎
- 分割训练难度高，前期指标起量慢
- 演示稳定性不够理想

当前模块二采用 `YOLO11n` 的原因是：

- 模型更轻量
- 训练速度更快
- 更适合网页部署和实际演示
- 更符合“小动物等非常规道路风险目标识别”的展示需求

## 项目目录结构
项目中最关键的目录如下：

```text
yolov8/
├─ app/                 # FastAPI 后端、配置与推理服务
├─ configs/             # 项目配置、模型配置、数据集配置
├─ data/                # 数据转换、校验与统计脚本
├─ datasets/            # 训练数据集
├─ inference/           # 命令行推理脚本
├─ models/              # 自定义模型注册逻辑
├─ result/              # 训练、验证和 Web 批量推理输出目录
├─ static/              # 前端页面与脚本
├─ training/            # 训练与验证脚本
├─ weights/             # 固定命名的最终权重
├─ start_web.py         # 网页启动入口
├─ start_web.bat        # Windows 本地一键启动脚本
└─ requirements.txt     # 项目依赖
```

## 项目清理与合并建议

本节只给出清理建议，不代表必须立即删除。删除前建议先确认是否还需要复现实验、继续训练或保留论文素材。

### 建议保留的核心工程内容

| 路径 | 建议 | 原因 |
|---|---|---|
| `app/` | 保留 | FastAPI 后端、配置加载和 Web 推理服务核心代码 |
| `static/` | 保留 | Web 前端页面、样式和交互脚本 |
| `configs/` | 保留 | 数据集、模型和运行参数配置 |
| `data/` | 保留 | BDD100K、IDD animal 数据转换和校验脚本 |
| `training/` | 保留 | 模块一和模块二训练、验证、导出脚本 |
| `inference/` | 保留 | 本地命令行推理脚本 |
| `models/` | 保留 | 自定义模型注册、损失函数和结构扩展逻辑 |
| `weights/` | 保留 | Web 演示所需最终权重，至少保留 `best.pt` 和 `animal_best.pt` |
| `requirements.txt` | 保留 | 项目依赖入口 |
| `start_web.py`、`start_web.bat` | 保留 | 本地 Web 演示启动入口 |

### 可以删除或不建议提交的内容

| 路径 | 建议 | 删除条件 | 说明 |
|---|---|---|---|
| `app/__pycache__/`、`models/__pycache__/`、`training/__pycache__/`、`inference/__pycache__/` | 可以删除 | 任意时间 | Python 缓存目录，运行时会自动重新生成 |
| `results/` | 可以删除或合并到 `result/` | 确认其中没有需要保留的验证输出 | 当前配置文件使用的是 `result/`，`results/` 容易造成目录混乱 |
| `result/animal_sequences/` | 可按需删除 | 不需要保留 Web 批量推理生成的图片序列和 zip | 属于运行产物，占用空间较大，不影响代码运行 |
| `result/train_animal/`、`result/train_bdd_full/` | 可归档后删除 | 已经提取关键指标、曲线和最佳权重 | 属于训练产物；若要复现实验或查原始日志，先不要删 |
| `datasets/` | 可外置或删除 | 不在本机继续训练，只做 Web 演示 | 数据集体积最大；Web 演示只依赖 `weights/`，不依赖完整训练集 |
| `.codex/` | 可从交付包移除 | 打包给别人或提交最终项目时 | Codex 本地会话文件，不属于项目源码 |
| `.git/` | 不要随意删除 | 只有在做纯交付压缩包且不需要版本历史时 | 删除后会失去 Git 版本记录 |

### 建议合并或整理的内容

| 当前路径 | 建议合并到 | 原因 |
|---|---|---|
| `paper_assets/` 与 `论文插图_手动插入/` | 已整理到 `paper_assets/manual_figures/` | 两者都是论文插图素材，集中保存后更便于论文插图维护 |
| `交通目标检测论文初稿.md`、`面向道路场景的改进YOLOv8s交通目标检测系统设计与验证_无图片占位版.docx`、`项目计划书.md` | 已整理到 `paper_assets/manuscript/` | 论文文档已从项目根目录移出，根目录更聚焦工程入口 |
| `trafficdetect-yolo-papers/`、`trafficdetect-yolo-papers-zh/`、`trafficdetect-yolo-papers-zh-multisite/` | 已整理到 `paper_assets/literature/` | 论文已引用文献放入 `core/`，原始检索资料统一归档到 `chinese_multisite/` |
| 根目录 `yolov8s.pt` | 已移动到 `weights/yolov8s.pt` | 当前训练脚本优先查找 `weights/yolov8s.pt`，权重文件已统一归入 `weights/` |

### 推荐整理后的目录形态

```text
yolov8/
├─ app/
├─ configs/
├─ data/
├─ datasets/                 # 可外置，若只演示 Web 可不随项目交付
├─ inference/
├─ models/
├─ paper_assets/
│  ├─ manual_figures/
│  ├─ literature/
│  │  ├─ core/              # 论文已引用核心文献
│  │  │  ├─ chinese/        # 已引用中文核心文献
│  │  │  └─ english/        # 已引用英文核心文献
│  │  └─ chinese_multisite/ # 原始文献检索归档
│  └─ manuscript/
├─ result/                   # 训练与推理产物，可按需清理
├─ static/
├─ tools/
├─ training/
├─ weights/
├─ README.md
├─ requirements.txt
├─ start_web.bat
└─ start_web.py
```

### 清理优先级建议

| 优先级 | 操作 | 预期收益 |
|---|---|---|
| 高 | 删除所有 `__pycache__/` | 安全、无风险、清理缓存 |
| 高 | 删除或合并空的 `results/` 到 `result/` | 避免结果目录混乱 |
| 中 | 已将论文引用文献整理到 `paper_assets/literature/core/`，其余检索资料归档到 `paper_assets/literature/chinese_multisite/` | 写论文时优先查看核心文献，备用资料也不丢失 |
| 中 | 已合并 `paper_assets/` 与 `论文插图_手动插入/` | 论文素材更清晰 |
| 中 | 已将根目录论文文档移动到 `paper_assets/manuscript/` | 根目录更干净 |
| 低 | 删除或外置 `datasets/` | 释放大量空间，但会影响本地训练复现 |
| 低 | 清理 `result/` 下大体积训练和推理产物 | 释放空间，但会影响原始实验记录追溯 |

## 环境依赖

### 本地开发环境建议
- Windows 10/11
- Python 3.10 或 3.12
- Anaconda / Miniconda
- NVIDIA GPU + CUDA 环境

### 主要依赖
- `ultralytics`
- `opencv-python`
- `pillow`
- `numpy`
- `matplotlib`
- `pandas`
- `PyYAML`
- `fastapi`
- `uvicorn`
- `python-multipart`
- `onnx`

依赖文件：

- [requirements.txt](C:\Users\89657\Desktop\yolov8\requirements.txt)

### 5090 服务器提示
如果在 5090 服务器上训练，建议：

- 优先保留镜像自带 `torch`
- 不要先盲目覆盖安装新版本 `torch`
- 仅补装项目缺少的其余依赖

## 数据集准备

### 模块一：BDD100K
模块一使用重建后的 YOLO 检测数据集：

- `datasets/bdd100k`

相关脚本：

- [data/bdd100k_to_yolo.py](C:\Users\89657\Desktop\yolov8\data\bdd100k_to_yolo.py)
- [data/verify_dataset.py](C:\Users\89657\Desktop\yolov8\data\verify_dataset.py)
- [data/dataset_stats.py](C:\Users\89657\Desktop\yolov8\data\dataset_stats.py)

### 模块二：IDD animal
模块二使用已经筛选、清洗并转换完成的 YOLO 数据集：

- `datasets/idd_animal_yolo`

相关脚本：

- [data/idd_animal_to_yolo.py](C:\Users\89657\Desktop\yolov8\data\idd_animal_to_yolo.py)

数据集配置文件：

- [configs/dataset_idd_animal.yaml](C:\Users\89657\Desktop\yolov8\configs\dataset_idd_animal.yaml)

## 模型训练

### 模块一训练
标准训练命令：

```bash
python -u training/train.py --variant full --epochs 100 --batch 32 --workers 8 --imgsz 640 --device 0 --name train_bdd_full
```

模块一支持的变体：

- `baseline`
- `p2`
- `p2_cbam`
- `full`

示例：

```bash
python -u training/train.py --variant baseline --epochs 100 --batch 32 --workers 8 --imgsz 640 --device 0 --name train_bdd_baseline
```

### 模块二训练
正式训练：

```bash
python -u training/train_obstacle.py --epochs 100 --batch 32 --workers 8 --imgsz 960 --device 0 --name train_animal
```

quick smoke：

```bash
python -u training/train_obstacle.py --quick --device 0 --name smoke_animal
```

### 验证命令
模块一：

```bash
python -u training/val.py --variant full --device 0
```

模块二：

```bash
python -u training/val_obstacle.py --device 0 --name val_animal
```

## 本地部署
本项目本地部署是交付和答辩展示的重点，推荐按下面流程执行。

### 1. 创建并激活环境
如果本地还没有项目环境，可以先创建：

```powershell
conda create -n yolov8 python=3.10 -y
conda activate yolov8
```

### 2. 安装依赖
在项目根目录执行：

```powershell
pip install -r requirements.txt
```

### 3. 检查关键权重文件
本地网页启动前，建议确认 `weights/` 下至少存在：

- 模块一主权重：`best.pt`
- 模块二主权重：`animal_best.pt`

如果模块一需要对照展示，也可以保留：

- `baseline_best.pt`
- `p2_best.pt`
- `p2_cbam_best.pt`

### 4. 启动网页
推荐两种方式。

#### 方式一：使用批处理脚本
直接双击：

- [start_web.bat](C:\Users\89657\Desktop\yolov8\start_web.bat)

该脚本会：

- 激活 `yolov8` 环境
- 启动 `start_web.py`
- 默认使用 `8010` 端口

#### 方式二：命令行启动

```powershell
conda activate yolov8
python start_web.py
```

或：

```powershell
conda activate yolov8
python -m app.main
```

### 5. 本地访问地址
启动成功后，在浏览器中访问：

- `http://127.0.0.1:8010`
- `http://localhost:8010`

### 6. 本地部署检查清单
如果网页打不开，建议按顺序检查：

1. 当前是否已激活 `yolov8` 环境
2. `weights/` 下是否存在对应模型权重
3. 端口 `8010` 是否被其他程序占用
4. `datasets/`、`configs/`、`app/` 是否完整

### 7. 本地命令行推理
模块一：

```powershell
python -u inference/predict.py --variant full --source path\to\image_or_video --device 0
```

模块二：

```powershell
python -u inference/predict_obstacle.py --source path\to\image_or_folder --device 0
```

## 服务器训练建议

### 上传方式
最稳妥的做法是将整个项目目录打包上传。

本地压缩命令：

```powershell
cd C:\Users\89657\Desktop
Compress-Archive -Path .\yolov8 -DestinationPath .\yolov8.zip -Force
```

### 服务器解压

```bash
cd /root/autodl-tmp
apt-get update
apt-get install -y unzip tmux
unzip yolov8.zip
cd /root/autodl-tmp/yolov8
```

### 创建环境

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda create -n yolov8 python=3.12 -y
conda activate yolov8
```

### 检查 GPU 与 torch

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

### 安装依赖

```bash
pip install ultralytics==8.4.36 opencv-python==4.13.0.92 pillow==12.1.1 numpy==2.2.6 matplotlib==3.10.8 pandas==2.3.3 PyYAML==6.0.3 onnx==1.18.0 fastapi uvicorn python-multipart
```

### 模块二服务器训练命令

```bash
cd /root/autodl-tmp/yolov8
source /root/miniconda3/etc/profile.d/conda.sh
conda activate yolov8
unset OMP_NUM_THREADS
python -u training/train_obstacle.py --epochs 100 --batch 32 --workers 8 --imgsz 960 --device 0 --name train_animal_5090
```

### 常用辅助命令
后台训练：

```bash
tmux new -s animal_train
```

重新进入：

```bash
tmux attach -t animal_train
```

显卡监控：

```bash
nvidia-smi -l 2
```

## 模型权重位置

### 模块一
模块一最佳权重通常保存在：

- `results/<run_name>/weights/best.pt`

训练脚本会额外复制到：

- `weights/best.pt`
- `weights/baseline_best.pt`
- `weights/p2_best.pt`
- `weights/p2_cbam_best.pt`

### 模块二
模块二训练过程中，最佳权重通常保存为：

- `results/<run_name>/weights/best.pt`

训练脚本会额外复制到固定位置：

- `weights/animal_best.pt`

## 说明与注意事项

### 1. 模块二接口路径仍沿用 `obstacle`
为了降低系统改动成本，模块二虽然已经切换到“道路动物识别”，但当前接口路径仍保留为：

- `/api/obstacle/config`
- `/api/obstacle/detect/image`
- `/api/obstacle/detect/batch`

这不会影响实际功能与展示。

### 2. 模块一是主成果，模块二是扩展成果
项目整体答辩时，建议将：

- 模块一作为主要性能和算法优化展示对象
- 模块二作为非常规道路风险目标识别扩展模块

### 3. 原 SOD 路线保留为实验记录
模块二曾经历：

- SOD 检测
- SOD 分割
- IDD animal 检测

前两条路线保留为实验与方案演进记录，但不再作为最终主线。
