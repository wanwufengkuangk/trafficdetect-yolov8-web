const MODULE_ENDPOINTS = {
  traffic: {
    config: "/api/config",
    detectImage: "/api/detect/image",
    websocket: "/api/ws/video",
    uploadText: "上传交通场景图像",
    idleCameraText: "启动实时视频流",
    activeCameraText: "停止实时视频流",
    emptyText: "上传一张交通场景图像，或开启摄像头实时流。",
    emptyResultText: "未检测到目标",
    streamNote: "模块一支持单图检测与实时视频流。",
  },
  obstacle: {
    config: "/api/obstacle/config",
    detectImage: "/api/obstacle/detect/image",
    detectBatch: "/api/obstacle/detect/batch",
    uploadText: "上传道路场景图像",
    folderText: "选择序列文件夹",
    playText: "开始序列播放",
    stopText: "停止序列播放",
    exportText: "导出序列结果",
    emptyText: "上传一张道路场景图像，或选择序列文件夹逐帧识别道路动物。",
    emptyResultText: "未识别到动物",
    streamNote: "模块二支持单图检测、文件夹序列同步回放和批量导出。",
  },
};

const uploadBtn = document.getElementById("upload-btn");
const fileInput = document.getElementById("file-input");
const folderInput = document.getElementById("folder-input");
const folderBtn = document.getElementById("folder-btn");
const sequenceActionRow = document.getElementById("sequence-action-row");
const sequencePlayBtn = document.getElementById("sequence-play-btn");
const sequenceExportBtn = document.getElementById("sequence-export-btn");
const sequenceSelection = document.getElementById("sequence-selection");
const cameraBtn = document.getElementById("camera-btn");
const stageFrame = document.querySelector(".stage-frame");
const resultImage = document.getElementById("result-image");
const emptyState = document.getElementById("empty-state");
const confSlider = document.getElementById("conf-slider");
const iouSlider = document.getElementById("iou-slider");
const confVal = document.getElementById("conf-val");
const iouVal = document.getElementById("iou-val");
const labelsToggle = document.getElementById("labels-toggle");
const classTags = document.getElementById("class-tags");
const resultsList = document.getElementById("results-list");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const engineStatus = document.getElementById("engine-status");
const webTitle = document.getElementById("web-title");
const webSubcopy = document.getElementById("web-subcopy");
const moduleIndicator = document.getElementById("module-indicator");
const hiddenVideo = document.getElementById("hidden-video");
const offscreenCanvas = document.getElementById("offscreen-canvas");
const offscreenContext = offscreenCanvas.getContext("2d", { willReadFrequently: true });
const moduleButtons = Array.from(document.querySelectorAll(".module-btn"));
const metricALabel = document.getElementById("metric-a-label");
const metricAValue = document.getElementById("metric-a-value");
const metricBLabel = document.getElementById("metric-b-label");
const metricBValue = document.getElementById("metric-b-value");
const metricCLabel = document.getElementById("metric-c-label");
const metricCValue = document.getElementById("metric-c-value");
const metricDLabel = document.getElementById("metric-d-label");
const metricDValue = document.getElementById("metric-d-value");
const artifactLinks = document.getElementById("artifact-links");
const previewPanel = document.getElementById("preview-panel");
const previewCaption = document.getElementById("preview-caption");
const sequencePreviewGrid = document.getElementById("sequence-preview-grid");
const streamNote = document.getElementById("stream-note");

const previewController = createPreviewController({
  imageElement: resultImage,
  setMediaVisible,
  urlApi: URL,
});

let websocket = null;
let streamTimer = null;
let frameCounter = 0;
let cameraActive = false;
let currentModule = "traffic";
const moduleConfigs = {};
let sequenceFiles = [];
let sequencePlaying = false;
let sequenceStopRequested = false;
let currentSequenceFrame = 0;
let positiveFrameCount = 0;

function currentModuleMeta() {
  return MODULE_ENDPOINTS[currentModule];
}

function currentModuleConfig() {
  return moduleConfigs[currentModule];
}

function setMediaVisible(visible) {
  stageFrame.classList.toggle("has-media", visible);
  emptyState.style.display = visible ? "none" : "grid";
}

function clearStage() {
  previewController.clear();
}

function updateResultImage(base64Payload) {
  previewController.showRendered(base64Payload);
}

function showFilePreview(file) {
  previewController.showPreview(file);
}

function formatPercent(value) {
  return `${(Number(value || 0) * 100).toFixed(2)}%`;
}

