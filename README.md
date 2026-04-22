# TrafficDetect

## 项目概述
TrafficDetect 是一个面向道路交通场景的目标识别 Web 项目，当前保留了网页端部署主线，支持两个识别模块：

- 交通目标检测：基于 BDD100K 的 10 类检测
- 道路动物识别：基于 IDD animal 子集的单类检测

项目目标不是只训练一个模型，而是提供一套可训练、可推理、可本地部署、可答辩演示的完整工程。

## 当前算法方案

### 模块一：交通目标检测
- 数据集：`datasets/bdd100k`
- 基础模型：`YOLOv8s`
- 最终改进：`P2 小目标检测头 + CBAM 注意力 + WIoU 边框回归损失`
- 类别：
  `pedestrian`、`rider`、`car`、`truck`、`bus`、`train`、`motorcycle`、`bicycle`、`traffic light`、`traffic sign`

### 模块二：道路动物识别
- 数据集：`datasets/idd_animal_yolo`
- 基础模型：`YOLO11n`
- 任务：单类动物检测
- 类别：`animal`

## 目录结构
```text
yolov8/
├─ app/                         # FastAPI 后端、路由、推理服务、运行配置解析
├─ configs/                     # 项目配置、模型配置、数据集配置、部署模板
├─ data/                        # 数据转换、校验、统计、演示集筛选脚本
├─ datasets/                    # 数据集与演示测试集
├─ inference/                   # 命令行推理脚本
├─ models/                      # 自定义模块注册、损失函数
├─ paper_assets/                # 论文、插图、文献归档
├─ result/                      # 训练与推理输出
├─ static/                      # Web 前端资源
├─ training/                    # 训练与验证脚本
├─ weights/                     # 固定命名权重
├─ start_web.py                 # Python 启动入口，支持外部配置文件
├─ start_web.bat                # Windows 通用启动脚本
├─ requirements.txt             # Python 依赖
└─ README.md                    # 项目说明
```

## 核心文件说明
- [configs/default.yaml](/C:/Users/89657/Desktop/yolov8/configs/default.yaml)：项目当前默认运行配置。
- [configs/deploy.example.yaml](/C:/Users/89657/Desktop/yolov8/configs/deploy.example.yaml)：跨电脑部署用模板配置，建议复制一份再改。
- [start_web.py](/C:/Users/89657/Desktop/yolov8/start_web.py)：支持 `--config` 指定运行配置。
- [start_web.bat](/C:/Users/89657/Desktop/yolov8/start_web.bat)：Windows 下直接双击或命令行执行的通用启动脚本。
- [app/config.py](/C:/Users/89657/Desktop/yolov8/app/config.py)：运行时配置解析，支持读取环境变量 `TRAFFICDETECT_CONFIG`。

## 新电脑部署

### 1. 建议交付的最小文件
如果你要把项目拷到另一台电脑，只做本地演示，至少保留这些内容：

- `app/`
- `configs/`
- `models/`
- `static/`
- `weights/`
- `requirements.txt`
- `start_web.py`
- `start_web.bat`

如果只是做网页演示，不训练模型，可以不带完整 `datasets/`。

### 2. 创建环境
建议 Python 版本：

- `Python 3.10`
- `Conda/Miniconda`

示例：

```powershell
conda create -n yolov8 python=3.10 -y
conda activate yolov8
```

### 3. 安装依赖
在项目根目录执行：

```powershell
pip install -r requirements.txt
```

### 4. 检查权重
启动前建议确认：

- `weights/best.pt`
- `weights/animal_best.pt`

如果缺少这两个文件，网页虽然能启动，但对应模块无法正常推理。

## 通用部署配置文件
为了方便换电脑部署，项目现在支持通过单独配置文件启动。

推荐做法：

1. 复制 [configs/deploy.example.yaml](/C:/Users/89657/Desktop/yolov8/configs/deploy.example.yaml)
2. 另存为 `configs/local.yaml`
3. 按你的电脑情况修改标题、权重路径目录名、结果目录名等
4. 用 `--config configs/local.yaml` 启动

说明：

