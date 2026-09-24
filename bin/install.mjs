#!/usr/bin/env node
// One-line installer: adds "gamebox-buildbox-classic@latest" to the
// OpenCode `plugin[]` array so /gamebox-xxx commands load on next start.
// Usage:
//   npx -y gamebox-buildbox-classic        (patches global config)
//   npx -y gamebox-buildbox-classic --project   (patches ./opencode.json)
//   npx -y gamebox-buildbox-classic --dry-run
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";

const PKG = "gamebox-buildbox-classic@latest";
const args = new Set(process.argv.slice(2));
const dryRun = args.has("--dry-run");
const projectMode = args.has("--project");

function configPath() {
  if (projectMode) return resolve(process.cwd(), "opencode.json");
  const dir = join(homedir(), ".config", "opencode");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  return join(dir, "opencode.json");
}

const file = configPath();
let cfg = {};
if (existsSync(file)) {
  try {
    cfg = JSON.parse(readFileSync(file, "utf8"));
  } catch (e) {
    console.error(`Could not parse ${file}: ${e.message}`);
    process.exit(1);
  }
}
if (!Array.isArray(cfg.plugin)) cfg.plugin = [];
if (!cfg.plugin.includes(PKG)) {
  cfg.plugin.push(PKG);
  if (dryRun) {
    console.log(`[dry-run] Would add "${PKG}" to plugin[] in ${file}`);
  } else {
    writeFileSync(file, JSON.stringify(cfg, null, 2) + "\n");
    console.log(`Added "${PKG}" to plugin[] in ${file}`);
  }
} else {
  console.log(`"${PKG}" is already in plugin[] in ${file}`);
}
console.log("Restart OpenCode, then type /gamebox- for the 6 commands.");
