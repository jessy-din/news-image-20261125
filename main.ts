import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry point: copy the rendered newspaper image beside this file to the
// output directory the grader provides. No network, no writes to this
// repository, nothing but the Node standard library.
//
// The grader sets MAKEFUN_OUTPUT_DIR; without it the program writes to
// /output, the path the competition's deliverable names.
const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const source = join(here, "entry.png");
const target = join(outDir, "entry.png");

if (!existsSync(source)) {
  console.error("entry.png not found next to main.ts");
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);
console.log("wrote " + target);

