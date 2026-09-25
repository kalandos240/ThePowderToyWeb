let sdk = null;
let sdkInitPromise = null;
let readySent = false;
let loadingReadySent = false;
let gameplayActive = false;
let sdkGameplayActive = false;
let platformPauseActive = false;
let gameplayBlocked = false;
let sdkListenersInstalled = false;
let pauseRuntimeCallback = () => {};
let resumeRuntimeCallback = () => {};

const SDK_INIT_TIMEOUT_MS = 8000;

function sendLoadingReady(currentSDK) {
  if (!currentSDK || !readySent || loadingReadySent) {
    return;
  }

  try {
    currentSDK.features?.LoadingAPI?.ready();
    loadingReadySent = true;
    console.info("[Yandex] LoadingAPI.ready sent.");
  } catch (error) {
    console.error("[Yandex] LoadingAPI.ready failed.", error);
  }
}

function startGameplayOnSDK(currentSDK) {
  if (
    !currentSDK ||
    sdkGameplayActive ||
    !gameplayActive ||
    document.hidden ||
    platformPauseActive ||
    gameplayBlocked
  ) {
    return;
  }

  try {
    currentSDK.features?.GameplayAPI?.start();
    sdkGameplayActive = true;
  } catch (error) {
    console.error("[Yandex] GameplayAPI.start failed.", error);
  }
}

function stopGameplayOnSDK(currentSDK) {
  if (!currentSDK || !sdkGameplayActive) {
    return;
  }

  try {
    currentSDK.features?.GameplayAPI?.stop();
  } catch (error) {
    console.error("[Yandex] GameplayAPI.stop failed.", error);
  } finally {
    sdkGameplayActive = false;
  }
}

function installSDKPauseListeners(currentSDK) {
  if (!currentSDK?.on || sdkListenersInstalled) {
    return;
  }

  sdkListenersInstalled = true;

  currentSDK.on("game_api_pause", () => {
    platformPauseActive = true;

    // Yandex applies GameplayAPI.stop() automatically for this event.
    // Preserve the logical gameplay state, but mark the SDK side stopped so
    // resume can explicitly reconcile it when required.
    sdkGameplayActive = false;
    pauseRuntimeCallback();
    console.info("[Yandex] game_api_pause");
  });

  currentSDK.on("game_api_resume", () => {
    platformPauseActive = false;

    if (!document.hidden) {
      resumeRuntimeCallback();
    }

    if (readySent && !document.hidden && !gameplayBlocked) {
      if (gameplayActive) {
        startGameplayOnSDK(currentSDK);
      } else {
        void gameplayStart();
      }
    }

    console.info("[Yandex] game_api_resume");
  });
}

function adoptSDK(currentSDK, late = false) {
  if (!currentSDK) {
    return null;
  }

  sdk = currentSDK;
  sdkInitPromise = Promise.resolve(currentSDK);
  window.ysdk = currentSDK;
  installSDKPauseListeners(currentSDK);

  if (late) {
    console.info("[Yandex] SDK initialized after startup timeout; state reconciled.");
  } else {
    console.info("[Yandex] SDK initialized.");
  }

  sendLoadingReady(currentSDK);
  startGameplayOnSDK(currentSDK);
  return currentSDK;
}

export async function initYandexSDK() {
  if (sdkInitPromise) {
    return sdkInitPromise;
  }

  sdkInitPromise = (async () => {
    if (typeof window.YaGames === "undefined") {
      console.info("[Yandex] SDK is unavailable; using local development mode.");
      return null;
    }

    let timeoutId = null;
    const rawInitPromise = Promise.resolve().then(() => window.YaGames.init());

    try {
      const timeoutPromise = new Promise((_, reject) => {
        timeoutId = window.setTimeout(() => {
          const error = new Error(
            `Yandex SDK initialization timed out after ${SDK_INIT_TIMEOUT_MS} ms`
          );
          error.name = "YandexSDKTimeoutError";
          reject(error);
        }, SDK_INIT_TIMEOUT_MS);
      });

      const currentSDK = await Promise.race([rawInitPromise, timeoutPromise]);
      return adoptSDK(currentSDK);
    } catch (error) {
      if (error?.name === "YandexSDKTimeoutError") {
        console.warn("[Yandex] SDK initialization timed out; continuing while it finishes.");

        // Do not block the game on a slow SDK, but keep the original init
        // operation alive. If it eventually succeeds, attach it and reconcile
        // LoadingAPI/GameplayAPI with the already-running game.
        void rawInitPromise
          .then((currentSDK) => {
            adoptSDK(currentSDK, true);
          })
          .catch((lateError) => {
            console.error("[Yandex] Late SDK initialization failed.", lateError);
          });
      } else {
        console.error("[Yandex] SDK initialization failed.", error);
      }
      return null;
    } finally {
      if (timeoutId !== null) {
        window.clearTimeout(timeoutId);
      }
    }
  })();

  return sdkInitPromise;
}

export async function signalGameReady() {
  if (readySent) {
    return;
  }

  const currentSDK = await initYandexSDK();
  readySent = true;
  sendLoadingReady(currentSDK);
}

export async function gameplayStart() {
  if (gameplayActive || document.hidden || platformPauseActive || gameplayBlocked) {
    return;
  }

  const currentSDK = await initYandexSDK();
  gameplayActive = true;
  startGameplayOnSDK(currentSDK);
}

export async function gameplayStop() {
  if (!gameplayActive) {
    return;
  }

  const currentSDK = await initYandexSDK();
  gameplayActive = false;
  stopGameplayOnSDK(currentSDK);
}

export function setGameplayBlocked(blocked) {
  const next = Boolean(blocked);
  if (gameplayBlocked === next) {
    return;
  }

  gameplayBlocked = next;
  if (gameplayBlocked) {
    void gameplayStop();
  } else if (readySent && !document.hidden && !platformPauseActive) {
    void gameplayStart();
  }
}

export function installPlatformPauseBridge({ onPause, onResume } = {}) {
  pauseRuntimeCallback = () => {
    onPause?.();
  };
  resumeRuntimeCallback = () => {
    onResume?.();
  };

  const pauseRuntime = () => {
    pauseRuntimeCallback();
  };

  const resumeRuntime = () => {
    if (!document.hidden && !platformPauseActive) {
      resumeRuntimeCallback();
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

  // A page restored from the browser back/forward cache may receive pageshow
  // without a fresh boot. Resume the native loop and gameplay markup here so
  // returning through browser history cannot leave the simulation frozen.
  window.addEventListener("pageshow", () => {
    resumeRuntime();
    if (readySent) {
      void gameplayStart();
    }
  });

  // SDK event handlers are installed by adoptSDK(), including when the SDK
  // resolves only after the startup timeout.
  void initYandexSDK();
}


export function getYandexLanguage(currentSDK = sdk) {
  const language =
    currentSDK?.environment?.i18n?.lang ||
    document.documentElement.lang ||
    navigator.language ||
    "en";

  const normalized = String(language).toLowerCase().split("-")[0];
  return normalized === "ru" ? "ru" : "en";
}
