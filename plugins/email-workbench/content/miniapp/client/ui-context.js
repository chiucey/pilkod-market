import { t } from './i18n.js';
/** A small same-origin bridge. Full draft content stays in the existing draft/recovery service. */
export function createUiContextBridge({ api, capture, execute, available, notice }) {
  const instanceId = crypto.randomUUID();
  let sequence = 0;
  let previous;
  let timer;
  let stopped = false;
  let running = false;
  function snapshot() {
    const state = capture();
    const serialized = JSON.stringify(state);
    if (serialized !== previous) { sequence += 1; previous = serialized; }
    return { instanceId, sequence, ...state };
  }
  async function tick() {
    if (stopped || running || !available()) return;
    running = true;
    try {
      const context = snapshot();
      const { operations } = await api('ui/context', context);
      for (const operation of operations) {
        if (stopped) return;
        const current = snapshot();
        let ack;
        if (current.sequence !== operation.expectedSequence)
          ack = { status: 'blocked', result: { reason: 'changed' } };
        else {
          try { ack = await execute(operation); }
          catch (error) {
            ack = { status: 'blocked', result: { reason: error?.code === 'REVISION_CONFLICT' ? 'conflict' : 'unavailable' } };
            notice(t('助手操作未完成，页面输入仍保留。请核对保存或连接状态。'), true);
          }
        }
        await api('ui/ack', { operationId: operation.operationId, ...ack, context: snapshot() });
      }
    } catch {
      // A missed heartbeat becomes stale on the backend; never invent an ACK.
    } finally { running = false; }
  }
  return {
    start() { stopped = false; clearInterval(timer); timer = setInterval(() => void tick(), 1500); void tick(); },
    publish: tick,
    invalidate: async () => { await api('ui/context', snapshot()); },
    stop() {
      stopped = true; clearInterval(timer);
      const state = capture();
      // Dirty offline instances remain visible and block remote overwrites.
      if (!state.dirty && !state.saving && !state.uploading)
        void api('ui/close', { instanceId }).catch(() => {});
    },
  };
}
