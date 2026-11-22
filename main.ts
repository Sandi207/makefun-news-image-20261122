import { copyFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
const outputDirectory = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
mkdirSync(outputDirectory, { recursive: true });
const destination = resolve(outputDirectory, "entry.png");
copyFileSync(fileURLToPath(new URL("./entry.png", import.meta.url)), destination);
console.log(destination);
