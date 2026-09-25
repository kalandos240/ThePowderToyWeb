import {
  initYandexSDK,
  installPlatformPauseBridge,
  signalGameReady,
  gameplayStart,
  gameplayStop,
  getYandexLanguage,
  onYandexSDKReady,
  setGameplayBlocked,
  canShowFullscreenAd,
  showFullscreenAd
} from "./yandex.js";

const app = document.getElementById("app");
const canvas = document.getElementById("canvas");
const mobileTextInput = document.getElementById("mobile-text-input");
const loader = document.getElementById("loader");
const status = document.getElementById("status");
const orientationGate = document.getElementById("orientation-gate");
const orientationTitle = document.getElementById("orientation-title");
const orientationMessage = document.getElementById("orientation-message");
const adWarning = document.getElementById("ad-warning");
const adWarningTitle = document.getElementById("ad-warning-title");
const adWarningCountdown = document.getElementById("ad-warning-countdown");
const adWarningMessage = document.getElementById("ad-warning-message");
const fatal = document.getElementById("fatal");
const fatalTitle = document.querySelector("#fatal h1");
const fatalMessage = document.getElementById("fatal-message");
const reloadButton = document.getElementById("reload");

// Lightweight startup telemetry used by the release smoke tests. Values are
// navigation-relative milliseconds from performance.now(); there is no
// network reporting and the object stays local to the page.
const startupTiming = {
  moduleReadyMs: performance.now(),
  engineFactoryStartMs: null,
  nativePresentableMs: null,
  readyMs: null
};
window.__tptStartupTiming = startupTiming;

const MESSAGES = {
  en: {
    init: "Initializing Yandex Games…",
    engine: "Loading engine…",
    simulation: "Starting simulation…",
    preparing: "Preparing interface…",
    fatalTitle: "The game could not be started",
    reload: "Reload",
    rotateTitle: "Rotate your device",
    rotateMessage: "The Powder Toy is designed for landscape mode.",
    textInputLabel: "Game text input",
    adWarningTitle: "Advertisement in",
    adWarningMessage: "The game is paused.",
    unknown: "Unknown error",
    loadScript: (src) => `Failed to load ${src}`,
    missingFactory: "create_powder was not found in the Emscripten build."
  },
  ru: {
    init: "Инициализация Яндекс Игр…",
    engine: "Загрузка движка…",
    simulation: "Запуск симуляции…",
    preparing: "Подготовка интерфейса…",
    fatalTitle: "Не удалось запустить игру",
    reload: "Перезапустить",
    rotateTitle: "Поверните устройство",
    rotateMessage: "Для The Powder Toy используйте горизонтальный режим.",
    textInputLabel: "Ввод текста в игре",
    adWarningTitle: "Реклама через",
    adWarningMessage: "Игра поставлена на паузу.",
    unknown: "Неизвестная ошибка",
    loadScript: (src) => `Не удалось загрузить ${src}`,
    missingFactory: "Функция create_powder не найдена в Emscripten-сборке."
  }
};

let uiLanguage = "en";

function applyPlatformLanguage(currentSDK) {
  const requested = getYandexLanguage(currentSDK);
  uiLanguage = Object.prototype.hasOwnProperty.call(MESSAGES, requested) ? requested : "en";
  document.documentElement.lang = uiLanguage;
  window.yandexDetectedLanguage = requested;
  window.tptLanguage = uiLanguage;

  if (fatalTitle) {
    fatalTitle.textContent = message("fatalTitle");
  }
  reloadButton.textContent = message("reload");
  orientationTitle.textContent = message("rotateTitle");
  orientationMessage.textContent = message("rotateMessage");
  mobileTextInput.setAttribute("aria-label", message("textInputLabel"));
  if (adWarningTitle) {
    adWarningTitle.textContent = message("adWarningTitle");
  }
  if (adWarningMessage) {
    adWarningMessage.textContent = message("adWarningMessage");
  }
}

