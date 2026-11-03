/** Per-window state. Never shared across imports, accounts or MiniApp windows. */
export function createPageState({
  Controller = globalThis.AbortController,
  cancelTimer = (timer) => clearTimeout(timer),
  revokeObjectURL = (url) => URL.revokeObjectURL(url),
} = {}) {
  const state = {
    account: {
      accounts: /** @type {Array<Record<string, unknown>>} */ ([]),
      historyAccounts: [], preferences: { revision: 0, accounts: [] },
      accountId: '', accountsLoaded: false,
    },
    navigation: {
      view: 'inbox', pendingNavigation: undefined, pendingWorkbenchTarget: false,
      settingsReturn: undefined,
    },
    inbox: {
      cursor: undefined, query: undefined, resultScope: undefined, mailboxPages: new Map(), loadedMessages: [],
      folderScope: undefined, workCursor: undefined, folderChoices: new Map(),
      scopeFilters: new Map(), folderCache: new Map(),
    },
    composer: {
      // Pending upload bytes and editing state stay in this page's memory.
      dirty: false, editSequence: 0, editor: undefined, pendingTransfer: undefined,
      draftSelection: new Map(), draftPoll: undefined, autosaveTimer: undefined,
      autosaveBlocked: false, saving: undefined, editLease: undefined,
    },
    reader: {
      selectedMessageKey: undefined, frame: undefined, images: new Set(), assets: new Set(),
    },
    lifecycle: {
      csrf: undefined, busy: false, disposed: false, localDataCleared: false,
      mailCheckTimer: undefined,
    },
  };
  const scopes = new Map(['inbox', 'reader', 'list'].map((name) => [name, {
    generation: 0, controller: new Controller(),
  }]));
  let retired = false;
  function scope(name) {
    const value = scopes.get(name);
    if (!value) throw new TypeError(`Unknown page request scope: ${name}`);
    return value;
  }
  const requests = {
    generation: (name) => scope(name).generation,
    signal: (name) => scope(name).controller.signal,
    current: (name, generation) => !state.lifecycle.disposed && scope(name).generation === generation,
    invalidate(name) {
      const value = scope(name);
      value.controller.abort();
      value.controller = new Controller();
      if (state.lifecycle.disposed) value.controller.abort();
      return ++value.generation;
    },
  };
  function releaseReader() {
    requests.invalidate('reader');
    state.reader.frame?.dispose();
    state.reader.frame = undefined;
    for (const url of state.reader.images) revokeObjectURL(url);
    state.reader.images.clear();
    for (const asset of state.reader.assets) asset.dispose();
    state.reader.assets.clear();
  }
  function suspend({ permanent = false } = {}) {
    if (retired) return false;
    state.lifecycle.disposed = true;
    requests.invalidate('inbox');
    requests.invalidate('list');
    releaseReader();
    for (const [owner, key] of [
      [state.composer, 'draftPoll'], [state.composer, 'autosaveTimer'],
      [state.lifecycle, 'mailCheckTimer'],
    ]) {
      cancelTimer(owner[key]);
      owner[key] = undefined;
    }
    retired = permanent;
    return true;
  }
  function resume() {
    if (retired) return false;
    state.lifecycle.disposed = false;
    // A hidden page's work must not become current again after a BFCache restore.
    for (const name of scopes.keys()) requests.invalidate(name);
    return true;
  }
  return Object.assign(state, { requests, releaseReader, suspend, resume });
}
