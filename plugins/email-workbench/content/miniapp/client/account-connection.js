import { t, tt, locale } from './i18n.js';
// Form credentials are never included in Agent handoffs or browser storage.
import { authorizationPrompt, authorizationHandoffError } from './account-authorization.js';
export const vaultErrors = new Set([
  'VAULT_LOCKED', 'VAULT_KEY_MISSING', 'VAULT_INCOMPLETE', 'VAULT_CORRUPT', 'VAULT_CLEAR_PENDING',
  'CREDENTIAL_UNAVAILABLE', 'CREDENTIAL_DENIED', 'CREDENTIAL_LOCKED',
  'STORAGE_UNAVAILABLE', 'STORAGE_CORRUPT',
]);
export function createAccountConnection(ctx) {
  const { el, api } = ctx;
  let dialog;
  let secretFields = [];
  const secretToggles = new Map();
  let pending = false;
  let operationId;
  let returnFocus;
  function hideSecrets() {
    for (const input of secretFields) {
      input.type = 'password';
      const toggle = secretToggles.get(input);
      if (toggle) {
        toggle.button.textContent = t('显示');
        toggle.button.setAttribute('aria-pressed', 'false');
        toggle.button.setAttribute('aria-label', tt`显示${toggle.label}`);
      }
    }
  }
  function clearSecrets() {
    hideSecrets();
    for (const input of secretFields) input.value = '';
  }
  window.addEventListener('blur', hideSecrets);
  document.addEventListener('visibilitychange', () => { if (document.hidden) hideSecrets(); });
  function dispose() {
    const previousFocus = returnFocus;
    returnFocus = undefined;
    clearSecrets();
    secretFields = [];
    secretToggles.clear();
    dialog?.remove();
    dialog = undefined;
    operationId = undefined;
    if (previousFocus?.isConnected && !previousFocus.disabled) previousFocus.focus({ preventScroll: true });
  }
  function makeDialog(title) {
    const previousFocus = document.activeElement;
    dispose();
    returnFocus = previousFocus;
    const node = el('dialog', undefined, 'account-connection');
    node.id = 'account-connection';
    node.setAttribute('aria-labelledby', 'connection-title');
    const heading = el('h2', title);
    heading.id = 'connection-title';
    node.append(heading);
    document.body.append(node);
    dialog = node;
    return node;
  }
  function action(text, callback, style) {
    const node = el('button', text, style);
    node.type = 'button';
    node.addEventListener('click', () => void callback());
    return node;
  }
  function errorText(error) {
    return ctx.error(error?.code) ?? t('连接未完成，请核对授权码和服务商状态后重试。');
  }
  async function open(result = {}, options = {}) {
    if (dialog?.open && operationId && operationId === (result.operationId ?? result.id)) {
      dialog.querySelector('input')?.focus();
      return;
    }
    if (pending) return;
    if (dialog?.open && secretFields.some((input) => input.value)) {
      ctx.notice(t('当前连接表单仍有未提交的输入，请完成或取消后再打开另一项连接。'));
      return;
    }
    const setup = result.setup ?? options;
    const existing = ctx.accounts().find((item) => item.address === (setup.address ?? result.address));
    const providers = (await api('accounts/providers')).filter(Boolean);
    let configuration;
    let authorizationProvider;
    let authorizationPending = false;
    let authorizationSent = false;
    let detectionGeneration = 0;
    let detectionTimer;
    const node = makeDialog(existing ? t('更新邮箱连接') : t('连接邮箱'));
    operationId = result.operationId ?? result.id;
    const currentOperation = operationId;
    let finished = false;
    const fromTask = Boolean(options.fromTask);
    node.append(el('p', existing ? t('更新此邮箱的授权码，保留现有收发服务器配置。') : fromTask ? t('连接邮箱后，继续这次邮件任务。') : t('填写邮箱地址与协议凭据，连接你的邮箱。'), 'connection-intro'));
    const form = el('form', undefined, 'connection-form');
    form.id = 'account-connect-form';
    form.autocomplete = 'off';
    const fields = el('fieldset');
    fields.className = 'connection-fields';
    const field = (key, labelText, value = '', type = 'text', parent = fields) => {
      const label = el('label', labelText);
      const input = el('input');
      input.id = `connect-${key}`;
      input.type = type;
      input.value = String(value);
      input.required = true;
      input.autocomplete = type === 'password' ? 'new-password' : 'off';
      input.spellcheck = false;
      if (type === 'password') {
        const row = el('span', undefined, 'connection-secret-input');
        const toggle = key === 'password' ? action(t('让助手协助获取'), () => requestAuthorization()) : action(t('显示'), () => {
          const visible = input.type === 'password';
          input.type = visible ? 'text' : 'password';
          toggle.textContent = visible ? t('隐藏') : t('显示');
          toggle.setAttribute('aria-pressed', String(visible));
          toggle.setAttribute('aria-label', `${visible ? t('隐藏') : t('显示')}${labelText}`);
        });
        if (key === 'password') {
          toggle.id = 'connect-get-authorization';
          toggle.className = 'connection-code-action';
          toggle.setAttribute('aria-describedby', 'connect-authorization-status');
        } else {
          toggle.setAttribute('aria-label', tt`显示${labelText}`);
          toggle.setAttribute('aria-pressed', 'false');
          toggle.setAttribute('aria-controls', input.id);
          secretToggles.set(input, { button: toggle, label: labelText });
        }
        row.append(input, toggle);
        label.append(row);
        secretFields.push(input);
      } else label.append(input);
      parent.append(label);
      return input;
    };
    const providerLabel = el('label', t('邮箱服务商'));
    const provider = el('select'); provider.id = 'connect-provider';
    const placeholder = el('option', t('请选择服务商')); placeholder.value = ''; provider.append(placeholder);
    for (const item of providers) { const option = el('option', t(item.label)); option.value = item.id; provider.append(option); }
    const customOption = el('option', t('其他服务商 · 手动配置服务器')); customOption.value = 'custom'; provider.append(customOption);
    const unsupported = el('option', t('未列出／暂不支持')); unsupported.value = 'unsupported'; provider.append(unsupported);
    provider.value = providers.some((item) => item.id === setup.provider) ? setup.provider : '';
    providerLabel.append(provider); providerLabel.hidden = true;
    const address = field('address', t('邮箱地址'), setup.address ?? result.address ?? existing?.address ?? '', 'email');
    address.maxLength = 320;
    address.placeholder = t('你的邮箱地址');
    address.readOnly = !!existing;
    fields.append(providerLabel);
    let providerDomain = address.value.trim().split('@')[1]?.toLowerCase() ?? '';
    let acceptedTypo = '';
    const typo = el('div', undefined, 'connection-typo'); typo.hidden = true;
    fields.append(typo);
    const customFields = el('fieldset', undefined, 'connection-servers');
    customFields.hidden = true; customFields.disabled = true;
    const endpoints = {};
    let customInitialized = false;
    function showCustom(value) {
      customFields.hidden = !value;
      customFields.disabled = !value;
      if (!value || customInitialized) return;
      customInitialized = true;
      customFields.append(el('legend', t('收发服务器')), el('p', t('请按邮箱管理员提供的信息填写。授权码会发送到以下服务器进行验证。'), 'muted'));
      for (const [protocol, title, port] of [['imap', t('收信 IMAP'), 993], ['smtp', t('发信 SMTP'), 465]]) {
        const group = el('div', undefined, 'connection-server');
        group.append(el('h3', title));
        const suggested = setup.provider === 'custom' ? setup[protocol] : undefined;
        const host = field(`${protocol}-host`, t('服务器地址'), suggested?.host ?? '', 'text', group);
        host.placeholder = protocol === 'imap' ? 'imap.example.com' : 'smtp.example.com';
        host.maxLength = 253;
        const number = field(`${protocol}-port`, t('端口'), suggested?.port ?? port, 'number', group);
        number.min = '1'; number.max = '65535';
        const securityLabel = el('label', t('加密方式'));
        const security = el('select'); security.id = `connect-${protocol}-security`;
        for (const [key, name] of [['tls', 'SSL / TLS'], ['starttls', 'STARTTLS']]) { const option = el('option', name); option.value = key; security.append(option); }
        security.value = suggested?.security ?? 'tls'; securityLabel.append(security); group.append(securityLabel);
        const username = field(`${protocol}-username`, t('登录用户名'), suggested?.username ?? address.value.trim(), 'text', group);
        username.maxLength = 320;
        endpoints[protocol] = { host, port: number, security, username };
        customFields.append(group);
      }
    }
    fields.append(customFields);
    const password = field('password', t('邮箱授权码'), '', 'password');
    password.maxLength = 4096;
    const getAuthorization = fields.querySelector('#connect-get-authorization');
    const authorizationStatus = el('p', t('将请求填入会话输入框，由你发送后开始协助。'), 'muted connection-authorization-status');
    authorizationStatus.id = 'connect-authorization-status';
    authorizationStatus.setAttribute('role', 'status');
    fields.append(authorizationStatus);
    function resetAuthorization() {
      authorizationSent = false;
      if (!authorizationPending) {
        getAuthorization.disabled = false;
        getAuthorization.textContent = t('让助手协助获取');
      }
      authorizationStatus.textContent = t('将请求填入会话输入框，由你发送后开始协助。');
    }
    async function requestAuthorization() {
      if (pending || authorizationPending || authorizationSent) return;
      if (!address.value.trim() || !address.reportValidity()) {
        authorizationStatus.textContent = t('请先填写正确的邮箱地址。');
        address.focus();
        return;
      }
      const value = address.value.trim();
      const selectedValue = provider.value;
      authorizationPending = true;
      getAuthorization.disabled = true;
      try {
        clearTimeout(detectionTimer);
        await detectProvider();
        if (dialog !== node || address.value.trim() !== value || provider.value !== selectedValue) return;
        if (!authorizationProvider?.webmailUrl?.startsWith('https://')) {
          authorizationStatus.textContent = !typo.hidden ? t('请先核对邮箱后缀，再让助手协助获取。')
            : provider.value === 'custom' ? t('自定义服务器暂无对应的自动获取入口，请使用管理员提供的授权方式。')
            : helpText.textContent;
          return;
        }
        const message = window.mcode?.miniapp?.message;
        if (typeof message?.append !== 'function') {
          authorizationStatus.textContent = t('此窗口无法把请求交给助手，请在应用内打开邮箱工作台，或使用下方官方教程手动获取。');
          return;
        }
        // Explicit allowlist: never serialize the form, configuration or password inputs.
        const prompt = authorizationPrompt({ address: value, provider: authorizationProvider,
          operationId: currentOperation, origin: window.location.origin });
        hideSecrets();
        getAuthorization.textContent = t('正在交给会话…');
        await message.append(prompt);
        if (dialog !== node) return;
        if (address.value.trim() !== value || provider.value !== selectedValue) {
          authorizationStatus.textContent = t('之前的邮箱请求已追加到会话，但当前地址或服务商已改变。请先移除旧请求，再为当前邮箱发起。');
          return;
        }
        authorizationSent = true;
        authorizationStatus.textContent = t('请求已追加到会话输入框。点击发送后，助手会打开邮箱；登录或身份验证时由你完成，之后继续获取并回填。');
      } catch (error) {
        if (dialog !== node) return;
        authorizationStatus.textContent = authorizationHandoffError(error);
        // Unknown delivery must not be automatically or accidentally repeated.
        if (error?.message === 'result_unknown') authorizationSent = true;
      } finally {
        authorizationPending = false;
        getAuthorization.disabled = authorizationSent;
        getAuthorization.textContent = authorizationSent ? t('请到会话继续') : t('让助手协助获取');
      }
    }
    const help = el('p', undefined, 'muted connection-help');
    const helpText = el('span');
    const helpLink = el('a', t('获取授权码帮助'));
    helpLink.target = '_blank';
    helpLink.rel = 'noopener noreferrer';
    help.append(helpText, helpLink);
    fields.insertBefore(help, customFields);
    const advanced = el('details', undefined, 'connection-advanced');
    advanced.append(el('summary', t('显示名称（可选）')));
    const label = field('label', t('显示名称（可选）'), setup.label ?? existing?.label ?? '', 'text', advanced);
    label.required = false;
    label.maxLength = 100;
    const separateLabel = el('label', undefined, 'check');
    const separate = el('input');
    separate.type = 'checkbox'; separate.id = 'connect-separate-password';
    separateLabel.append(separate, document.createTextNode(t('收信和发信使用不同授权码')));
    fields.append(separateLabel);
    const smtpPassword = field('smtp-password', t('发信授权码（SMTP）'), '', 'password', fields);
    smtpPassword.required = false;
    smtpPassword.closest('label').hidden = true;
    separate.addEventListener('change', () => {
      password.closest('label').firstChild.textContent = separate.checked ? t('收信授权码（IMAP）') : t('邮箱授权码');
      smtpPassword.closest('label').hidden = !separate.checked;
      smtpPassword.required = separate.checked;
      if (!separate.checked) { smtpPassword.value = ''; hideSecrets(); }
    });
    fields.append(advanced);
    async function detectProvider() {
      const generation = ++detectionGeneration;
      const value = address.value.trim();
      configuration = undefined;
      authorizationProvider = undefined;
      helpLink.hidden = true;
      showCustom(false);
      typo.hidden = true;
      if (!value || !address.validity.valid) { helpText.textContent = t('填写邮箱地址后自动识别服务商。'); providerLabel.hidden = true; return; }
      if (existing && value === existing.address) {
        configuration = { imap: { ...existing.imap }, smtp: { ...existing.smtp } };
        authorizationProvider = providers.find((item) => item.imap?.host === existing.imap?.host && item.smtp?.host === existing.smtp?.host);
        helpText.textContent = t('沿用此邮箱已经验证的收发连接配置，请输入新的授权码。');
        providerLabel.hidden = true;
        return;
      }
      const detected = await api('accounts/detect', { address: value });
      if (generation !== detectionGeneration || address.value.trim() !== value) return;
      if (detected.status === 'unsupported') {
        helpText.textContent = detected.reason === 'oauth' ? t('此服务商需要 OAuth，目前不支持授权码连接。') : t('此服务商需要 Bridge，目前暂不支持。');
        providerLabel.hidden = true;
        return;
      }
      const domain = value.split('@')[1]?.toLowerCase();
      const corrections = { 'qq.cq': 'qq.com', '163.cpm': '163.com', '126.cpm': '126.com', 'qq.cpm': 'qq.com', 'gmail.cpm': 'gmail.com', '163.con': '163.com', 'qq.con': 'qq.com', 'gmail.con': 'gmail.com' };
      if (!detected.provider && corrections[domain] && acceptedTypo !== value) {
        const corrected = `${value.split('@')[0]}@${corrections[domain]}`;
        typo.hidden = false;
        typo.replaceChildren(el('p', tt`邮箱后缀可能拼错了，是否为 ${corrected}？`),
          action(tt`改为 ${corrections[domain]}`, () => { address.value = corrected; address.dispatchEvent(new Event('input')); }),
          action(t('保留此地址'), () => { acceptedTypo = value; void detectProvider(); }));
        providerLabel.hidden = true;
        helpText.textContent = t('请先确认邮箱后缀。');
        return;
      }
      if (!detected.provider && provider.value === 'custom') {
        providerLabel.hidden = false;
        showCustom(true);
        configuration = Object.fromEntries(Object.entries(endpoints).map(([protocol, inputs]) => [protocol, {
          host: inputs.host.value.trim(), port: Number(inputs.port.value), security: inputs.security.value, username: inputs.username.value.trim(),
        }]));
        helpText.textContent = t('使用下方明确填写的收发服务器。请使用客户端授权码或应用密码。');
        return;
      }
      const selected = detected.provider ?? providers.find((item) => item.id === provider.value);
      providerLabel.hidden = !!detected.provider;
      if (!selected) { helpText.textContent = provider.value === 'unsupported' ? t('暂不支持此邮箱服务商。输入已保留。') : t('无法从此域名识别服务器。请选择邮箱实际托管的服务商，或手动配置收发服务器。'); return; }
      authorizationProvider = selected;
      configuration = Object.fromEntries(['imap', 'smtp'].map((protocol) => {
        const endpoint = selected[protocol];
        return [protocol, { host: endpoint.host, port: endpoint.port, security: endpoint.security, username: endpoint.usernameFormat === 'local' ? value.split('@')[0] : value }];
      }));
      helpText.textContent = `${t(selected.label)} · ${selected.note?.[locale()] ?? t('请开启 IMAP / SMTP 并使用客户端授权码或应用密码。')} `;
      if (selected.helpUrl?.startsWith('https://')) { helpLink.hidden = false; helpLink.href = selected.helpUrl; }
    }
    address.addEventListener('input', () => {
      resetAuthorization();
      const domain = address.value.trim().split('@')[1]?.toLowerCase() ?? '';
      if (domain !== providerDomain) {
        provider.value = ''; providerDomain = domain; acceptedTypo = '';
        // A new domain requires a new explicit server choice.
        customFields.replaceChildren(); customInitialized = false; showCustom(false);
      }
      configuration = undefined; detectionGeneration += 1; clearTimeout(detectionTimer);
      detectionTimer = setTimeout(() => { void detectProvider().catch(() => { helpText.textContent = t('暂未完成识别，可点击验证重试。'); }); }, 180);
    });
    provider.addEventListener('change', () => { resetAuthorization(); void detectProvider().catch(() => { helpText.textContent = t('服务商信息暂不可用，请重试。'); }); });
    await detectProvider();
    const privacy = el('details', undefined, 'connection-privacy');
    privacy.append(el('summary', t('凭据与数据如何保存')), el('p', t('授权码按 MCode 登录账号在云端加密保存，草稿和附件保留在本机。助手协助获取时，工具记录可能包含新生成的授权码。'), 'muted'));
    fields.append(privacy);
    const status = el('p', '', 'connection-status muted');
    status.id = 'connect-status';
    status.setAttribute('role', 'status');
    const buttons = el('div', undefined, 'actions');
    const cancel = action(t('取消'), async () => {
      if (pending) return;
      dispose();
      if (currentOperation) await api('accounts/cancel', { id: currentOperation }).catch(() => {});
    });
    const submit = el('button', existing ? t('验证并更新') : t('验证并连接'), 'primary');
    submit.type = 'submit'; submit.id = 'connect-submit';
    buttons.append(cancel, submit);
    const retry = action(t('解锁本机邮箱并重试'), async () => {
      retry.disabled = true;
      try {
        await api('vault/unlock', { retry: true });
        retry.hidden = true;
        status.textContent = t('本机邮箱已解锁，请重新输入授权码，再验证并连接。');
        password.focus();
        status.className = 'connection-status muted';
      } catch (error) { status.textContent = errorText(error); }
      finally { retry.disabled = false; }
    });
    retry.hidden = true;
    const footer = el('div', undefined, 'connection-footer');
    footer.append(status, retry, buttons);
    // Keep scrolling on a regular block: fieldset's anonymous content box can
    // otherwise overflow a flex item and scroll the entire dialog on focus.
    const scroll = el('div', undefined, 'connection-scroll');
    scroll.append(fields);
    form.append(scroll, footer);
    node.append(form);
    node.addEventListener('cancel', (event) => {
      event.preventDefault();
      if (!pending) { if (finished) dispose(); else cancel.click(); }
    });
    node.addEventListener('close', clearSecrets);
    async function watchConnectionStage() {
      if (!currentOperation) return;
      while (pending && dialog === node) {
        try {
          const progress = await api('accounts/setup', { id: currentOperation, waitMs: 500 });
          if (!pending || dialog !== node) return;
          if (progress.status === 'initializing') status.textContent = t('正在安全保存邮箱信息…');
          if (progress.status === 'verifying') status.textContent = t('正在验证邮箱连接…');
          if (!['waiting_for_input', 'initializing', 'verifying'].includes(progress.status)) return;
        } catch { return; } // The connection submission remains authoritative if status reads fail.
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
    }
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (pending || !form.reportValidity()) return;
      pending = true; submit.disabled = true;
      try { await detectProvider(); } catch (error) { pending = false; submit.disabled = false; status.textContent = errorText(error); return; }
      if (!form.reportValidity()) { pending = false; submit.disabled = false; return; }
      if (!configuration) { pending = false; submit.disabled = false; status.textContent = helpText.textContent; status.className = 'connection-status error'; return; }
      const input = {
        label: label.value.trim() || address.value.trim(), address: address.value.trim(),
        imap: { ...configuration.imap }, smtp: { ...configuration.smtp },
        imapPassword: password.value, smtpPassword: separate.checked ? smtpPassword.value : password.value,
      };
      hideSecrets();
      pending = true;
      fields.disabled = true; cancel.disabled = true; submit.disabled = true;
      status.textContent = t('正在连接邮箱…');
      status.className = 'connection-status muted';
      status.setAttribute('role', 'status');
      let connected;
      void watchConnectionStage();
      try {
        connected = await api('accounts/connect', { ...(currentOperation ? { operationId: currentOperation } : {}), input });
        clearSecrets();
        await ctx.connected({ ...connected, status: 'connected' });
      } catch (error) {
        if (vaultErrors.has(error?.code)) clearSecrets();
        status.textContent = errorText(error) + (vaultErrors.has(error?.code) ? t(' 已清除本次授权码，请解锁后重新输入。') : '');
        status.className = 'connection-status error';
        status.setAttribute('role', 'alert');
        retry.hidden = !vaultErrors.has(error?.code);
      } finally {
        input.imapPassword = ''; input.smtpPassword = '';
        pending = false;
        fields.disabled = false; cancel.disabled = false; submit.disabled = false;
      }
      if (!connected) return;
      finished = true;
      const successTitle = el('h2', t('邮箱已连接'));
      successTitle.id = 'connection-title';
      node.replaceChildren(successTitle, el('p', connected.account.address, 'connection-address'));
      const successActions = el('div', undefined, 'actions');
      const prefs = connected.preferences;
      const selected = prefs?.defaultAccountId === connected.account.id;
      node.append(el('p', selected ? t('此邮箱是当前邮箱，也将用于新邮件。') : t('当前邮箱保持不变。你可以切换到新连接的邮箱。'), 'muted'));
      if (!selected) successActions.append(action(t('打开新邮箱'), async () => {
        try { await ctx.select(connected.account.id); dispose(); }
        catch (error) { ctx.notice(errorText(error), true); }
      }, 'primary'));
      successActions.append(action(selected ? t('进入工作台') : t('继续使用当前邮箱'), dispose, selected ? 'primary' : undefined));
      if (fromTask && currentOperation) {
        const append = window.mcode?.miniapp?.message?.append;
        if (typeof append === 'function') successActions.prepend(action(t('回到会话继续'), async () => {
          try {
            await append(tt`邮箱连接已完成，请查询连接操作 ${currentOperation} 并继续本次原请求。`);
            ctx.notice(t('继续任务的内容已交给会话输入框，请确认发送。'));
          } catch { ctx.notice(t('未能追加到会话，请回到原会话发送“继续刚才的邮件任务”。'), true); }
        }, 'primary'));
        node.append(el('p', t('助手若仍在等待，会继续原任务；若会话已结束，请回到会话发送继续。'), 'muted'));
      }
      node.append(successActions);
    });
    node.showModal();
    (address.value ? password : address).focus();
  }
  function unlock(error, resume) {
    if (pending) return;
    const blocked = /^(?:CREDENTIAL_|VAULT_LOCKED)/u.test(error?.code ?? '');
    const clearing = error?.code === 'VAULT_CLEAR_PENDING';
    const node = makeDialog(blocked ? t('需要解锁本机邮箱') : t('本机邮箱暂时无法打开'));
    const status = el('p', errorText(error));
    status.setAttribute('role', 'alert');
    node.append(status, el('p', clearing
      ? t('上次明确确认的清除操作尚未完成。邮箱业务已暂停，只能由你手动重试清除；不会自动创建新邮箱库。')
      : blocked
      ? t('邮箱数据保留在本机。请允许系统凭证访问后重试。不会创建替代密钥或清空已有数据。')
      : t('已有文件和系统凭证都会保留。请检查提示的问题后重试；不会自动清空数据或生成替代密钥。'), 'muted'));
    const buttons = el('div', undefined, 'actions');
    const close = action(t('稍后重试'), dispose);
    const retry = action(t('重试解锁'), async () => {
      retry.disabled = true; close.disabled = true;
      try {
        await api('vault/unlock', { retry: true });
        dispose();
        await resume();
      } catch (next) {
        if (dialog === node) status.textContent = errorText(next);
        else if (vaultErrors.has(next?.code)) unlock(next, resume);
        else ctx.notice(errorText(next), true);
      }
      finally { retry.disabled = false; close.disabled = false; }
    }, 'primary');
    const clear = action(clearing ? t('重试清除') : t('清除本机邮箱数据'), () => ctx.clearLocalData(), 'danger');
    buttons.append(close);
    if (!clearing) buttons.append(retry);
    buttons.append(clear); node.append(buttons);
    node.addEventListener('cancel', (event) => { event.preventDefault(); if (!retry.disabled) dispose(); });
    node.showModal();
  }
  return { open, unlock, dispose, active: () => Boolean(dialog?.open) };
}
