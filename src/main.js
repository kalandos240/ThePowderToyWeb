import {
  initYandexSDK,
  installPlatformPauseBridge,
  signalGameReady,
  gameplayStart,
  gameplayStop,
  getYandexLanguage,
  setGameplayBlocked
} from "./yandex.js";

const app = document.getElementById("app");
const canvas = document.getElementById("canvas");
const mobileTextInput = document.getElementById("mobile-text-input");
const loader = document.getElementById("loader");
const status = document.getElementById("status");
const orientationGate = document.getElementById("orientation-gate");
const orientationTitle = document.getElementById("orientation-title");
const orientationMessage = document.getElementById("orientation-message");
const fatal = document.getElementById("fatal");
const fatalTitle = document.querySelector("#fatal h1");
const fatalMessage = document.getElementById("fatal-message");
const reloadButton = document.getElementById("reload");

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
let runtimePaused = false;
let orientationBlocked = false;
let nativeModalBlocked = false;
let sdkMobilePlatform = null;
window.__tptRuntimePaused = false;
window.__tptOrientationBlocked = false;
window.__tptNativeModalBlocked = false;
window.__tptNativeModalDepth = 0;
window.__tptSdkMobilePlatform = null;

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
  "invoking FS.syncfs",
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
    console.info("[TPT]", ...args);
    return;
  }

  if (ENGINE_STDERR_WARNING_PREFIXES.some((prefix) => text.startsWith(prefix))) {
    console.warn("[TPT]", ...args);
    return;
  }

  console.error("[TPT]", ...args);
}

function isTouchEnvironment() {
  return Boolean(
    navigator.maxTouchPoints > 0 ||
    window.matchMedia?.("(pointer: coarse)")?.matches
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
    console.warn("[TPT] Could not read Yandex deviceInfo.", error);
  }

  sdkMobilePlatform = mobilePlatform;
  window.__tptSdkMobilePlatform = sdkMobilePlatform;
}

function isMobilePlatform() {
  return sdkMobilePlatform ?? isTouchEnvironment();
}

function updateGameplayBlockState() {
  setGameplayBlocked(orientationBlocked || nativeModalBlocked);
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

  mobileTextInput.style.left = `${left}px`;
  mobileTextInput.style.top = `${top}px`;
  mobileTextInput.style.width = `${width}px`;
  mobileTextInput.style.height = `${height}px`;

  window.__tptMobileTextInputRect = { left, top, width, height };
}

function focusMobileTextInput() {
  if (
    !mobileTextInputActive ||
    !isTouchEnvironment() ||
    orientationBlocked ||
    document.hidden
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
  const logicalWidth = canvas.width || 612;
  const logicalHeight = canvas.height || 384;
  const appStyle = getComputedStyle(app);
  const horizontalPadding =
    parseFloat(appStyle.paddingLeft) + parseFloat(appStyle.paddingRight);
  const verticalPadding =
    parseFloat(appStyle.paddingTop) + parseFloat(appStyle.paddingBottom);
  const availableWidth = Math.max(0, app.clientWidth - horizontalPadding);
  const availableHeight = Math.max(0, app.clientHeight - verticalPadding);

  if (!logicalWidth || !logicalHeight || !availableWidth || !availableHeight) {
    return;
  }

  const scale = Math.min(
    availableWidth / logicalWidth,
    availableHeight / logicalHeight
  );

  canvas.style.width = `${Math.max(1, Math.floor(logicalWidth * scale))}px`;
  canvas.style.height = `${Math.max(1, Math.floor(logicalHeight * scale))}px`;
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
  const requested = platformPauseRequested || orientationPauseRequested;
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

async function onPresentable() {
  if (presentable) {
    return;
  }

  presentable = true;
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
}

window.mark_presentable = () => {
  void onPresentable();
};

function scheduleViewportUpdate() {
  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      fitCanvas();
      positionMobileTextInput();
      updateOrientationGate();
    })
  );
}

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
  const [currentSDK] = await Promise.all([
    initYandexSDK(),
    loadScript("./game/powder.js")
  ]);
  await applyPlatformDevice(currentSDK);
  applyPlatformLanguage(currentSDK);

  setStatus(message("engine"));

  if (typeof window.create_powder !== "function") {
    throw new Error(message("missingFactory"));
  }

  setStatus(message("simulation"));

  const gamePromise = window.create_powder({
    canvas,
    print: (...args) => console.log("[TPT]", ...args),
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

void boot().catch(showFatal);