function message(key, ...args) {
  const value = MESSAGES[uiLanguage]?.[key] ?? MESSAGES.en[key];
  return typeof value === "function" ? value(...args) : value;
}

let presentable = false;
let fatalShown = false;
let gameModule = null;
let platformPauseRequested = document.hidden;
let orientationPauseRequested = false;
let adPauseRequested = false;
let runtimePaused = false;
let orientationBlocked = false;
let nativeModalBlocked = false;
let sdkMobilePlatform = null;
let nativeLanguageLocked = false;
let viewportUpdateScheduled = false;
let lastCanvasStyleWidth = "";
let lastCanvasStyleHeight = "";
let lastCanvasImageRendering = "";
let adTimerId = null;
let adCycleActive = false;
const coarsePointerMedia =
  typeof window.matchMedia === "function"
    ? window.matchMedia("(pointer: coarse)")
    : null;
const AD_INTERVAL_MS = 120000;
const AD_WARNING_SECONDS = 2;
window.__tptRuntimePaused = false;
window.__tptOrientationBlocked = false;
window.__tptNativeModalBlocked = false;
window.__tptNativeModalDepth = 0;
window.__tptSdkMobilePlatform = null;
window.__tptAdWarningActive = false;
window.__tptAdCycleActive = false;
window.__tptAdAttemptCount = 0;
window.__tptCanvasFit = null;

const ENGINE_STDOUT_DEBUG =
  new URLSearchParams(window.location.search).get("tpt-debug") === "1";

function logEngineStdout(...args) {
  if (ENGINE_STDOUT_DEBUG) {
    console.log("[TPT]", ...args);
  }
}

function setStatus(message) {
  status.textContent = message;
}

const ENGINE_STDERR_INFO_PREFIXES = [
  "ReadFile: powder.pref: No such file or directory",
  "ReadFile: stamps/stamps.json: No such file or directory",
  "ReadFile: stamps/stamps.def: No such file or directory",
  "required #PowderSessionInfo elements not found, can't authenticate",
  "network support not compiled in",
  "web main loop via requestAnimationFrame",
  // Emscripten's SDL2 renderer asks for RAF timing while SDL_CreateRenderer
  // runs, before the application has installed its own browser main loop.
  // Our patched TPT source is statically checked to contain no such timing
  // call, so this exact SDL2 diagnostic is informational rather than fatal.
  "emscripten_set_main_loop_timing: Cannot set timing mode for main loop since a main loop does not exist!"
];

const ENGINE_STDERR_WARNING_PREFIXES = [
  "warning: 2 FS.syncfs operations in flight at once"
];

function logEngineStderr(...args) {
  const text = args.map((value) => String(value)).join(" ");

  if (ENGINE_STDERR_INFO_PREFIXES.some((prefix) => text.startsWith(prefix))) {
    if (ENGINE_STDOUT_DEBUG) {
      console.info("[TPT]", ...args);
    }
    return;
  }

  if (ENGINE_STDERR_WARNING_PREFIXES.some((prefix) => text.startsWith(prefix))) {
    if (ENGINE_STDOUT_DEBUG) {
      console.warn("[TPT]", ...args);
    }
    return;
  }

  console.error("[TPT]", ...args);
}

function isTouchEnvironment() {
  return Boolean(
    navigator.maxTouchPoints > 0 ||
    coarsePointerMedia?.matches
  );
}

