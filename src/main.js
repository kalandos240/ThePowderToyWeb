import {
  initYandexSDK,
  installGameplayVisibilityBridge,
  signalGameReady,
  gameplayStart,
  gameplayStop
} from "./yandex.js";

const app = document.getElementById("app");
const canvas = document.getElementById("canvas");
const loader = document.getElementById("loader");
const status = document.getElementById("status");
const fatal = document.getElementById("fatal");
const fatalMessage = document.getElementById("fatal-message");
const reloadButton = document.getElementById("reload");

let presentable = false;
let fatalShown = false;

function setStatus(message) {
  status.textContent = message;
}

function showFatal(error) {
  if (fatalShown) {
    return;
  }

  fatalShown = true;
  console.error("[TPT] Fatal startup error:", error);

  void gameplayStop();

  loader.hidden = true;
  canvas.style.display = "none";
  fatalMessage.textContent =
    error instanceof Error ? error.message : String(error || "Неизвестная ошибка");
  fatal.hidden = false;
  app.setAttribute("aria-busy", "false");
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`Не удалось загрузить ${src}`));
    document.head.appendChild(script);
  });
}

async function onPresentable() {
  if (presentable) {
    return;
  }

  presentable = true;
  canvas.style.display = "block";
  loader.hidden = true;
  app.setAttribute("aria-busy", "false");

  // Let the browser paint the final interactive canvas before reporting Game Ready.
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  await signalGameReady();
  await gameplayStart();
}

window.mark_presentable = () => {
  void onPresentable();
};

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
  installGameplayVisibilityBridge();

  setStatus("Инициализация Яндекс Игр…");
  const sdkPromise = initYandexSDK();

  setStatus("Загрузка движка…");
  await loadScript("./game/powder.js");

  if (typeof window.create_powder !== "function") {
    throw new Error("Функция create_powder не найдена в Emscripten-сборке.");
  }

  setStatus("Запуск симуляции…");

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

  // SDK failure must never block the native game startup.
  await Promise.allSettled([sdkPromise, gamePromise]);

  if (!presentable) {
    setStatus("Подготовка интерфейса…");
  }
}

void boot().catch(showFatal);