- 这个配置文件默认仍使用相对路径，所以项目目录整体拷走后通常不用改源码。
- 如果你在别的电脑上只保留 Web 演示，可以把配置里的数据集相关路径保留默认值，不影响网页检测。

## 启动方式

### 方式一：直接用批处理
Windows 下可直接运行：

```powershell
start_web.bat
```

`start_web.bat` 支持以下环境变量：

- `CONDA_ENV_NAME`：Conda 环境名，默认 `yolov8`
- `TRAFFICDETECT_CONFIG`：配置文件路径，默认 `configs/default.yaml`
- `TRAFFICDETECT_HOST`：监听地址，默认 `0.0.0.0`
- `TRAFFICDETECT_PORT`：端口，默认 `8010`

示例：

```powershell
set CONDA_ENV_NAME=yolov8
set TRAFFICDETECT_CONFIG=C:\Users\YourName\Desktop\yolov8\configs\local.yaml
set TRAFFICDETECT_PORT=8010
start_web.bat
```

### 方式二：命令行启动
使用默认配置：

```powershell
conda activate yolov8
python start_web.py --host 0.0.0.0 --port 8010
```

使用自定义配置：

```powershell
conda activate yolov8
python start_web.py --config configs/local.yaml --host 0.0.0.0 --port 8010
```

如果你更习惯先设环境变量，也可以：

```powershell
conda activate yolov8
$env:TRAFFICDETECT_CONFIG="C:\Users\YourName\Desktop\yolov8\configs\local.yaml"
python -m app.main --host 0.0.0.0 --port 8010
```

启动成功后访问：

- `http://127.0.0.1:8010`
- `http://localhost:8010`

## 本地部署排查
如果网页打不开，按下面顺序检查：

1. 当前是否已激活正确的 Conda 环境。
2. `pip install -r requirements.txt` 是否已经执行成功。
3. `weights/best.pt` 和 `weights/animal_best.pt` 是否存在。
4. 端口 `8010` 是否被占用。
5. `configs/default.yaml` 或你指定的 `configs/local.yaml` 是否存在。
6. `static/`、`app/`、`models/` 目录是否完整。

## 训练与验证

### 模块一训练
```powershell
python -u training/train.py --variant full --epochs 100 --batch 32 --workers 8 --imgsz 640 --device 0 --name train_bdd_full
```

支持的交通模型变体：

- `baseline`
- `p2`
- `p2_cbam`
- `full`

### 模块一验证
```powershell
python -u training/val.py --variant full --device 0
```

### 模块二训练
```powershell
python -u training/train_obstacle.py --epochs 100 --batch 32 --workers 8 --imgsz 960 --device 0 --name train_animal
```

### 模块二验证
```powershell
python -u training/val_obstacle.py --device 0 --name val_animal
```

## 命令行推理

### 交通目标检测
```powershell
python -u inference/predict.py --variant full --source path\\to\\image_or_video --device 0
```

### 道路动物识别
```powershell
python -u inference/predict_obstacle.py --source path\\to\\image_or_folder --device 0
```

## 答辩演示资源
已经筛出一组适合展示的 BDD100K 演示图：

- [datasets/bdd100k_demo](/C:/Users/89657/Desktop/yolov8/datasets/bdd100k_demo)

包含：

- `images/`：原图
- `predictions/`：预测可视化效果图
- `labels/`：对应标签
- `metadata.csv`：评分与类别信息

## 说明

### 模块二接口仍沿用 `obstacle`
虽然展示名称已经改成“道路动物识别”，但部分后端接口路径仍使用 `obstacle` 命名，例如：

- `/api/obstacle/config`
- `/api/obstacle/detect/image`
- `/api/obstacle/detect/batch`

这只是接口历史命名，不影响功能。

### 部署建议
如果你的目标是“换台电脑继续演示”，最稳妥的做法是：

1. 拷贝整个项目目录
2. 保证 `weights/` 完整
3. 新建 Conda 环境
4. `pip install -r requirements.txt`
5. 复制 `configs/deploy.example.yaml` 为 `configs/local.yaml`
6. 用 `python start_web.py --config configs/local.yaml --port 8010` 启动
