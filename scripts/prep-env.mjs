import { spawnSync } from "child_process";
import fs from "fs";
import path from "path";
import crypto from "crypto";

const ROOT = process.cwd();
const ENV_PATH = path.join(ROOT, ".env");
const REQ_PATH = path.join(ROOT, "requirements.txt");
const CACHE_DIR = path.join(ROOT, ".cache");
const REQ_HASH_FILE = path.join(CACHE_DIR, "requirements.hash");
const PY_DEFAULTS = `PY_EXECUTABLE=python\nPYGMENTIZE_THEME=native\n`;

// ensure cache dir
if (!fs.existsSync(CACHE_DIR)) fs.mkdirSync(CACHE_DIR, { recursive: true });

// create a minimal .env if missing
if (!fs.existsSync(ENV_PATH)) {
  fs.writeFileSync(ENV_PATH, PY_DEFAULTS, { encoding: "utf8" });
  console.log("[prep] Created .env with defaults (edit as needed).");
} else {
  console.log("[prep] .env exists; leaving untouched.");
}

// choose python executable from env or fallback
const pythonExec = process.env.PY_EXECUTABLE || "python3" || "python";

// read requirements and compute hash
let needInstall = false;
if (!fs.existsSync(REQ_PATH)) {
  console.log("[prep] No requirements.txt found; skipping pip install.");
} else {
  const reqContent = fs.readFileSync(REQ_PATH, "utf8");
  const hash = crypto.createHash("sha1").update(reqContent).digest("hex");

  const prevHash = fs.existsSync(REQ_HASH_FILE)
    ? fs.readFileSync(REQ_HASH_FILE, "utf8").trim()
    : null;

  if (hash !== prevHash) {
    needInstall = true;
    fs.writeFileSync(REQ_HASH_FILE, hash, "utf8");
    console.log("[prep] requirements.txt changed or first run — will install.");
  } else {
    console.log("[prep] requirements unchanged — skipping pip install.");
  }
}

// if needed, run pip install
if (needInstall) {
  try {
    // ensure pip is available
    const pipCheck = spawnSync(pythonExec, ["-m", "pip", "--version"], {
      stdio: "pipe",
    });
    if (pipCheck.status !== 0) {
      console.error(
        `[prep] ${pythonExec} -m pip not available. Output:\n${pipCheck.stderr.toString()}`
      );
      process.exit(1);
    }

    console.log(`[prep] Running: ${pythonExec} -m pip install -r requirements.txt`);
    const install = spawnSync(pythonExec, ["-m", "pip", "install", "-r", "requirements.txt"], {
      stdio: "inherit",
    });
    if (install.status !== 0) {
      console.error("[prep] pip install failed.");
      process.exit(install.status || 1);
    }
    console.log("[prep] pip install completed.");
  } catch (e) {
    console.error("[prep] Failed to run pip install:", e);
    process.exit(1);
  }
}