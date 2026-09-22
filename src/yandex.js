let sdk = null;
let sdkInitPromise = null;
let readySent = false;
let gameplayActive = false;

export async function initYandexSDK() {
  if (sdkInitPromise) {
    return sdkInitPromise;
  }

  sdkInitPromise = (async () => {
    if (typeof window.YaGames === "undefined") {
      console.info("[Yandex] SDK is unavailable; using local development mode.");
      return null;
    }

    try {
      sdk = await window.YaGames.init();
      window.ysdk = sdk;
      console.info("[Yandex] SDK initialized.");
      return sdk;
    } catch (error) {
      console.error("[Yandex] SDK initialization failed.", error);
      return null;
    }
  })();

  return sdkInitPromise;
}

export async function signalGameReady() {
  if (readySent) {
    return;
  }

  const currentSDK = await initYandexSDK();
  if (!currentSDK) {
    readySent = true;
    return;
  }

  try {
    currentSDK.features?.LoadingAPI?.ready();
    readySent = true;
    console.info("[Yandex] LoadingAPI.ready sent.");
  } catch (error) {
    console.error("[Yandex] LoadingAPI.ready failed.", error);
  }
}

export async function gameplayStart() {
  if (gameplayActive || document.hidden) {
    return;
  }

  const currentSDK = await initYandexSDK();
  if (!currentSDK) {
    gameplayActive = true;
    return;
  }

  try {
    currentSDK.features?.GameplayAPI?.start();
    gameplayActive = true;
  } catch (error) {
    console.error("[Yandex] GameplayAPI.start failed.", error);
  }
}

export async function gameplayStop() {
  if (!gameplayActive) {
    return;
  }

  const currentSDK = await initYandexSDK();
  if (!currentSDK) {
    gameplayActive = false;
    return;
  }

  try {
    currentSDK.features?.GameplayAPI?.stop();
  } catch (error) {
    console.error("[Yandex] GameplayAPI.stop failed.", error);
  } finally {
    gameplayActive = false;
  }
}

export function installGameplayVisibilityBridge() {
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      void gameplayStop();
    } else if (readySent) {
      void gameplayStart();
    }
  });

  window.addEventListener("pagehide", () => {
    void gameplayStop();
  });
}