async function applyPlatformDevice(currentSDK) {
  let mobilePlatform = null;

  try {
    const source = currentSDK?.deviceInfo;
    const deviceInfo =
      typeof source === "function"
        ? await Promise.resolve(source.call(currentSDK))
        : source;

    if (typeof deviceInfo?.type === "string") {
      const type = deviceInfo.type.toLowerCase();
      mobilePlatform = type === "mobile" || type === "tablet";
    } else if (deviceInfo) {
      const mobile =
        typeof deviceInfo.isMobile === "function"
          ? deviceInfo.isMobile()
          : Boolean(deviceInfo.isMobile);
      const tablet =
        typeof deviceInfo.isTablet === "function"
          ? deviceInfo.isTablet()
          : Boolean(deviceInfo.isTablet);
      mobilePlatform = Boolean(mobile || tablet);
    }
  } catch (error) {
    // DeviceInfo is an optional refinement. Browser touch/pointer detection is
    // the intended fallback, so keep this non-fatal path out of production
    // warnings while preserving opt-in diagnostics.
    if (ENGINE_STDOUT_DEBUG) {
      console.info("[TPT] Could not read Yandex deviceInfo; using browser fallback.", error);
    }
  }

  const changed = sdkMobilePlatform !== mobilePlatform;
  sdkMobilePlatform = mobilePlatform;
  window.__tptSdkMobilePlatform = sdkMobilePlatform;
  return changed;
}

function isMobilePlatform() {
  return sdkMobilePlatform ?? isTouchEnvironment();
}

function updateGameplayBlockState() {
  setGameplayBlocked(
    orientationBlocked ||
    nativeModalBlocked ||
    adPauseRequested
  );
}

window.__tptNativeModalBridge = {
  setBlocked(blocked, depth = blocked ? 1 : 0) {
    nativeModalBlocked = Boolean(blocked);
    window.__tptNativeModalBlocked = nativeModalBlocked;
    window.__tptNativeModalDepth = Math.max(0, Number(depth) || 0);
    updateGameplayBlockState();
  }
};

let mobileTextInputActive = false;
let mobileTextInputRect = null;
let mobileCompositionActive = false;
let mobileCompositionCommit = "";

window.__tptMobileTextInputActive = false;
window.__tptMobileTextInputFocused = false;
window.__tptMobileTextInputRect = null;

function positionMobileTextInput() {
  if (!mobileTextInputRect || mobileTextInput.hidden) {
    return;
  }

  const canvasRect = canvas.getBoundingClientRect();
  const nativeWidth = Math.max(1, canvas.width || 1);
  const nativeHeight = Math.max(1, canvas.height || 1);
  const scaleX = canvasRect.width / nativeWidth;
  const scaleY = canvasRect.height / nativeHeight;
  const rawLeft = canvasRect.left + mobileTextInputRect.x * scaleX;
  const rawTop = canvasRect.top + mobileTextInputRect.y * scaleY;
  const maxLeft = Math.max(canvasRect.left, canvasRect.right - 1);
  const maxTop = Math.max(canvasRect.top, canvasRect.bottom - 1);
  const left = Math.min(maxLeft, Math.max(canvasRect.left, rawLeft));
  const top = Math.min(maxTop, Math.max(canvasRect.top, rawTop));
  const width = Math.max(
    1,
    Math.min(canvasRect.right - left, mobileTextInputRect.w * scaleX)
  );
  const height = Math.max(
    1,
    Math.min(canvasRect.bottom - top, mobileTextInputRect.h * scaleY)
  );

  const previousRect = window.__tptMobileTextInputRect;
  const geometryChanged =
    !previousRect ||
    previousRect.left !== left ||
    previousRect.top !== top ||
    previousRect.width !== width ||
    previousRect.height !== height;

  if (geometryChanged) {
    mobileTextInput.style.left = `${left}px`;
    mobileTextInput.style.top = `${top}px`;
    mobileTextInput.style.width = `${width}px`;
    mobileTextInput.style.height = `${height}px`;
    window.__tptMobileTextInputRect = { left, top, width, height };
  }
}

