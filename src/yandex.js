let sdk = null;
let sdkInitPromise = null;
let readySent = false;
let gameplayActive = false;
let platformPauseActive = false;

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
  if (gameplayActive || document.hidden || platformPauseActive) {
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

export function installPlatformPauseBridge({ onPause, onResume } = {}) {
  const pauseRuntime = () => {
    onPause?.();
  };

  const resumeRuntime = () => {
    if (!document.hidden && !platformPauseActive) {
      onResume?.();
    }
  };

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      pauseRuntime();
      void gameplayStop();
    } else {
      resumeRuntime();
      if (readySent) {
        void gameplayStart();
      }
    }
  });

  window.addEventListener("pagehide", () => {
    pauseRuntime();
    void gameplayStop();
  });

  void initYandexSDK().then((currentSDK) => {
    if (!currentSDK?.on) {
      return;
    }

    currentSDK.on("game_api_pause", () => {
      platformPauseActive = true;
      gameplayActive = false;
      pauseRuntime();
      console.info("[Yandex] game_api_pause");
    });

    currentSDK.on("game_api_resume", () => {
      platformPauseActive = false;
      if (readySent && !document.hidden) {
        gameplayActive = true;
      }
      resumeRuntime();
      console.info("[Yandex] game_api_resume");
    });
  });
}