function setMetricSet({ aLabel, aValue, bLabel, bValue, cLabel, cValue, dLabel, dValue }) {
  metricALabel.textContent = aLabel;
  metricAValue.textContent = aValue;
  metricBLabel.textContent = bLabel;
  metricBValue.textContent = bValue;
  metricCLabel.textContent = cLabel;
  metricCValue.textContent = cValue;
  metricDLabel.textContent = dLabel;
  metricDValue.textContent = dValue;
}

function setTrafficMetrics(mode = "IMAGE", detections = [], fps = 0) {
  const maxConfidence = detections.length
    ? Math.max(...detections.map((item) => Number(item.confidence || 0)))
    : 0;
  setMetricSet({
    aLabel: "Mode",
    aValue: mode,
    bLabel: "FPS",
    bValue: String(fps),
    cLabel: "Detections",
    cValue: String(detections.length),
    dLabel: "Max Confidence",
    dValue: formatPercent(maxConfidence),
  });
}

function setObstacleMetrics({ mode, progress, positiveFrames, maxConfidence }) {
  setMetricSet({
    aLabel: "Mode",
    aValue: mode,
    bLabel: "Progress",
    bValue: progress,
    cLabel: "Positive Frames",
    cValue: String(positiveFrames),
    dLabel: "Max Confidence",
    dValue: formatPercent(maxConfidence),
  });
}

function setStatus(text, mode = "idle") {
  statusText.textContent = text;
  engineStatus.textContent = text;
  statusDot.classList.remove("active", "error");
  if (mode === "active") {
    statusDot.classList.add("active");
  }
  if (mode === "error") {
    statusDot.classList.add("error");
  }
}

function renderTrafficResults(detections) {
  resultsList.innerHTML = "";
  if (!detections.length) {
    resultsList.innerHTML = `<div class="result-item"><span>${currentModuleMeta().emptyResultText}</span><span>0</span></div>`;
    return;
  }

  detections.forEach((item) => {
    const node = document.createElement("div");
    node.className = "result-item";
    node.innerHTML = `<span>${item.class_name_zh}</span><strong>${formatPercent(item.confidence)}</strong>`;
    resultsList.appendChild(node);
  });
}

function renderObstacleResults(detections, summary) {
  resultsList.innerHTML = "";

  const summaryRows = [
    ["动物数量", String(summary.detection_count || 0)],
    ["最大置信度", formatPercent(summary.max_confidence)],
  ];
  summaryRows.forEach(([label, value]) => {
    const node = document.createElement("div");
    node.className = "result-item";
    node.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    resultsList.appendChild(node);
  });

  if (!detections.length) {
    const emptyNode = document.createElement("div");
    emptyNode.className = "result-item";
    emptyNode.innerHTML = `<span>${currentModuleMeta().emptyResultText}</span><span>0</span>`;
    resultsList.appendChild(emptyNode);
    return;
  }

  detections.forEach((item, index) => {
    const node = document.createElement("div");
    node.className = "result-item";
    node.innerHTML = `<span>动物 ${index + 1}</span><strong>${formatPercent(item.confidence)}</strong>`;
    resultsList.appendChild(node);
  });
}

function clearArtifacts() {
  artifactLinks.innerHTML = "";
  sequencePreviewGrid.innerHTML = "";
  previewPanel.hidden = true;
}

function renderArtifactLinks(payload) {
  artifactLinks.innerHTML = "";
  const links = [
    ["下载 ZIP", payload.archive_path],
    ["查看 CSV", payload.csv_path],
    ["查看 Summary", payload.summary_path],
    ["查看 Manifest", payload.manifest_path],
  ];
  links.forEach(([label, href]) => {
    const anchor = document.createElement("a");
    anchor.className = "artifact-link";
    anchor.href = href;
    anchor.textContent = label;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    artifactLinks.appendChild(anchor);
  });
}

function renderSequencePreview(preview) {
  sequencePreviewGrid.innerHTML = "";
  if (!preview || !preview.length) {
    previewPanel.hidden = true;
    return;
  }
  previewPanel.hidden = false;
  previewCaption.textContent = `展示 ${preview.length} 帧关键结果`;
  preview.forEach((item) => {
    const card = document.createElement("article");
    card.className = "preview-card";
    card.innerHTML = `
      <img src="${item.rendered_url}" alt="${item.file_name}">
      <div class="preview-card-body">
        <strong>${item.file_name}</strong>
        <p>Detections: ${item.detection_count}</p>
        <p>Max Confidence: ${formatPercent(item.max_confidence)}</p>
      </div>
    `;
    sequencePreviewGrid.appendChild(card);
  });
}

