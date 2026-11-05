/** Codex importer contract check against current Archon source, only in a temporary target.
 * ARCHON_ROOT=... tsx --tsconfig <source-paths.json> tests/verify_codex_native.mts
 * Optional CODEX_SOURCE + CODEX_SESSION_IDS (comma-separated) must point at a source snapshot.
 * Other adapters: SOURCE_TYPE, SOURCE_PATH, SOURCE_IDS; optional SOURCE_WORKSPACE / SOURCE_ALL.
 */
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = process.env.ARCHON_ROOT;
assert(root);
const load = (path: string) => import(pathToFileURL(join(root, 'packages/local-runtime-v2/src', path)).href);
const { DatabaseClient } = await load('infra/db/client.ts');
const { initializeDatabase } = await load('infra/db/initialize.ts');
const { createSessionRepository } = await load('service/session-system/sessions/repo/drizzle.ts');
const { createMessageRepository } = await load('service/session-system/messages/repo/drizzle.ts');
const { createSessionSystemCanonicalHistoryProvider } = await load('service/session-system/messages/history/canonical-history-provider.ts');
const { createReleasedSessionHistoryReader } = await load('service/session-system/messages/history/released-session-history-reader.ts');
const { createHistoryPersistenceRepository } = await load('service/session-system/legacy-migration/repo/history-checkpoint.ts');
const { createLegacyHistorySourceReader } = await load('service/session-system/legacy-migration/repo/pi-history-source.ts');
const { createUserMessageId } = await load('service/session-system/shared/user-message-id.ts');
const { canonicalActiveHistoryRevision } = await load('infra/file/canonical-history.ts');
const temp = realpathSync(mkdtempSync(join(tmpdir(), 'codex-native-')));
const dataDir = join(temp, 'target');
const client = new DatabaseClient({ dataDir });
const python = process.env.PYTHON || 'python3';
const script = fileURLToPath(new URL('../scripts/migrate.py', import.meta.url));
try {
  await initializeDatabase({ database: client, dataDir });
  const sessions = createSessionRepository({ db: client.db });
  await sessions.create({ sessionId: 'existing', agentName: 'mavis', workspaceDir: temp,
    runtime: 'pi-agent', sessionType: 'branch', sessionKind: 'conversation', title: 'Existing native session',
    sessionDataVersion: 4, sessionOrigin: 'local-runtime' });
  const previous = client.rawDb.prepare('SELECT * FROM local_runtime_sessions WHERE session_id=?').get('existing');
  const sourceType = process.env.SOURCE_TYPE || 'codex';
  const externalSource = process.env.SOURCE_PATH || process.env.CODEX_SOURCE;
  const source = externalSource || join(temp, 'source');
  const ids = (process.env.SOURCE_IDS || process.env.CODEX_SESSION_IDS)?.split(',') || ['11111111-1111-1111-1111-111111111111'];
  assert(sourceType === 'codex' || externalSource, 'SOURCE_PATH is required for other source adapters');
  if (!externalSource) execFileSync(python, ['-c', `
import pathlib,json,sys
root=pathlib.Path(sys.argv[1]);(root/'sessions').mkdir(parents=True)
sid=sys.argv[3]
def msg(t):return {'type':'message','role':'user','content':[{'type':'input_text','text':t}]}
rows=[('session_meta',{'id':sid,'cwd':sys.argv[2]}),
 ('response_item',msg('# Files mentioned by the user:\\n## input.txt: /tmp/input.txt\\n## My request:\\nPRESERVE REAL REQUEST')),
 ('compacted',{'message':'DECISION LANTERN-73','replacement_history':[msg('DECISION LANTERN-73')]}),
 ('response_item',msg('CONTINUE REQUEST'))]
p=root/'sessions'/('rollout-date-'+sid+'_22222222-2222-2222-2222-222222222222.jsonl')
p.write_text(''.join(json.dumps({'timestamp':'2026-09-15T12:00:00Z','type':k,'payload':v})+'\\n' for k,v in rows))
`, source, temp, ids[0]]);
  const bulk = (process.env.SOURCE_ALL || process.env.CODEX_BULK) === '1';
  const reportPath = join(temp, 'bulk.json');
  const args = [script, 'apply', '--source', sourceType, '--source-db', source, '--target-data-dir', dataDir,
    '--report', reportPath, '--batch-size', '1', ...(bulk ? ['--all'] : ids.flatMap(id => ['--session', id]))];
  if (process.env.SOURCE_WORKSPACE) args.push('--workspace', process.env.SOURCE_WORKSPACE);
  if (process.env.SOURCE_ALLOW_REFERENCES === '1') args.push('--allow-reference-only');
  if (process.env.CONTEXT_SUMMARY_DIR) args.push('--context-summary-dir', process.env.CONTEXT_SUMMARY_DIR);
  {
    const preview = [...args]; preview[1] = 'plan';
    const planned = JSON.parse(execFileSync(python, preview, { encoding: 'utf8' }));
    assert.equal(planned.counts.ready, ids.length);
  }
  const outcome = JSON.parse(execFileSync(python, args, { encoding: 'utf8' }));
  const result = { imported: outcome.counts.imported, sessions: JSON.parse(readFileSync(reportPath, 'utf8')).sessions.map((entry: any) => entry.plan) };
  assert.equal(result.imported, ids.length);
  const messages = createMessageRepository({ db: client.db });
  const checkpoints = createHistoryPersistenceRepository({ db: client.db });
  const released = createReleasedSessionHistoryReader({ dataDir, sessions });
  const provider = () => createSessionSystemCanonicalHistoryProvider({ dataDir, sessions, legacyHistory: {
    sources: createLegacyHistorySourceReader({ db: client.db, readLedgerSnapshot: (id: string) => released.readLedgerSnapshot(id) }), checkpoints,
  } });
  const evidence = [];
  for (const row of result.sessions) {
    const file = join(dataDir, 'v2/sessions', row.historyRelativeDir, 'messages.jsonl');
    const records = readFileSync(file, 'utf8').trim().split('\n').map(JSON.parse);
    assert.equal((await checkpoints.getCheckpoint(row.targetId)).targetRevision, canonicalActiveHistoryRevision(records));
    const display = await messages.list(row.targetId);
    const before = await provider().read(row.targetId);
    assert.equal(before.messages.length, row.canonicalMessageCount);
    if (!externalSource) {
      assert(JSON.stringify(display).includes('PRESERVE REAL REQUEST'));
      assert(!JSON.stringify(before).includes('PRESERVE REAL REQUEST'));
      assert(JSON.stringify(before).includes('LANTERN-73'));
    }
    const after = await provider().append({ sessionId: row.targetId, turnId: 'test-continuation', reason: 'messageDelta',
      operation: { id: 'test-append', kind: 'append' }, messages: [{ role: 'user', content: [{ type: 'text', text: '继续' }], timestamp: Date.now() }],
      identityHints: [{ index: 0, messageId: createUserMessageId({ sessionId: row.targetId, messageKey: 'test-continuation' }), source: 'display-user' }] });
    assert.deepEqual(after.messages.slice(0, before.messages.length), before.messages);
    assert.deepEqual((await provider().read(row.targetId)).messages, after.messages);
    evidence.push({ sourceId: row.sourceId, display: row.messageCount, canonical: row.canonicalMessageCount, appendAndReload: true });
  }
  assert.equal(JSON.parse(execFileSync(python, args, { encoding: 'utf8' })).status, 'completed');
  assert.deepEqual(client.rawDb.prepare('SELECT * FROM local_runtime_sessions WHERE session_id=?').get('existing'), previous);
  console.log(JSON.stringify({ sourceType, bulk, nativeHistory: evidence, existingSessionUnchanged: true, idempotentAfterContinuation: true }));
} finally {
  client.close();
  rmSync(temp, { recursive: true, force: true });
}