function focusMobileTextInput() {
  if (
    !mobileTextInputActive ||
    !isTouchEnvironment() ||
    document.hidden ||
    platformPauseRequested ||
    orientationBlocked ||
    nativeModalBlocked ||
    adPauseRequested
  ) {
    return;
  }

  mobileTextInput.hidden = false;
  positionMobileTextInput();

  try {
    mobileTextInput.focus({ preventScroll: true });
  } catch {
    mobileTextInput.focus();
  }

  window.__tptMobileTextInputFocused =
    document.activeElement === mobileTextInput;
}

function pushMobileTextInput(text) {
  if (!gameModule || typeof gameModule.ccall !== "function" || !text) {
    return;
  }

  for (const character of Array.from(String(text))) {
    gameModule.ccall(
      "YandexWeb_PushTextInput",
      null,
      ["string"],
      [character]
    );
  }
}

function pushMobileKey(keycode) {
  if (!gameModule || typeof gameModule.ccall !== "function") {
    return;
  }

  gameModule.ccall(
    "YandexWeb_PushKey",
    null,
    ["number"],
    [keycode]
  );
}

function startMobileTextInput() {
  mobileTextInputActive = true;
  window.__tptMobileTextInputActive = true;

  if (!isTouchEnvironment()) {
    return;
  }

  mobileTextInput.value = "";
  mobileTextInput.hidden = false;
  positionMobileTextInput();
  focusMobileTextInput();
}

function stopMobileTextInput() {
  mobileTextInputActive = false;
  mobileCompositionActive = false;
  mobileCompositionCommit = "";
  window.__tptMobileTextInputActive = false;
  window.__tptMobileTextInputFocused = false;

  if (document.activeElement === mobileTextInput) {
    mobileTextInput.blur();
  }
  mobileTextInput.value = "";
  mobileTextInput.hidden = true;
}

function setMobileTextInputRect(x, y, width, height) {
  mobileTextInputRect = {
    x: Number(x) || 0,
    y: Number(y) || 0,
    w: Math.max(1, Number(width) || 1),
    h: Math.max(1, Number(height) || 1)
  };

  if (mobileTextInputActive && isTouchEnvironment()) {
    mobileTextInput.hidden = false;
    positionMobileTextInput();
  }
}

window.__tptMobileTextBridge = {
  start: startMobileTextInput,
  stop: stopMobileTextInput,
  setRect: setMobileTextInputRect
};

mobileTextInput.addEventListener("keydown", (event) => {
  event.stopPropagation();

  if (event.key === "Enter") {
    event.preventDefault();
    pushMobileKey(13);
  } else if (event.key === "Backspace") {
    event.preventDefault();
    pushMobileKey(8);
  } else if (event.key === "Delete") {
    event.preventDefault();
    pushMobileKey(127);
  } else if (event.key === "Escape") {
    event.preventDefault();
    pushMobileKey(27);
  }
});

mobileTextInput.addEventListener("keyup", (event) => {
  event.stopPropagation();
});

mobileTextInput.addEventListener("keypress", (event) => {
  event.stopPropagation();
});

mobileTextInput.addEventListener("compositionstart", (event) => {
  event.stopPropagation();
  mobileCompositionActive = true;
  mobileCompositionCommit = "";
});

mobileTextInput.addEventListener("compositionend", (event) => {
  event.stopPropagation();
  mobileCompositionActive = false;
  mobileCompositionCommit = event.data || "";
  if (mobileCompositionCommit) {
    pushMobileTextInput(mobileCompositionCommit);
  }
  mobileTextInput.value = "";
});

mobileTextInput.addEventListener("input", (event) => {
  event.stopPropagation();

  if (event.isComposing || mobileCompositionActive) {
    return;
  }

  const inserted =
    typeof event.data === "string" && event.data.length
      ? event.data
      : mobileTextInput.value;

  if (mobileCompositionCommit && inserted === mobileCompositionCommit) {
    mobileCompositionCommit = "";
    mobileTextInput.value = "";
    return;
  }

  mobileCompositionCommit = "";
  if (inserted) {
    pushMobileTextInput(inserted);
  }
  mobileTextInput.value = "";
});