function sortSequenceFiles(files) {
  return [...files]
    .filter((file) => file.type.startsWith("image/") || /\.(png|jpe?g|bmp|webp)$/i.test(file.name))
    .sort((left, right) =>
      resolveSequenceFileName(left).localeCompare(resolveSequenceFileName(right), undefined, {
        numeric: true,
        sensitivity: "base",
      })
    );
}

function resolveSequenceFileName(file) {
  return file.webkitRelativePath || file.name;
}

function updateSequenceControls() {
  const supportsSequence = Boolean(currentModuleConfig()?.supports_sequence_input);
  folderBtn.hidden = !supportsSequence;
  sequenceActionRow.hidden = !supportsSequence;
  sequenceSelection.hidden = !supportsSequence;
  if (!supportsSequence) {
    return;
  }

  folderBtn.textContent = currentModuleMeta().folderText;
  sequencePlayBtn.textContent = sequencePlaying ? currentModuleMeta().stopText : currentModuleMeta().playText;
  sequenceExportBtn.textContent = currentModuleMeta().exportText;
  sequencePlayBtn.disabled = !sequenceFiles.length;
  sequenceExportBtn.disabled = !sequenceFiles.length || sequencePlaying;
  sequenceSelection.textContent = sequenceFiles.length
    ? `已选择 ${sequenceFiles.length} 帧，首帧：${resolveSequenceFileName(sequenceFiles[0])}`
    : "未选择序列文件夹";
}

function updateCameraButton() {
  const supportsStream = Boolean(currentModuleConfig()?.supports_stream);
  cameraBtn.hidden = !supportsStream;
  if (!supportsStream) {
    return;
  }
  cameraBtn.textContent = cameraActive ? currentModuleMeta().activeCameraText : currentModuleMeta().idleCameraText;
}

function applyModuleConfig(module, data) {
  currentModule = module;
  moduleConfigs[module] = data;
  webTitle.textContent = data.web_title;
  webSubcopy.textContent = data.module_subtitle;
  moduleIndicator.textContent = data.module_title;
  confSlider.value = data.default_conf;
  iouSlider.value = data.default_iou;
  confVal.textContent = Number(data.default_conf).toFixed(2);
  iouVal.textContent = Number(data.default_iou).toFixed(2);
  uploadBtn.textContent = currentModuleMeta().uploadText;
  emptyState.querySelector("p").textContent = currentModuleMeta().emptyText;
  streamNote.textContent = currentModuleMeta().streamNote;

  classTags.innerHTML = "";
  data.ch_classes.forEach((label) => {
    const node = document.createElement("span");
    node.className = "tag-item";
    node.textContent = label;
    classTags.appendChild(node);
  });

  moduleButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.module === module);
  });
  updateCameraButton();
  updateSequenceControls();
}

async function loadModuleConfig(module) {
  if (moduleConfigs[module]) {
    return moduleConfigs[module];
  }
  const response = await fetch(MODULE_ENDPOINTS[module].config);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "failed to load module config");
  }
  moduleConfigs[module] = data;
  return data;
}

function stopSequencePlayback() {
  if (sequencePlaying) {
    sequenceStopRequested = true;
    setStatus("STOPPING", "active");
  }
}

function resetSequenceState(clearFiles = true) {
  stopSequencePlayback();
  sequencePlaying = false;
  sequenceStopRequested = false;
  currentSequenceFrame = 0;
  positiveFrameCount = 0;
  if (clearFiles) {
    sequenceFiles = [];
    folderInput.value = "";
  }
  updateSequenceControls();
}

function resetUiForModuleSwitch() {
  stopCamera();
  resetSequenceState(true);
  clearArtifacts();
  clearStage();
  setStatus("READY", "active");
}

async function switchModule(module) {
  if (module === currentModule) {
    return;
  }
  const config = await loadModuleConfig(module);
  resetUiForModuleSwitch();
  applyModuleConfig(module, config);
  if (module === "traffic") {
    renderTrafficResults([]);
    setTrafficMetrics("IMAGE", [], 0);
  } else {
    renderObstacleResults([], {
      detection_count: 0,
      max_confidence: 0,
    });
    setObstacleMetrics({
      mode: "IMAGE",
      progress: "-",
      positiveFrames: 0,
      maxConfidence: 0,
    });
  }
}

