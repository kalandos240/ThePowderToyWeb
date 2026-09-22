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

      // Yandex automatically applies GameplayAPI.stop() for this event.
      // Keep our own gameplayActive flag unchanged so an explicit stop made
      // by the game is not accidentally forgotten on resume.
      pauseRuntime();
      console.info("[Yandex] game_api_pause");
    });

    currentSDK.on("game_api_resume", () => {
      platformPauseActive = false;

      // Yandex automatically restores gameplay markup only when appropriate.
      // We only resume the native loop here; our explicit markup state remains
      // controlled by gameplayStart()/gameplayStop().
      resumeRuntime();
      console.info("[Yandex] game_api_resume");
    });
  });
}


export function getYandexLanguage(currentSDK = sdk) {
  const language = currentSDK?.environment?.i18n?.lang;
  return typeof language === "string" && language.length > 0
    ? language.toLowerCase()
    : "en";
}