mobileTextInput.addEventListener("focus", () => {
  window.__tptMobileTextInputFocused = true;
});

mobileTextInput.addEventListener("blur", () => {
  window.__tptMobileTextInputFocused = false;
});

mobileTextInput.addEventListener("pointerdown", (event) => {
  event.stopPropagation();
});

mobileTextInput.addEventListener("contextmenu", (event) => {
  event.preventDefault();
  event.stopPropagation();
});

function updateOrientationGate() {
  const nextBlocked = Boolean(
    presentable &&
    isMobilePlatform() &&
    window.innerHeight > window.innerWidth
  );

  // ResizeObserver + visualViewport can emit several events for the same
  // geometry. Avoid repeating DOM writes and gameplay-state reconciliation
  // when the orientation gate itself did not change.
  if (nextBlocked === orientationBlocked) {
    return;
  }

  const wasBlocked = orientationBlocked;
  orientationBlocked = nextBlocked;
  orientationGate.hidden = !orientationBlocked;
  orientationPauseRequested = orientationBlocked;
  window.__tptOrientationBlocked = orientationBlocked;

  if (orientationBlocked && document.activeElement === mobileTextInput) {
    mobileTextInput.blur();
    window.__tptMobileTextInputFocused = false;
  } else if (
    wasBlocked &&
    !orientationBlocked &&
    mobileTextInputActive &&
    isTouchEnvironment()
  ) {
    focusMobileTextInput();
  }

  applyRuntimePauseState();
  updateGameplayBlockState();
}

function fitCanvas() {
  const logicalWidth = canvas.width || 629;
  const logicalHeight = canvas.height || 424;
  const appWidth = app.clientWidth;
  const appHeight = app.clientHeight;

  // Always re-read computed safe-area padding. Mobile browsers can change
  // env(safe-area-inset-*) across repeated fullscreen/browser-chrome cycles
  // without changing app.clientWidth/clientHeight. The individual canvas
  // style writes below are still coalesced, so unchanged geometry remains cheap.
  const appStyle = getComputedStyle(app);
  const horizontalPadding =
    parseFloat(appStyle.paddingLeft) + parseFloat(appStyle.paddingRight);
  const verticalPadding =
    parseFloat(appStyle.paddingTop) + parseFloat(appStyle.paddingBottom);
  const availableWidth = Math.max(0, appWidth - horizontalPadding);
  const availableHeight = Math.max(0, appHeight - verticalPadding);

  if (!logicalWidth || !logicalHeight || !availableWidth || !availableHeight) {
    return;
  }

  const displayWidth = Math.max(1, Math.round(availableWidth));
  const displayHeight = Math.max(1, Math.round(availableHeight));
  const scaleX = displayWidth / logicalWidth;
  const scaleY = displayHeight / logicalHeight;
  const uniformScale = Math.abs(scaleX - scaleY) < 0.01;
  const integerScale =
    uniformScale &&
    Math.abs(scaleX - Math.round(scaleX)) < 0.01 &&
    scaleX >= 1;

  // Yandex can provide very wide/short game slots. Fill the complete slot
  // rather than letterboxing the fixed TPT logical framebuffer. For exact
  // integer scaling keep hard pixel edges; otherwise browser interpolation
  // keeps text and UI lines substantially cleaner than uneven pixel stepping.
  const nextStyleWidth = `${displayWidth}px`;
  const nextStyleHeight = `${displayHeight}px`;

  // The native TPT framebuffer is intentionally compact. Yandex desktop
  // slots can be much wider than it, so browser interpolation makes text and
  // 1px UI lines visibly soft. Prefer nearest-neighbour output whenever the
  // framebuffer is being enlarged on either axis; keep normal filtering only
  // for pure downscaling.
  const crispUpscale = scaleX > 1.02 || scaleY > 1.02;
  const nextImageRendering = crispUpscale ? "pixelated" : "auto";

  // visualViewport scroll/resize bursts frequently repeat identical geometry,
  // especially around mobile browser chrome and the virtual keyboard. Avoid
  // invalidating layout/style when the target canvas presentation is unchanged.
  if (lastCanvasStyleWidth !== nextStyleWidth) {
    canvas.style.width = nextStyleWidth;
    lastCanvasStyleWidth = nextStyleWidth;
  }
  if (lastCanvasStyleHeight !== nextStyleHeight) {
    canvas.style.height = nextStyleHeight;
    lastCanvasStyleHeight = nextStyleHeight;
  }
  if (lastCanvasImageRendering !== nextImageRendering) {
    canvas.style.imageRendering = nextImageRendering;
    lastCanvasImageRendering = nextImageRendering;
  }

  window.__tptCanvasFit = {
    logicalWidth,
    logicalHeight,
    displayWidth,
    displayHeight,
    scaleX,
    scaleY,
    integerScale,
    crispUpscale
  };
}

