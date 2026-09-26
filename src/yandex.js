let sdk = null;
let sdkInitPromise = null;
let sdkScriptPromise = null;
let readySent = false;
let loadingReadySent = false;
let gameplayActive = false;
let sdkGameplayActive = false;
let platformPauseActive = false;
let gameplayBlocked = false;
let sdkListenersInstalled = false;
let fullscreenAdRequestActive = false;
let pauseRuntimeCallback = () => {};
let resumeRuntimeCallback = () => {};
const sdkReadySubscribers = new Set();

const SDK_INIT_TIMEOUT_MS = 8000;
const AD_CALLBACK_START_TIMEOUT_MS = 15000;
const AD_CALLBACK_CLOSE_TIMEOUT_MS = 300000;
const SDK_SCRIPT_ID = "yandex-games-sdk";
const YANDEX_DEBUG =
  new URLSearchParams(window.location.search).get("tpt-debug") === "1";

function debugInfo(...args) {
  if (YANDEX_DEBUG) {
    console.info(...args);
  }
}

function loadYandexSDKScript() {
  if (typeof window.YaGames !== "undefined") {
    return Promise.resolve(true);
  }

  if (sdkScriptPromise) {
    return sdkScriptPromise;
  }

  sdkScriptPromise = new Promise((resolve) => {
    let settled = false;
    const finish = (available) => {
      if (settled) {
        return;
      }
      settled = true;
      resolve(Boolean(available));
    };

    let script = document.getElementById(SDK_SCRIPT_ID);
    const created = !script;

    if (!script) {
      script = document.createElement("script");
      script.id = SDK_SCRIPT_ID;
      script.src = "/sdk.js";
      script.async = true;
    }

    script.addEventListener(
      "load",
      () => finish(typeof window.YaGames !== "undefined"),
      { once: true }
    );
    script.addEventListener("error", () => finish(false), { once: true });

    // If another integration supplied the script before this module ran,
    // YaGames may already be available even though its load event is gone.
    if (typeof window.YaGames !== "undefined") {
      finish(true);
      return;
    }

    if (created) {
      document.head.appendChild(script);
    }
  });

  return sdkScriptPromise;
}

function sendLoadingReady(currentSDK) {
  if (!currentSDK || !readySent || loadingReadySent) {
    return;
  }

  try {
    currentSDK.features?.LoadingAPI?.ready();
    loadingReadySent = true;
    debugInfo("[Yandex] LoadingAPI.ready sent.");
  } catch (error) {
    debugInfo("[Yandex] LoadingAPI.ready failed.", error);
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
    debugInfo("[Yandex] GameplayAPI.start failed.", error);
  }
}

function stopGameplayOnSDK(currentSDK) {
  if (!currentSDK || !sdkGameplayActive) {
    return;
  }

  try {
    currentSDK.features?.GameplayAPI?.stop();
  } catch (error) {
    debugInfo("[Yandex] GameplayAPI.stop failed.", error);
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

    // Yandex applies the platform pause automatically. Keep sdkGameplayActive
    // unchanged here: for an SDK that was already active, Yandex also owns the
    // matching resume. A late SDK adopted during the pause never sets this flag.
    pauseRuntimeCallback();
    debugInfo("[Yandex] game_api_pause");
  });

  currentSDK.on("game_api_resume", () => {
    platformPauseActive = false;

    if (!document.hidden) {
      resumeRuntimeCallback();
    }

    if (readySent && !document.hidden && !gameplayBlocked) {
      if (!gameplayActive) {
        void gameplayStart();
      } else if (!sdkGameplayActive) {
        // This is the late-adoption case: the SDK appeared while platform
        // pause was active, so Yandex had no prior GameplayAPI.start to resume.
        startGameplayOnSDK(currentSDK);
      }
    }

    debugInfo("[Yandex] game_api_resume");
  });
}

function notifySDKReady(currentSDK, late) {
  for (const callback of sdkReadySubscribers) {
    Promise.resolve()
      .then(() => callback(currentSDK, { late }))
      .catch((error) => {
        console.error("[Yandex] SDK-ready subscriber failed.", error);
      });
  }
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
    debugInfo("[Yandex] SDK initialized after startup timeout; state reconciled.");
  } else {
    debugInfo("[Yandex] SDK initialized.");
  }

  sendLoadingReady(currentSDK);
  startGameplayOnSDK(currentSDK);
  notifySDKReady(currentSDK, late);
  return currentSDK;
}

export function onYandexSDKReady(callback) {
  if (typeof callback !== "function") {
    return () => {};
  }

  sdkReadySubscribers.add(callback);
  if (sdk) {
    Promise.resolve()
      .then(() => callback(sdk, { late: false }))
      .catch((error) => {
        console.error("[Yandex] SDK-ready subscriber failed.", error);
      });
  }

  return () => {
    sdkReadySubscribers.delete(callback);
  };
}

