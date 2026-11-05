/** Optional integration check against a prepared agent-archon source checkout.
 * ARCHON_ROOT=/path/to/archon PYTHON=/path/to/python3 tsx --tsconfig <archon-source-paths.json> tests/verify_native.mts
 * Uses an isolated temporary directory; never opens the user's profile.
 */
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = process.env.ARCHON_ROOT;
assert(root, 'Set ARCHON_ROOT to a prepared agent-archon source checkout');
const load = (path: string) => import(pathToFileURL(join(root, 'packages/local-runtime-v2/src', path)).href);
const { DatabaseClient } = await load('infra/db/client.ts');
const { initializeDatabase } = await load('infra/db/initialize.ts');
const { createSessionRepository } = await load('service/session-system/sessions/repo/drizzle.ts');
const { createMessageRepository } = await load('service/session-system/messages/repo/drizzle.ts');
const { createSessionSystemCanonicalHistoryProvider } = await load('service/session-system/messages/history/canonical-history-provider.ts');
const { createReleasedSessionHistoryReader } = await load('service/session-system/messages/history/released-session-history-reader.ts');
const { createHistoryPersistenceRepository } = await load('service/session-system/legacy-migration/repo/history-checkpoint.ts');
const { createLegacyHistorySourceReader } = await load('service/session-system/legacy-migration/repo/pi-history-source.ts');
const { canonicalActiveHistoryRevision } = await load('infra/file/canonical-history.ts');
const { ConversationActionProjectionService } = await load('service/session-system/messages/query/conversation-action-projection.ts');
const { eligible } = await load('service/session-system/projects/sidebar/predicate.ts');
const { sessions: table } = await load('infra/db/schema/sessions.ts');
const { projects } = await load('infra/db/schema/projects.ts');
const { createUserMessageId } = await load('service/session-system/shared/user-message-id.ts');
const { eq } = createRequire(join(root, 'package.json'))('drizzle-orm');
const python = process.env.PYTHON || 'python3';
const script = fileURLToPath(new URL('../scripts/migrate.py', import.meta.url));
const temp = realpathSync(mkdtempSync(join(tmpdir(), 'session-migration-native-')));
const dataDir = join(temp, 'target');
const source = join(temp, 'source.sqlite');
const client = new DatabaseClient({ dataDir });
try {
  await initializeDatabase({ database: client, dataDir });
  const sessions = createSessionRepository({ db: client.db });
  await sessions.create({ sessionId: 'native-seed', agentName: 'mavis', workspaceDir: temp,
    runtime: 'pi-agent', sessionType: 'branch', sessionKind: 'conversation', title: 'Native seed',
    sessionDataVersion: 4, sessionOrigin: 'local-runtime' });
  const project = client.rawDb.prepare('SELECT project_id FROM local_runtime_sessions WHERE session_id=?').get('native-seed');
  client.rawDb.prepare('UPDATE local_runtime_projects SET hidden=1 WHERE project_id=?').run(project.project_id);
  const legacy = JSON.stringify({ sessionId: 'legacy-stub', agentName: 'mavis', title: '真实旧会话', sessionDataVersion: 4 });
  client.rawDb.prepare('INSERT INTO local_runtime_sessions(session_id,columnar_version,record_json,updated_at_ms) VALUES(?,0,?,1)').run('legacy-stub', legacy);
  execFileSync(python, ['-c', `
import sqlite3,json,sys
c=sqlite3.connect(sys.argv[1]);c.executescript('''
CREATE TABLE session(id TEXT,directory TEXT,title TEXT,time_created INTEGER,time_updated INTEGER);
CREATE TABLE message(id TEXT,session_id TEXT,time_created INTEGER,data TEXT,sequence INTEGER);
CREATE TABLE part(id TEXT,message_id TEXT,session_id TEXT,time_created INTEGER,data TEXT,sequence INTEGER);
''')
c.execute('INSERT INTO session VALUES(?,?,?,?,?)',('source',sys.argv[2],'迁移搜索 🐈',1700000000000,1700000001000))
for i,role in enumerate(('user','assistant')):
 mid='m'+str(i);c.execute('INSERT INTO message VALUES(?,?,?,?,?)',(mid,'source',1700000000000+i,json.dumps({'role':role}),i))
 c.execute('INSERT INTO part VALUES(?,?,?,?,?,?)',(mid+'p',mid,'source',1700000000000+i,json.dumps({'type':'text','text':'中文历史 '+role}),0))
c.execute('INSERT INTO part VALUES(?,?,?,?,?,?)',('tool','m1','source',1700000000001,json.dumps({'type':'tool','tool':'bash','callID':'old-call','state':{'status':'running','input':{'command':'NEVER_EXECUTE'},'output':'preserved line\\n'*800}}),1))
c.execute('ALTER TABLE session ADD COLUMN task_type TEXT')
c.execute('ALTER TABLE session ADD COLUMN parent_id TEXT')
c.execute("UPDATE session SET task_type='fork',parent_id='original-parent'")
c.execute("INSERT INTO session(id,directory,title,time_created,time_updated,task_type,parent_id) VALUES('child',?,'Internal subagent',1700000000002,1700000001002,'subagent_child','source')",(sys.argv[2],))
c.commit();c.close()
`, source, temp]);
  const reportPath = join(temp, 'migration-job.json');
  const args = [script, 'apply', '--source', 'zcode', ...(process.env.MIGRATION_SCOPE === 'selected' ? ['--session', 'source'] : ['--all']), '--report', reportPath, '--source-db', source, '--target-data-dir', dataDir];
  const rejected = [...args]; rejected[1] = 'plan';
  const blocked = JSON.parse(execFileSync(python, rejected, { encoding: 'utf8' }));
  assert.equal(blocked.counts.incompatible, 1);
  const rejectedReport = JSON.parse(readFileSync(reportPath, 'utf8'));
  assert.match(rejectedReport.sessions[0].error, /restore-projects/);
  rmSync(reportPath);
  args.push('--restore-projects');
  const preview = [...args]; preview[1] = 'plan';
  execFileSync(python, preview, { encoding: 'utf8' });
  const outcome = JSON.parse(execFileSync(python, args, { encoding: 'utf8' }));
  const saved = JSON.parse(readFileSync(reportPath, 'utf8'));
  const result = { imported: outcome.counts.imported, sessions: saved.sessions.map((entry: any) => entry.plan), backup: saved.batches[0].backup };
  assert.equal(result.imported, 1);
  assert.equal(saved.excludedSessions.length, process.env.MIGRATION_SCOPE === 'selected' ? 0 : 1);
  assert.equal(client.rawDb.prepare("SELECT count(*) AS n FROM local_runtime_sessions WHERE title LIKE '%Internal subagent%'").get().n, 0);
  const row = result.sessions[0];
  assert(await sessions.get(row.targetId));
  assert.equal((await sessions.searchPage({ keyword: '迁移搜索 🐈' })).sessions[0].sessionId, row.targetId);
  const visible = client.db.select({ id: table.sessionId }).from(table).innerJoin(projects, eq(table.projectId, projects.projectId)).where(eligible()).all();
  assert(visible.some((x: {id: string}) => x.id === row.targetId));
  assert(!visible.some((x: {id: string}) => x.id === 'native-seed'));
  assert.equal(client.rawDb.prepare('SELECT record_json FROM local_runtime_sessions WHERE session_id=?').get('legacy-stub').record_json, legacy);
  const messages = createMessageRepository({ db: client.db });
  const display = await messages.list(row.targetId);
  const historical = display.messages[1].tool_calls[0];
  assert.equal(historical.tool_name, '历史工具记录');
  assert.equal(historical.tool_call_status, 2);
  const { sanitizeWireToolCallResultData } = await import(pathToFileURL(join(root, 'packages/agent-core/src/event-bridge/display-sanitize.ts')).href);
  const sanitized = sanitizeWireToolCallResultData(historical.tool_call_result_data);
  assert.equal(JSON.parse(sanitized).content[0].text.includes('preserved line\n'.repeat(800)), true);
  const projection = new ConversationActionProjectionService({ sessions, messages, operations: { blocksSession: async () => false } });
  const actions = await projection.project({ sessionId: row.targetId, messages: display.messages, mutationActive: false });
  assert.equal(actions[0].actions.rewind, true);
  assert.equal(actions[1].actions.fork, true);
  const released = createReleasedSessionHistoryReader({ dataDir, sessions });
  const checkpoints = createHistoryPersistenceRepository({ db: client.db });
  const provider = () => createSessionSystemCanonicalHistoryProvider({ dataDir, sessions, legacyHistory: {
    sources: createLegacyHistorySourceReader({ db: client.db, readLedgerSnapshot: (id: string) => released.readLedgerSnapshot(id) }), checkpoints,
  } });
  const history = provider();
  const records = readFileSync(join(dataDir, 'v2/sessions', row.historyRelativeDir, 'messages.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
  assert.equal((await checkpoints.getCheckpoint(row.targetId)).targetRevision, canonicalActiveHistoryRevision(records));
  await provider().read(row.targetId);
  client.rawDb.prepare('DELETE FROM local_runtime_pi_history_file_migrations WHERE session_id=?').run(row.targetId);
  await assert.rejects(() => provider().read(row.targetId), /Canonical history materialization is ambiguous/);
  const repair = JSON.parse(execFileSync(python, [script, 'repair', '--target-data-dir', dataDir, '--target-session', row.targetId], { encoding: 'utf8' }));
  assert.equal(repair.status, 'repaired');
  const before = await history.read(row.targetId);
  assert.equal(before.messages.length, 2);
  const after = await history.append({ sessionId: row.targetId, turnId: 'continuation', reason: 'messageDelta',
    operation: { id: 'test-append', kind: 'append' }, messages: [{ role: 'user', content: [{ type: 'text', text: '继续' }], timestamp: Date.now() }],
    identityHints: [{ index: 0, messageId: createUserMessageId({ sessionId: row.targetId, messageKey: 'continuation' }), source: 'display-user' }] });
  assert.deepEqual(after.messages.slice(0, 2), before.messages);
  assert.equal(after.messages.length, 3);
  assert.deepEqual((await provider().read(row.targetId)).messages, after.messages);
  const bytes = readFileSync(join(dataDir, 'v2/sessions', row.historyRelativeDir, 'messages.jsonl'));
  const repeated = JSON.parse(execFileSync(python, args, { encoding: 'utf8' }));
  assert.equal(repeated.status, 'completed');
  assert.equal((await provider().read(row.targetId)).messages.length, 3);
  assert.deepEqual(readFileSync(join(dataDir, 'v2/sessions', row.historyRelativeDir, 'messages.jsonl')), bytes);
  assert.equal(client.rawDb.prepare('PRAGMA journal_mode').get().journal_mode, 'wal');
  console.log(JSON.stringify({ subagentsExcluded: true, userForkPreserved: true, productionHistoryInitialization: true, oldBugReproduced: true, repair: true, nativeRevisionMatches: true, nativeSchema: true, walBackup: true, legacyPreserved: true, search: true, actions: true,
    restoredProjectVisible: true, previousSessionsHidden: true, appendPrefixPreserved: true, repeatUnchanged: true }));
} finally {
  client.close();
  rmSync(temp, { recursive: true, force: true });
}
