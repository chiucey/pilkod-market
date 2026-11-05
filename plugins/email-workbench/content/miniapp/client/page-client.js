// A local runtime restart rotates CSRF, but does not expire the mailbox account.
// Only retry a request the server explicitly rejected BEFORE dispatching it.
export function createPageClient(fetcher) {
  let token;
  let refreshing;
  const fail = (code) => { const error = new Error(code); error.code = code; throw error; };
  async function decode(url, init) {
    try {
      const response = await fetcher(url, init);
      return { response, value: await response.json() };
    } catch { fail('OUTCOME_UNKNOWN'); }
  }
  async function bootstrap() {
    if (!refreshing) refreshing = (async () => {
      const { response, value } = await decode('/email/bootstrap', { cache: 'no-store' });
      if (!response.ok || typeof value.csrf !== 'string' || !value.csrf) fail('CONNECTOR_UNAVAILABLE');
      token = value.csrf;
      return token;
    })().finally(() => { refreshing = undefined; });
    return refreshing;
  }
  async function call(route, input = {}, signal) {
    const body = JSON.stringify(input);
    for (let attempt = 0; attempt < 2; attempt++) {
      const usedToken = token;
      const { response, value } = await decode(`/email/api/${route}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Email-Csrf': usedToken },
        body, cache: 'no-store', signal,
      });
      if (attempt === 0 && response.status === 403 && value.error === 'SESSION_STALE' && value.rejectedBeforeDispatch === true) {
        if (token === usedToken) await bootstrap();
        if (signal?.aborted) fail('OUTCOME_UNKNOWN');
        continue;
      }
      if (!response.ok || value.error) fail(value.error ?? 'REQUEST_FAILED');
      return value;
    }
  }
  return { bootstrap, call };
}
