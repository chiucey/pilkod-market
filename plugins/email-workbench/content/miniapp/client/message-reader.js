/** Bounded, page-local message cache. No credentials, disk writes or read-state mutations. */
export function createMessageReader(read, { now = Date.now, ttl = 60_000, limit = 12, maxBytes = 4 * 1024 * 1024 } = {}) {
  const cache = new Map(), pending = new Map();
  let generation = 0, bytes = 0;
  const keyOf = ref => JSON.stringify([ref.accountId, ref.folder, ref.uidValidity, ref.uid]);
  const copy = value => JSON.parse(JSON.stringify(value));
  const remove = key => { const entry = cache.get(key); if (entry) bytes -= entry.bytes; cache.delete(key); };
  function peek(ref) {
    const key = keyOf(ref), entry = cache.get(key);
    if (!entry) return;
    if (now() >= entry.until) { remove(key); return; }
    cache.delete(key); cache.set(key, entry);
    return copy(entry.message);
  }
  async function load(ref, speculative = false) {
    const key = keyOf(ref);
    if (!speculative) {
      // Even a cached foreground selection retires another in-flight read.
      // The same message instead takes ownership of its existing preload.
      for (const [other, task] of pending) if (other !== key) { task.controller.abort(); pending.delete(other); }
      const existing = pending.get(key);
      if (existing) existing.speculative = false;
    }
    const hit = peek(ref);
    if (hit) return hit;
    let entry = pending.get(key);
    if (!entry) {
      const controller = new AbortController(), epoch = generation;
      entry = { controller, speculative };
      entry.promise = (async () => {
        const message = await read({ ref }, controller.signal);
        let offset = message.nextTextOffset;
        while (offset !== undefined) {
          if (controller.signal.aborted) throw new Error('Message read cancelled');
          const part = await read({ ref, textOffset: offset }, controller.signal);
          if (part.textOffset !== offset || part.textCharacters !== message.textCharacters ||
              (part.nextTextOffset !== undefined && part.nextTextOffset <= offset)) {
            const error = new Error('INVALID_RESPONSE'); error.code = 'INVALID_RESPONSE'; throw error;
          }
          message.text += part.text;
          offset = part.nextTextOffset;
        }
        if (!controller.signal.aborted && generation === epoch) {
          const size = JSON.stringify(message).length * 2;
          if (size <= maxBytes) {
            remove(key);
            cache.set(key, { message: copy(message), bytes: size, until: now() + ttl }); bytes += size;
            while (cache.size > limit || bytes > maxBytes) remove(cache.keys().next().value);
          }
        }
        return message;
      })().finally(() => { if (pending.get(key) === entry) pending.delete(key); });
      pending.set(key, entry);
    }
    return copy(await entry.promise);
  }
  return {
    peek, load: ref => load(ref),
    prefetch(ref) {
      if (pending.size || peek(ref)) return Promise.resolve();
      return load(ref, true).then(() => {}, () => {});
    },
    cancelPrefetch() {
      for (const [key, task] of pending) if (task.speculative) { task.controller.abort(); pending.delete(key); }
    },
    update(ref, fields) { const entry = cache.get(keyOf(ref)); if (entry) Object.assign(entry.message, fields); },
    clear() {
      generation += 1; cache.clear(); bytes = 0;
      for (const task of pending.values()) task.controller.abort();
      pending.clear();
    },
  };
}

/** Prepare a small reading window while idle; foreground actions always retire the queue. */
export function createMessagePreloader(reader, canRun, { delay = 500 } = {}) {
  let timer, generation = 0;
  const stop = () => { clearTimeout(timer); generation += 1; };
  return {
    stop,
    schedule(items) {
      stop();
      const epoch = generation, queue = [], keys = new Set();
      let bytes = 0;
      for (const item of items) {
        if (!Number.isFinite(item.size) || item.size < 0 || item.size > 256 * 1024) continue;
        const key = JSON.stringify(item.ref);
        if (keys.has(key) || reader.peek(item.ref)) continue;
        if (queue.length >= 3 || bytes + item.size > 512 * 1024) break;
        keys.add(key); queue.push(item.ref); bytes += item.size;
      }
      timer = setTimeout(async () => {
        for (const ref of queue) {
          if (epoch !== generation || !canRun()) return;
          await reader.prefetch(ref);
        }
      }, delay);
    },
  };
}