async function detectImage(file) {
  stopCamera();
  stopSequencePlayback();
  showFilePreview(file);
  setStatus("PROCESSING", "active");

  const form = new FormData();
  form.append("file", file);
  form.append("conf", confSlider.value);
  form.append("iou", iouSlider.value);
  form.append("show_labels", labelsToggle.checked);

  try {
    const response = await fetch(currentModuleMeta().detectImage, { method: "POST", body: form });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "image inference failed");
    }

    updateResultImage(payload.image);
    if (currentModule === "traffic") {
      renderTrafficResults(payload.detections || []);
      setTrafficMetrics("IMAGE", payload.detections || [], 0);
    } else {
      renderObstacleResults(payload.detections || [], payload.summary || {});
      setObstacleMetrics({
        mode: "IMAGE",
        progress: "1/1",
        positiveFrames: (payload.summary?.detection_count || 0) > 0 ? 1 : 0,
        maxConfidence: payload.summary?.max_confidence || 0,
      });
    }
    setStatus("READY", "active");
  } catch (error) {
    if (currentModule === "traffic") {
      renderTrafficResults([]);
      setTrafficMetrics("IMAGE", [], 0);
    } else {
      renderObstacleResults([], {
        detection_count: 0,
        max_confidence: 0,
      });
      setObstacleMetrics({
        mode: "IMAGE",
        progress: "1/1",
        positiveFrames: 0,
        maxConfidence: 0,
      });
    }
    setStatus(error.message, "error");
  }
}

function syncCanvasSize() {
  if (!hiddenVideo.videoWidth || !hiddenVideo.videoHeight) {
    return false;
  }
  if (offscreenCanvas.width === hiddenVideo.videoWidth && offscreenCanvas.height === hiddenVideo.videoHeight) {
    return true;
  }
  offscreenCanvas.width = hiddenVideo.videoWidth;
  offscreenCanvas.height = hiddenVideo.videoHeight;
  return true;
}

async function waitForVideoReady() {
  if (hiddenVideo.readyState >= HTMLMediaElement.HAVE_METADATA && hiddenVideo.videoWidth && hiddenVideo.videoHeight) {
    await hiddenVideo.play();
    syncCanvasSize();
    return;
  }

  await new Promise((resolve, reject) => {
    const cleanup = () => {
      hiddenVideo.removeEventListener("loadedmetadata", onLoadedMetadata);
      hiddenVideo.removeEventListener("error", onError);
    };

    const onLoadedMetadata = async () => {
      cleanup();
      try {
        await hiddenVideo.play();
        syncCanvasSize();
        resolve();
      } catch (error) {
        reject(error);
      }
    };

    const onError = () => {
      cleanup();
      reject(new Error("camera stream failed to initialize"));
    };

    hiddenVideo.addEventListener("loadedmetadata", onLoadedMetadata, { once: true });
    hiddenVideo.addEventListener("error", onError, { once: true });
  });
}

function stopCamera() {
  cameraActive = false;
  if (streamTimer) {
    clearInterval(streamTimer);
    streamTimer = null;
  }
  if (websocket) {
    websocket.close();
    websocket = null;
  }
  if (hiddenVideo.srcObject) {
    hiddenVideo.srcObject.getTracks().forEach((track) => track.stop());
    hiddenVideo.srcObject = null;
  }
  hiddenVideo.pause();
  offscreenCanvas.width = 0;
  offscreenCanvas.height = 0;
  updateCameraButton();
}

function handleSocketMessage(rawPayload) {
  if (typeof rawPayload === "string" && rawPayload.startsWith("{")) {
    try {
      const parsed = JSON.parse(rawPayload);
      if (parsed.error) {
        setStatus(parsed.error, "error");
        stopCamera();
        return;
      }
    } catch (_error) {
      // Ignore non-JSON payloads and treat them as base64 frames.
    }
  }
  updateResultImage(rawPayload);
  frameCounter += 1;
}

async function startCamera() {
  if (!currentModuleConfig()?.supports_stream) {
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: 960 }, height: { ideal: 540 }, facingMode: "environment" },
    audio: false,
  });
  hiddenVideo.srcObject = stream;
  await waitForVideoReady();
  cameraActive = true;
  updateCameraButton();
  setTrafficMetrics("STREAM", [], 0);
  setStatus("STREAMING", "active");

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  websocket = new WebSocket(
    `${protocol}//${window.location.host}${currentModuleMeta().websocket}?conf=${confSlider.value}&iou=${iouSlider.value}&show_labels=${labelsToggle.checked}`
  );

  websocket.onopen = () => {
    streamTimer = setInterval(() => {
      if (!cameraActive || websocket.readyState !== WebSocket.OPEN) {
        return;
      }
      if (hiddenVideo.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
        return;
      }
      if (!syncCanvasSize()) {
        return;
      }
      offscreenContext.drawImage(hiddenVideo, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
      offscreenCanvas.toBlob((blob) => {
        if (blob) {
          websocket.send(blob);
        }
      }, "image/jpeg", 0.75);
    }, 70);
  };

  websocket.onmessage = (event) => {
    handleSocketMessage(event.data);
  };

  websocket.onerror = () => {
    setStatus("stream error", "error");
  };

  websocket.onclose = () => {
    if (cameraActive) {
      stopCamera();
    }
  };
}