function callRuntimeHook(name) {
  if (!gameModule) {
    return false;
  }

  const direct = gameModule[`_${name}`];
  if (typeof direct === "function") {
    direct();
    return true;
  }

  if (typeof gameModule.ccall === "function") {
    gameModule.ccall(name, null, [], []);
    return true;
  }

  console.warn(`[TPT] Runtime hook ${name} is unavailable.`);
  return false;
}

function applyRuntimePauseState() {
  const requested =
    platformPauseRequested ||
    orientationPauseRequested ||
    adPauseRequested;
  if (!gameModule || runtimePaused === requested) {
    return;
  }

  const hook = requested
    ? "YandexWeb_PauseMainLoop"
    : "YandexWeb_ResumeMainLoop";

  if (callRuntimeHook(hook)) {
    runtimePaused = requested;
    window.__tptRuntimePaused = runtimePaused;
  }
}

function setRuntimePaused(paused) {
  platformPauseRequested = Boolean(paused);
  applyRuntimePauseState();
}

function showFatal(error) {
  if (fatalShown) {
    return;
  }

  fatalShown = true;
  console.error("[TPT] Fatal startup error:", error);

  setRuntimePaused(true);
  void gameplayStop();

  loader.hidden = true;
  orientationGate.hidden = true;
  adWarning.hidden = true;
  clearAdTimer();
  setGameplayBlocked(true);
  canvas.style.display = "none";
  fatalMessage.textContent =
    error instanceof Error ? error.message : String(error || message("unknown"));
  fatal.hidden = false;
  app.setAttribute("aria-busy", "false");
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error(message("loadScript", src)));
    document.head.appendChild(script);
  });
}