export async function initYandexSDK() {
  if (sdkInitPromise) {
    return sdkInitPromise;
  }

  sdkInitPromise = (async () => {
    let timeoutId = null;
    const rawInitPromise = loadYandexSDKScript().then((available) => {
      if (!available || typeof window.YaGames === "undefined") {
        return null;
      }
      return window.YaGames.init();
    });

    try {
      const timeoutPromise = new Promise((_, reject) => {
        timeoutId = window.setTimeout(() => {
          const error = new Error(
            `Yandex SDK loading/initialization timed out after ${SDK_INIT_TIMEOUT_MS} ms`
          );
          error.name = "YandexSDKTimeoutError";
          reject(error);
        }, SDK_INIT_TIMEOUT_MS);
      });

      const currentSDK = await Promise.race([rawInitPromise, timeoutPromise]);
      if (!currentSDK) {
        debugInfo("[Yandex] SDK is unavailable; using local development mode.");
        return null;
      }
      return adoptSDK(currentSDK);
    } catch (error) {
      if (error?.name === "YandexSDKTimeoutError") {
        // Timeout is an expected startup fallback: the engine continues
        // immediately and adopts the SDK later if initialization completes.
        // Keep normal production console clean; expose the detail on demand.
        debugInfo(
          "[Yandex] SDK loading/initialization timed out; continuing while it finishes."
        );

        // The script request and YaGames.init() remain alive after the startup
        // fallback. If either completes later, adopt the SDK without reloading.
        void rawInitPromise
          .then((currentSDK) => {
            if (currentSDK) {
              adoptSDK(currentSDK, true);
            }
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

  // Native presentation readiness must not wait for SDK loading/initialization.
  // If Yandex is already adopted, notify it immediately; otherwise adoptSDK()
  // reconciles this logical ready state when the SDK arrives later.
  readySent = true;
  sendLoadingReady(sdk || window.ysdk || null);
  void initYandexSDK();
}

export async function gameplayStart() {
  if (gameplayActive || document.hidden || platformPauseActive || gameplayBlocked) {
    return;
  }

  // Keep the local gameplay state independent of SDK latency. A late SDK is
  // reconciled by adoptSDK(), which starts GameplayAPI only when appropriate.
  gameplayActive = true;
  startGameplayOnSDK(sdk || window.ysdk || null);
  void initYandexSDK();
}

export async function gameplayStop() {
  if (!gameplayActive) {
    return;
  }

  // Stopping gameplay is purely a local state transition. Do not start or
  // await SDK initialization just to stop; an already adopted SDK is updated
  // synchronously, and a future SDK will observe gameplayActive=false.
  gameplayActive = false;
  stopGameplayOnSDK(sdk || window.ysdk || null);
}

export async function canShowFullscreenAd() {
  const currentSDK = await initYandexSDK();
  return typeof currentSDK?.adv?.showFullscreenAdv === "function";
}

export async function showFullscreenAd() {
  if (fullscreenAdRequestActive) {
    return false;
  }

  const currentSDK = await initYandexSDK();
  const show = currentSDK?.adv?.showFullscreenAdv;
  if (typeof show !== "function") {
    debugInfo("[Yandex] Fullscreen advertising is unavailable.");
    return false;
  }

  fullscreenAdRequestActive = true;
  return new Promise((resolve) => {
    let settled = false;
    let watchdogId = window.setTimeout(() => {
      watchdogId = null;
      debugInfo("[Yandex] Fullscreen ad produced no initial callback; releasing request.");
      finish(false);
    }, AD_CALLBACK_START_TIMEOUT_MS);

    const armCloseWatchdog = () => {
      if (settled) {
        return;
      }
      if (watchdogId !== null) {
        window.clearTimeout(watchdogId);
      }
      watchdogId = window.setTimeout(() => {
        watchdogId = null;
        debugInfo("[Yandex] Fullscreen ad did not close in time; releasing request.");
        finish(false);
      }, AD_CALLBACK_CLOSE_TIMEOUT_MS);
    };

    const finish = (wasShown) => {
      if (settled) {
        return;
      }
      settled = true;
      if (watchdogId !== null) {
        window.clearTimeout(watchdogId);
        watchdogId = null;
      }
      fullscreenAdRequestActive = false;
      resolve(Boolean(wasShown));
    };

    try {
      show.call(currentSDK.adv, {
        callbacks: {
          onOpen() {
            debugInfo("[Yandex] Fullscreen ad opened.");
            armCloseWatchdog();
          },
          onClose(wasShown) {
            debugInfo("[Yandex] Fullscreen ad closed.", { wasShown });
            finish(wasShown);
          },
          onError(error) {
            debugInfo("[Yandex] Fullscreen ad failed.", error);
            finish(false);
          },
          onOffline() {
            debugInfo("[Yandex] Fullscreen ad skipped while offline.");
            finish(false);
          }
        }
      });
    } catch (error) {
      debugInfo("[Yandex] Fullscreen ad call failed.", error);
      finish(false);
    }
  });
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
    navigator.languages?.[0] ||
    navigator.language ||
    document.documentElement.lang ||
    "en";

  const normalized = String(language).toLowerCase().split("-")[0];
  return normalized === "ru" ? "ru" : "en";
}