async function playObstacleSequence() {
  if (!sequenceFiles.length || sequencePlaying) {
    return;
  }

  stopCamera();
  clearArtifacts();
  sequencePlaying = true;
  sequenceStopRequested = false;
  currentSequenceFrame = 0;
  positiveFrameCount = 0;
  updateSequenceControls();
  setStatus("SEQUENCE PLAYBACK", "active");

  try {
    for (const file of sequenceFiles) {
      if (sequenceStopRequested) {
        break;
      }
      currentSequenceFrame += 1;
      showFilePreview(file);

      const form = new FormData();
      form.append("file", file);
      form.append("conf", confSlider.value);
      form.append("iou", iouSlider.value);
      form.append("show_labels", labelsToggle.checked);

      const response = await fetch(currentModuleMeta().detectImage, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "sequence inference failed");
      }

      updateResultImage(payload.image);
      renderObstacleResults(payload.detections || [], payload.summary || {});
      if ((payload.summary?.detection_count || 0) > 0) {
        positiveFrameCount += 1;
      }
      setObstacleMetrics({
        mode: "SEQUENCE",
        progress: `${currentSequenceFrame}/${sequenceFiles.length}`,
        positiveFrames: positiveFrameCount,
        maxConfidence: payload.summary?.max_confidence || 0,
      });
    }

    if (sequenceStopRequested) {
      setStatus("SEQUENCE STOPPED", "active");
    } else {
      setStatus("READY", "active");
    }
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    sequencePlaying = false;
    sequenceStopRequested = false;
    updateSequenceControls();
  }
}

async function exportObstacleSequence() {
  if (!sequenceFiles.length || sequencePlaying) {
    return;
  }

  clearArtifacts();
  setStatus("EXPORTING", "active");
  const form = new FormData();
  sequenceFiles.forEach((file) => {
    form.append("files", file, resolveSequenceFileName(file));
  });
  form.append("conf", confSlider.value);
  form.append("iou", iouSlider.value);
  form.append("show_labels", labelsToggle.checked);

  try {
    const response = await fetch(currentModuleMeta().detectBatch, { method: "POST", body: form });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "sequence export failed");
    }
    renderArtifactLinks(payload);
    renderSequencePreview(payload.preview || []);
    setStatus("EXPORT READY", "active");
  } catch (error) {
    setStatus(error.message, "error");
  }
}

uploadBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  if (file) {
    detectImage(file);
  }
});

folderBtn.addEventListener("click", () => folderInput.click());
folderInput.addEventListener("change", (event) => {
  sequenceFiles = sortSequenceFiles(Array.from(event.target.files || []));
  resetSequenceState(false);
  updateSequenceControls();
});

sequencePlayBtn.addEventListener("click", async () => {
  if (sequencePlaying) {
    stopSequencePlayback();
    return;
  }
  await playObstacleSequence();
});

sequenceExportBtn.addEventListener("click", async () => {
  await exportObstacleSequence();
});

cameraBtn.addEventListener("click", async () => {
  if (cameraActive) {
    stopCamera();
    setTrafficMetrics("IMAGE", [], 0);
    setStatus("READY", "active");
    return;
  }
  try {
    await startCamera();
  } catch (error) {
    stopCamera();
    setStatus(error.message, "error");
  }
});

confSlider.addEventListener("input", () => {
  confVal.textContent = Number(confSlider.value).toFixed(2);
});

iouSlider.addEventListener("input", () => {
  iouVal.textContent = Number(iouSlider.value).toFixed(2);
});

moduleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    switchModule(button.dataset.module).catch((error) => {
      setStatus(error.message, "error");
    });
  });
});

setInterval(() => {
  if (currentModule === "traffic" && cameraActive) {
    setTrafficMetrics("STREAM", [], frameCounter);
  }
  frameCounter = 0;
}, 1000);

async function initializeApp() {
  const trafficConfig = await loadModuleConfig("traffic");
  applyModuleConfig("traffic", trafficConfig);
  renderTrafficResults([]);
  clearArtifacts();
  clearStage();
  setTrafficMetrics("IMAGE", [], 0);
  setStatus("READY", "active");
}

initializeApp().catch((error) => {
  setStatus(error.message, "error");
});