function sleep(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function clearAdTimer() {
  if (adTimerId !== null) {
    window.clearTimeout(adTimerId);
    adTimerId = null;
  }
}

function scheduleNextAd(delay = AD_INTERVAL_MS) {
  clearAdTimer();
  adTimerId = window.setTimeout(() => {
    adTimerId = null;
    void runFullscreenAdCycle();
  }, Math.max(1000, delay));
}

function canBeginFullscreenAdCycle() {
  return Boolean(
    presentable &&
    !fatalShown &&
    !document.hidden &&
    !platformPauseRequested &&
    !orientationBlocked &&
    !nativeModalBlocked
  );
}

async function runFullscreenAdCycle({ scheduleNext = true } = {}) {
  if (adCycleActive) {
    return false;
  }

  if (!canBeginFullscreenAdCycle()) {
    if (scheduleNext) {
      scheduleNextAd(15000);
    }
    return false;
  }

  if (!(await canShowFullscreenAd())) {
    if (scheduleNext) {
      scheduleNextAd();
    }
    return false;
  }

  // SDK availability can take time to resolve. The page may have become
  // hidden, rotated to portrait, entered a native modal, or received a
  // platform pause while we were awaiting it. Revalidate immediately before
  // taking gameplay ownership for the ad cycle.
  if (!canBeginFullscreenAdCycle()) {
    if (scheduleNext) {
      scheduleNextAd(15000);
    }
    return false;
  }

  const restoreMobileTextInputFocus =
    document.activeElement === mobileTextInput;

  if (restoreMobileTextInputFocus) {
    mobileTextInput.blur();
    window.__tptMobileTextInputFocused = false;
  }

  adCycleActive = true;
  adPauseRequested = true;
  window.__tptAdCycleActive = true;
  window.__tptAdWarningActive = true;
  window.__tptAdAttemptCount += 1;
  updateGameplayBlockState();
  applyRuntimePauseState();

  try {
    adWarningTitle.textContent = message("adWarningTitle");
    adWarningMessage.textContent = message("adWarningMessage");
    adWarning.hidden = false;

    for (let seconds = AD_WARNING_SECONDS; seconds >= 1; seconds -= 1) {
      adWarningCountdown.textContent = String(seconds);
      await sleep(1000);

      if (!canBeginFullscreenAdCycle()) {
        return false;
      }
    }

    // A blocker can arrive between the final countdown tick and the SDK call
    // (for example a modal opened by the last pointer event). Never launch an
    // ad over a newly blocked gameplay state.
    if (!canBeginFullscreenAdCycle()) {
      return false;
    }

    adWarning.hidden = true;
    window.__tptAdWarningActive = false;
    return await showFullscreenAd();
  } finally {
    adWarning.hidden = true;
    window.__tptAdWarningActive = false;
    adPauseRequested = false;
    adCycleActive = false;
    window.__tptAdCycleActive = false;
    updateGameplayBlockState();
    applyRuntimePauseState();

    if (
      restoreMobileTextInputFocus &&
      mobileTextInputActive &&
      !document.hidden &&
      !platformPauseRequested &&
      !orientationBlocked &&
      !nativeModalBlocked
    ) {
      focusMobileTextInput();
    }

    if (scheduleNext && !fatalShown) {
      scheduleNextAd();
    }
  }
}

window.__tptTriggerAdForTest = () =>
  runFullscreenAdCycle({ scheduleNext: false });

async function onPresentable() {
  if (presentable) {
    return;
  }

  presentable = true;
  startupTiming.nativePresentableMs = performance.now();
  fitCanvas();

  canvas.style.display = "block";
  loader.hidden = true;
  app.setAttribute("aria-busy", "false");
  updateOrientationGate();

  await new Promise((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(resolve))
  );

  await signalGameReady();
  await gameplayStart();
  startupTiming.readyMs = performance.now();
  scheduleNextAd();
}

window.mark_presentable = () => {
  void onPresentable();
};

function scheduleViewportUpdate() {
  if (viewportUpdateScheduled) {
    return;
  }

  viewportUpdateScheduled = true;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      viewportUpdateScheduled = false;
      fitCanvas();
      positionMobileTextInput();
      updateOrientationGate();
    });
  });
}

onYandexSDKReady((currentSDK) => {
  // Engine bootstrap no longer waits for YaGames.init(). Reconcile every SDK
  // arrival, not only the >timeout "late" path: the SDK may legitimately
  // resolve after powder.js but before the 8 second timeout.
  void (async () => {
    const deviceClassificationChanged = await applyPlatformDevice(currentSDK);

    const detectedLanguage = getYandexLanguage(currentSDK);
    window.yandexDetectedLanguage = detectedLanguage;

    if (!nativeLanguageLocked) {
      applyPlatformLanguage(currentSDK);
    } else if (detectedLanguage !== uiLanguage && ENGINE_STDOUT_DEBUG) {
      console.info(
        `[Yandex] SDK language ${detectedLanguage} differs from active ${uiLanguage}; keeping the current native UI language for this session.`
      );
    }

    if (deviceClassificationChanged) {
      scheduleViewportUpdate();
    }
  })();
});

