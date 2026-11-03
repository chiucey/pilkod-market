const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/iu;
export function readWorkbenchTarget(queryOrHash) {
  const entries = [...new URLSearchParams(queryOrHash.replace(/^[?#]/, ''))];
  if (entries.length !== 1) return;
  const [kind, id] = entries[0];
  if ((kind === 'draft' || kind === 'batch' || kind === 'setup') && UUID.test(id)) return { kind, id };
}
