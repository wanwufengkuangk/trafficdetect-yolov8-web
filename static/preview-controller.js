(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
  root.createPreviewController = api.createPreviewController;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function createPreviewController({ imageElement, setMediaVisible, urlApi }) {
    let previewUrl = null;

    function revokePreviewUrl() {
      if (previewUrl) {
        urlApi.revokeObjectURL(previewUrl);
        previewUrl = null;
      }
    }

    return {
      showPreview(file) {
        revokePreviewUrl();
        previewUrl = urlApi.createObjectURL(file);
        imageElement.src = previewUrl;
        setMediaVisible(true);
      },
      showRendered(base64Payload) {
        revokePreviewUrl();
        imageElement.src = `data:image/jpeg;base64,${base64Payload}`;
        setMediaVisible(true);
      },
      clear() {
        revokePreviewUrl();
        imageElement.removeAttribute("src");
        setMediaVisible(false);
      },
    };
  }

  return { createPreviewController };
});