window.addEventListener("resize", scheduleViewportUpdate, { passive: true });
window.addEventListener("orientationchange", scheduleViewportUpdate, { passive: true });
window.addEventListener("pageshow", scheduleViewportUpdate);
document.addEventListener("fullscreenchange", scheduleViewportUpdate);

let appResizeObserver = null;
if (typeof ResizeObserver !== "undefined") {
  appResizeObserver = new ResizeObserver(scheduleViewportUpdate);
  appResizeObserver.observe(app);
}

if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", scheduleViewportUpdate, {
    passive: true
  });
  window.visualViewport.addEventListener("scroll", scheduleViewportUpdate, {
    passive: true
  });
}

app.addEventListener("contextmenu", (event) => {
  event.preventDefault();
});

canvas.addEventListener(
  "pointerdown",
  () => {
    canvas.focus({ preventScroll: true });
  },
  { passive: true }
);

window.addEventListener("error", (event) => {
  if (!presentable) {
    showFatal(event.error || new Error(event.message));
  }
});

window.addEventListener("unhandledrejection", (event) => {
  if (!presentable) {
    showFatal(event.reason);
  }
});

reloadButton.addEventListener("click", () => {
  location.reload();
});

async function boot() {
  installPlatformPauseBridge({
    onPause: () => setRuntimePaused(true),
    onResume: () => setRuntimePaused(false)
  });

  setStatus(message("init"));

  // Start the platform SDK immediately, but do not put its network/init latency
  // on the engine critical path. The local JS/WASM payload can compile in
  // parallel; if Yandex is already ready by the time powder.js arrives we use
  // its locale/device data, otherwise browser fallbacks are used and the
  // existing late-SDK reconciliation path adopts Yandex afterwards.
  const sdkPromise = initYandexSDK();
  await loadScript("./game/powder.js");
  const currentSDK = window.ysdk || null;
  startupTiming.sdkAvailableAtEngineStart = Boolean(currentSDK);

  // DeviceInfo reconciliation is owned by onYandexSDKReady(). Keeping it out
  // of boot avoids duplicate SDK device queries and duplicate viewport work.
  // Until then, isMobilePlatform() uses the browser touch/pointer fallback.
  applyPlatformLanguage(currentSDK);

  // Keep the SDK promise alive explicitly so startup errors remain handled by
  // initYandexSDK(), while engine startup never waits for the SDK timeout.
  void sdkPromise;

  setStatus(message("engine"));

  if (typeof window.create_powder !== "function") {
    throw new Error(message("missingFactory"));
  }

  setStatus(message("simulation"));

  // The native UI caches its locale when it is constructed. From this point
  // onward keep one language for the session instead of mixing RU/EN if a
  // previously timed-out SDK reports a different locale later.
  nativeLanguageLocked = true;
  window.__tptLanguageLocked = uiLanguage;

  startupTiming.engineFactoryStartMs = performance.now();
  const gamePromise = window.create_powder({
    canvas,
    print: (...args) => logEngineStdout(...args),
    printErr: (...args) => logEngineStderr(...args),
    locateFile(path) {
      if (path.endsWith(".wasm")) {
        return `./game/${path}`;
      }
      return path;
    }
  });

  const gameResult = await Promise.resolve(gamePromise)
    .then((value) => ({ status: "fulfilled", value }))
    .catch((reason) => ({ status: "rejected", reason }));

  if (gameResult.status === "rejected") {
    throw gameResult.reason;
  }

  gameModule = gameResult.value;
  window.__tptGameModule = gameModule;
  applyRuntimePauseState();

  if (!presentable) {
    setStatus(message("preparing"));
  }
}

// Local/no-SDK fallback should respect the browser language immediately.
applyPlatformLanguage(null);

void boot().catch(showFatal);
