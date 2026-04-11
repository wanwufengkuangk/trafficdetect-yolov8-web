const uploadBtn = document.getElementById("upload-btn");
const fileInput = document.getElementById("file-input");
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
const fpsCounter = document.getElementById("fps-counter");
const modeLabel = document.getElementById("mode-label");
const webTitle = document.getElementById("web-title");
const hiddenVideo = document.getElementById("hidden-video");
const offscreenCanvas = document.getElementById("offscreen-canvas");
const offscreenContext = offscreenCanvas.getContext("2d", { willReadFrequently: true });

let websocket = null;
let streamTimer = null;
let frameCounter = 0;
let cameraActive = false;

function setMediaVisible(visible) {
  stageFrame.classList.toggle("has-media", visible);
  emptyState.style.display = visible ? "none" : "grid";
}

function updateResultImage(base64Payload) {
  resultImage.src = `data:image/jpeg;base64,${base64Payload}`;
  setMediaVisible(true);
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

function renderDetections(detections) {
  resultsList.innerHTML = "";
  if (!detections.length) {
    resultsList.innerHTML = "<div class='result-item'><span>未检测到目标</span><span>0</span></div>";
    return;
  }

  detections.forEach((item) => {
    const node = document.createElement("div");
    node.className = "result-item";
    node.innerHTML = `<span>${item.class_name_zh}</span><strong>${(item.confidence * 100).toFixed(1)}%</strong>`;
    resultsList.appendChild(node);
  });
}

async function loadConfig() {
  const response = await fetch("/api/config");
  const data = await response.json();
  webTitle.textContent = data.web_title;
  confSlider.value = data.default_conf;
  iouSlider.value = data.default_iou;
  confVal.textContent = Number(data.default_conf).toFixed(2);
  iouVal.textContent = Number(data.default_iou).toFixed(2);

  classTags.innerHTML = "";
  data.ch_classes.forEach((label) => {
    const node = document.createElement("span");
    node.className = "tag-item";
    node.textContent = label;
    classTags.appendChild(node);
  });

  setStatus("READY", "active");
}

async function detectImage(file) {
  stopCamera();
  modeLabel.textContent = "IMAGE";
  const form = new FormData();
  form.append("file", file);
  form.append("conf", confSlider.value);
  form.append("iou", iouSlider.value);
  form.append("show_labels", labelsToggle.checked);

  setStatus("PROCESSING", "active");
  try {
    const response = await fetch("/api/detect/image", { method: "POST", body: form });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "image detection failed");
    }
    updateResultImage(payload.image);
    renderDetections(payload.detections);
    setStatus("READY", "active");
  } catch (error) {
    renderDetections([]);
    setStatus(error.message, "error");
  }
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
  cameraBtn.textContent = "启动实时视频流";
}

async function startCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: 960 }, height: { ideal: 540 }, facingMode: "environment" },
    audio: false,
  });
  hiddenVideo.srcObject = stream;
  await waitForVideoReady();
  cameraActive = true;
  cameraBtn.textContent = "停止实时视频流";
  modeLabel.textContent = "STREAM";
  setStatus("STREAMING", "active");

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  websocket = new WebSocket(
    `${protocol}//${window.location.host}/api/ws/video?conf=${confSlider.value}&iou=${iouSlider.value}&show_labels=${labelsToggle.checked}`
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
    updateResultImage(event.data);
    frameCounter += 1;
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

uploadBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  if (file) {
    detectImage(file);
  }
});

cameraBtn.addEventListener("click", async () => {
  if (cameraActive) {
    stopCamera();
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

setInterval(() => {
  fpsCounter.textContent = String(frameCounter);
  frameCounter = 0;
}, 1000);

loadConfig().catch((error) => {
  setStatus(error.message, "error");
});
