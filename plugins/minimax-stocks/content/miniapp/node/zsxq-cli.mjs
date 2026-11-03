// @ts-check
// Read-only zsxq-cli bridge for the 知识星球 sentiment source.
//
// Boundary rules (agreed with the owner):
// - only the read-only `topic +search` / `group +list` subcommands are ever invoked;
// - arguments are fixed by this module and never pass through page input;
// - the CLI runs with execFile (no shell), a hard timeout, and bounded output;
// - when the CLI or its login state is unavailable the source is skipped, never faked.
import { execFile } from 'node:child_process';

const CLI = 'zsxq-cli';
const CHECK_TTL_MS = 10 * 60_000;
const CLI_TIMEOUT_MS = 20_000;
const MAX_OUTPUT_BYTES = 8 * 1024 * 1024;

export function createZsxqBridge() {
  /** @type {Set<import('node:child_process').ChildProcess>} */
  const children = new Set();
  let availability = { available: false, reason: 'unchecked', groupId: null, checkedAt: 0 };

  function run(args) {
    return new Promise((resolve, reject) => {
      const child = execFile(CLI, args, { timeout: CLI_TIMEOUT_MS, maxBuffer: MAX_OUTPUT_BYTES }, (error, stdout) => {
        children.delete(child);
        if (error) reject(error);
        else resolve(String(stdout));
      });
      children.add(child);
    });
  }

  return {
    /**
     * Capability probe: the CLI binary must exist AND the logged-in account must
     * return at least one group. Result is cached for 10 minutes.
     */
    async checkAvailable({ force = false } = {}) {
      if (!force && Date.now() - availability.checkedAt < CHECK_TTL_MS) return availability;
      try {
        const parsed = JSON.parse(await run(['group', '+list', '--json']));
        const groups = Array.isArray(parsed?.groups) ? parsed.groups.filter((row) => row?.group_id) : [];
        const group = groups[0] ?? null;
        availability = group
          ? { available: true, reason: 'ok', groupId: String(group.group_id), groupCount: groups.length, groupName: typeof group.name === 'string' ? group.name.slice(0, 40) : null, checkedAt: Date.now() }
          : { available: false, reason: 'no_group', groupId: null, groupCount: 0, groupName: null, checkedAt: Date.now() };
      } catch (error) {
        availability = {
          available: false,
          reason: error?.code === 'ENOENT' ? 'cli_missing' : 'cli_error',
          groupId: null,
          groupCount: 0,
          groupName: null,
          checkedAt: Date.now(),
        };
      }
      return availability;
    },

    /** Full-text topic search mapped to normalized sentiment items. */
    async fetchTopics(groupId, query) {
      const parsed = JSON.parse(await run(['topic', '+search', '--group-id', groupId, '--query', query, '--json']));
      const topics = Array.isArray(parsed?.topics_brief) ? parsed.topics_brief : [];
      return topics
        .map((topic) => {
          if (!topic || typeof topic.topic_id !== 'string' && typeof topic.topic_id !== 'number') return null;
          const content = cleanText(topic.content ?? '');
          if (content === '') return null;
          const firstLine = content.split('\n')[0]?.trim() ?? '';
          const title = firstLine !== '' ? firstLine.slice(0, 60) : cleanText(topic.title ?? '').slice(0, 60);
          if (title === '') return null;
          const tags = [topic.owner?.name, topic.digested ? '精华' : '']
            .filter((tag) => typeof tag === 'string' && tag.trim() !== '');
          return {
            id: `zsxq-${topic.topic_id}`,
            source: '知识星球',
            title,
            summary: content.slice(0, 180),
            content,
            publishedAt: normalizeTime(String(topic.create_time ?? '')),
            url: `https://wx.zsxq.com/topic/${topic.topic_id}`,
            tags,
          };
        })
        .filter((item) => item !== null && item.publishedAt !== '');
    },

    /** Kill in-flight CLI child processes on runtime dispose. */
    dispose() {
      for (const child of children) child.kill('SIGTERM');
      children.clear();
    },
  };
}

/** "2026-08-24T14:07:18.063+0800" → "…+08:00"; unparseable input yields ''. */
function normalizeTime(value) {
  const normalized = value.replace(/([+-]\d{2})(\d{2})$/, '$1:$2');
  return Number.isFinite(Date.parse(normalized)) ? normalized : '';
}

/** Strip zsxq inline markup: <e … title="%23…"/> hashtags and [emoji] markers. */
function cleanText(text) {
  let out = String(text ?? '').replace(/<e\s[^>]*?\/>/g, (match) => {
    const title = match.match(/title="([^"]*)"/);
    if (!title) return '';
    try { return decodeURIComponent(title[1]); } catch { return title[1]; }
  });
  out = out.replace(/\[[^\]]{1,8}\]/g, '');
  return out.trim();
}
