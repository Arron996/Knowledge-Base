#!/usr/bin/env node
/**
 * Evening Daily agent via Cursor SDK (local runtime + MCP from ~/.cursor).
 * Usage: node kb-evening-agent.mjs --date YYYY-MM-DD
 */
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Agent, CursorAgentError } from "@cursor/sdk";

const __dirname = dirname(fileURLToPath(import.meta.url));
const VAULT = join(__dirname, "..");

function parseArgs(argv) {
  let date = null;
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--date" && argv[i + 1]) {
      date = argv[++i];
    }
  }
  if (!date) {
    const d = new Date();
    date = d.toISOString().slice(0, 10);
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    console.error("Invalid --date, use YYYY-MM-DD");
    process.exit(1);
  }
  return date;
}

function buildPrompt(targetDate) {
  const instructions = readFileSync(
    join(VAULT, "Templates", "automation-evening-instructions.md"),
    "utf8",
  );
  return `工作目录：${VAULT}

按 Templates/automation-evening-instructions.md 与 Templates/daily-style-guide.md 执行晚间日报。

目标日期（今天）：${targetDate}

要求：
1. 先读 daily-style-guide.md（§5 iDev 三路、§6 合并规则）与 topic-registry.yaml
2. iDev2 / 飞书 / GitLab MCP 采集 → 对应 collect-*.py sidecar
3. python3 .scripts/collect-evening.py --date ${targetDate}
4. 写或更新 Daily/${targetDate}.md（§6 合并；填 ## 📋 明日待办）
5. **不要**写 Weekly（Weekly 由周五 9:00 早间脚本生成）
6. **不要** git commit/push（shell 脚本负责）

Instructions 摘要：
${instructions.slice(0, 4000)}
`;
}

async function main() {
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey) {
    console.error("CURSOR_API_KEY is not set");
    process.exit(1);
  }

  const targetDate = parseArgs(process.argv);
  const prompt = buildPrompt(targetDate);

  console.error(`[kb-evening-agent] starting for ${targetDate}...`);

  try {
    const result = await Agent.prompt(prompt, {
      apiKey,
      model: { id: "composer-2.5" },
      local: {
        cwd: VAULT,
        settingSources: ["all"],
      },
    });

    if (result.status === "error") {
      console.error(`[kb-evening-agent] run failed: ${result.id ?? "unknown"}`);
      process.exit(2);
    }
    console.error(`[kb-evening-agent] done: ${result.status}`);
  } catch (err) {
    if (err instanceof CursorAgentError) {
      console.error(
        `[kb-evening-agent] startup failed: ${err.message} retryable=${err.isRetryable}`,
      );
      process.exit(1);
    }
    throw err;
  }
}

main();
