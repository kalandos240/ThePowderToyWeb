import {
  initYandexSDK,
  installPlatformPauseBridge,
  signalGameReady,
  gameplayStart,
  gameplayStop,
  getYandexLanguage
} from "./yandex.js";

const app = document.getElementById("app");
const canvas = document.getElementById("canvas");
const loader = document.getElementById("loader");
const status = document.getElementById("status");
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
    unknown: "Неизвестная ошибка",
    loadScript: (src) => `Не удалось загрузить ${src}`,
    missingFactory: "Функция create_powder не найдена в Emscripten-сборке."
  }
};

let uiLanguage = "en";

function applyPlatformLanguage(currentSDK) {
  const requested = getYandexLanguage(currentSDK);
  uiLanguage = Object.hasOwn(MESSAGES, requested) ? requested : "en";
  document.documentElement.lang = uiLanguage;
  window.yandexDetectedLanguage = requested;
  window.tptLanguage = uiLanguage;

  if (fatalTitle) {
    fatalTitle.textContent = message("fatalTitle");
  }
  reloadButton.textContent = message("reload");
}

function message(key, ...args) {
  const value = MESSAGES[uiLanguage]?.[key] ?? MESSAGES.en[key];
  return typeof value === "function" ? value(...args) : value;
}

let presentable = false;
let fatalShown = false;
let gameModule = null;
let runtimePauseRequested = document.hidden;
let runtimePaused = false;

function setStatus(message) {
  status.textContent = message;
}

function fitCanvas() {
  const logicalWidth = canvas.width || 612;
  const logicalHeight = canvas.height || 384;
  const availableWidth = app.clientWidth;
  const availableHeight = app.clientHeight;

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
  if (!gameModule || runtimePaused === runtimePauseRequested) {
    return;
  }

  const hook = runtimePauseRequested
    ? "YandexWeb_PauseMainLoop"
    : "YandexWeb_ResumeMainLoop";

  if (callRuntimeHook(hook)) {
    runtimePaused = runtimePauseRequested;
  }
}

function setRuntimePaused(paused) {
  runtimePauseRequested = Boolean(paused);
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

  await new Promise((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(resolve))
  );

  await signalGameReady();
  await gameplayStart();
}

window.mark_presentable = () => {
  void onPresentable();
};

function scheduleCanvasFit() {
  requestAnimationFrame(() => requestAnimationFrame(fitCanvas));
}

window.addEventListener("resize", scheduleCanvasFit, { passive: true });
window.addEventListener("orientationchange", scheduleCanvasFit, { passive: true });
document.addEventListener("fullscreenchange", scheduleCanvasFit);

if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", scheduleCanvasFit, {
    passive: true
  });
  window.visualViewport.addEventListener("scroll", scheduleCanvasFit, {
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
  applyPlatformLanguage(currentSDK);

  setStatus(message("engine"));

  if (typeof window.create_powder !== "function") {
    throw new Error(message("missingFactory"));
  }

  setStatus(message("simulation"));

  const gamePromise = window.create_powder({
    canvas,
    print: (...args) => console.log("[TPT]", ...args),
    printErr: (...args) => console.error("[TPT]", ...args),
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
  applyRuntimePauseState();

  if (!presentable) {
    setStatus(message("preparing"));
  }
}

void boot().catch(showFatal);
