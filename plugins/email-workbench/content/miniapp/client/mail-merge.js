import { t, tt } from './i18n.js';
import { createRichEditor } from './editor-controls.js';
import { renderDraftBody } from './mail-content.js';
import { icon } from './mail-view.js';

import { parseMailingCsv, parseMailingImport, tableMailingRows, validateMailingList, prepareMailingRows, analyzeMailingRows } from './mailing-rules.js';
export { parseMailingCsv, prepareMailingRows, analyzeMailingRows } from './mailing-rules.js';
function invalid(message) { throw new Error(message); }

function expandRichTemplate(html, headers, fields) {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const expand = (value) =>
    value.replace(/\{\{\s*([^{}]+?)\s*\}\}/gu, (_match, key) => {
      const index = headers.indexOf(key.trim());
      if (index < 0 || !fields[index]) invalid(tt`变量 ${key} 未填写`);
      return fields[index];
    });
  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) node.textContent = expand(node.textContent);
  for (const link of doc.querySelectorAll('a[href]')) {
    const href = expand(link.getAttribute('href'));
    const url = new URL(href);
    if (!['https:', 'http:', 'mailto:'].includes(url.protocol) || url.username || url.password)
      invalid(t('模板链接不正确'));
    link.setAttribute('href', href);
  }
  if (/\{\{|\}\}/u.test(doc.body.innerHTML)) invalid(t('图文模板仍有未替换的变量'));
  return doc.body.innerHTML;
}

export function createMailMergeWorkspace(ctx) {
  const { $, el, button, api, notice } = ctx;
  let activeEditor;
  const dispose = () => {
    activeEditor?.destroy();
    activeEditor = undefined;
  };
  async function open() {
    if (!(await ctx.leaveEditor())) return;
    ctx.resetEditor();
    dispose();
    delete $('detail').dataset.batch;
    $('detail').replaceChildren(
      el('h2', t('准备批量邮件')),
      el('p', t('每位收件人分别收到一封邮件。先检查最终内容，再一次确认固定清单。'), 'muted'),
    );
    const form = el('fieldset', undefined, 'editor merge-form');
    form.id = 'merge-form';
    let step = 0;
    let showStep;
    const invalidRecipientField = (input, message) => {
      showStep(0);
      input.setAttribute('aria-invalid', 'true');
      input.setAttribute('aria-describedby', 'notice');
      input.focus();
      input.scrollIntoView?.({ block: 'center', inline: 'nearest' });
      invalid(message);
    };
    const clearFieldError = (event) => {
      if (event.target.getAttribute('aria-invalid') !== 'true') return;
      event.target.removeAttribute('aria-invalid');
      event.target.removeAttribute('aria-describedby');
      notice('');
    };
    form.addEventListener('input', clearFieldError);
    form.addEventListener('change', clearFieldError);
    const field = (labelText, id, tag = 'input') => {
      const label = el('label', labelText);
      const input = el(tag);
      input.id = id;
      label.append(input);
      form.append(label);
      return input;
    };
    const mode = field(t('发送方式'), 'merge-mode', 'select');
    for (const [value, label] of [
      ['personalized', t('逐人个性化邮件')],
      ['shared', t('同内容分别发送')],
    ]) {
      const option = el('option', label);
      option.value = value;
      mode.append(option);
    }
    const title = field(t('任务名称'), 'merge-title');
    title.maxLength = 120;
    const from = field(t('发件邮箱'), 'merge-from', 'select');
    const blank = el('option', t('请选择发件邮箱'));
    blank.value = '';
    from.append(blank);
    for (const account of ctx.accounts()) {
      const option = el('option', account.address);
      option.value = account.id;
      from.append(option);
    }
    from.value = ctx.defaultSender();
    const recipientSection = el('section', undefined, 'recipient-section');
    recipientSection.append(el('h3', t('收件人名单')), el('p', t('一人一行，姓名可选；使用 {{姓名}} 时需补齐。每批最多 100 人。'), 'muted'));
    const recipientTable = el('table', undefined, 'recipient-table');
    recipientTable.id = 'recipient-table';
    const head = el('thead');
    const headings = el('tr');
    for (const title of [t('行'), t('姓名'), t('邮箱'), t('附加字段'), t('操作')]) headings.append(el('th', title));
    head.append(headings);
    const recipientBody = el('tbody');
    recipientTable.append(head, recipientBody);
    let recipientRows = [{ rowId: crypto.randomUUID(), name: '', address: '', fields: {} }];
    const drawRecipients = () => {
      recipientBody.replaceChildren();
      recipientRows.forEach((row, index) => {
        const tr = el('tr'); tr.dataset.rowId = row.rowId;
        tr.append(el('td', `${index + 1}${row.sourceLine ? tt` · 来源 ${row.sourceLine}` : ''}`));
        for (const [key, label] of [['name', t('姓名')], ['address', t('邮箱')]]) {
          const td = el('td'); const input = el('input');
          input.value = row[key] ?? ''; input.setAttribute('aria-label', tt`第 ${index + 1} 行${label}`);
          input.addEventListener('input', () => { row[key] = input.value; if (row[key + 'Column']) row.fields[row[key + 'Column']] = input.value; });
          td.append(input); tr.append(td);
        }
        const extra = el('td'); const details = el('details');
        details.append(el('summary', tt`附加字段（${Object.keys(row.fields).length}）`));
        for (const key of Object.keys(row.fields)) {
          if (['姓名', 'name', 'email', '邮箱', row.nameColumn, row.addressColumn].includes(key)) continue;
          const label = el('label', key); const input = el('textarea'); input.value = row.fields[key];
          input.addEventListener('input', () => { row.fields[key] = input.value; });
          label.append(input); details.append(label);
        }
        extra.append(details); tr.append(extra);
        const actions = el('td'); actions.append(button(t('删除行'), () => { recipientRows = recipientRows.filter((candidate) => candidate !== row); ctx.dirty(true); clearPreview(); drawRecipients(); }));
        tr.append(actions); recipientBody.append(tr);
      });
    };
    recipientSection.append(recipientTable, button(t('添加一行'), () => {
      if (recipientRows.length >= 100) { notice(t('每批最多 100 人。'), true); return; }
      recipientRows.push({ rowId: crypto.randomUUID(), name: '', address: '', fields: {} });
      ctx.dirty(true); clearPreview(); drawRecipients();
    }));
    form.append(recipientSection);
    const source = field(t('粘贴名单（CSV／表格／逐行邮箱）'), 'merge-csv', 'textarea');
    source.maxLength = 512 * 1024;
    source.placeholder = t('email,姓名,时间,附件\n请在这里粘贴你自己的名单');
    const importPanel = el('details', undefined, 'recipient-import');
    importPanel.append(el('summary', t('粘贴或导入名单')), el('p', t('CSV 和表格粘贴首行须为列名；也支持每行一个邮箱。姓名和邮箱用不同列，不按空格猜测。先预览再加入名单。'), 'muted'));
    importPanel.append(source.parentElement);
    form.append(importPanel);
    const picker = field(t('或选择 UTF-8 CSV 文件'), 'merge-file');
    picker.type = 'file';
    picker.accept = '.csv,text/csv';
    const column = field(t('收件地址列'), 'merge-email-column', 'select');
    importPanel.append(picker.parentElement, column.parentElement);
    const importPreview = el('div', undefined, 'recipient-import-preview');
    importPreview.id = 'recipient-import-preview';
    importPanel.append(importPreview);
    const columns = el('p', t('解析名单后可使用 {{列名}} 替换姓名、时间、链接等。'), 'muted');
    form.append(columns);
    let preview;
    let parsedPreviewTable;
    let preparation;
    let table;
    const shared = new Map();
    const individual = new Map();
    const uploads = new Map();
    const previewBox = el('fieldset', undefined, 'merge-preview');
    previewBox.id = 'merge-preview';
    previewBox.hidden = true;
    const resultBox = el('div');
    resultBox.id = 'merge-result';
    const clearPreview = () => {
      if (preparation) return;
      preview = undefined;
      previewBox.hidden = true;
      previewBox.replaceChildren();
      resultBox.replaceChildren();
      if (step === 2) showStep?.(1);
    };
    const attempt = async (action) => {
      try {
        await action();
      } catch (error) {
        notice(error.code ? ctx.error(error.code) : error.message, true);
      }
    };
    const parse = () => {
      const headers = [...new Set(['姓名', 'name', 'email', ...recipientRows.flatMap((row) => Object.keys(row.fields))])];
      table = { headers, rowIds: recipientRows.map((row) => row.rowId), sourceLines: recipientRows.map((row, index) => row.sourceLine ?? index + 1),
        records: recipientRows.map((row) => headers.map((key) => ['姓名', 'name'].includes(key) ? row.name : ['email', '邮箱'].includes(key) ? row.address : row.fields[key] ?? '')) };
      if (!table.records.length || table.records.length > 100)
        invalid(t('每批需要 1 至 100 位收件人。'));
      const previous = 'email';
      column.replaceChildren(
        ...table.headers.map((header) => {
          const option = el('option', header);
          option.value = header;
          return option;
        }),
      );
      column.value = table.headers.includes(previous)
        ? previous
        : (table.headers.find((name) =>
            /^(email|e-mail|邮箱|邮件地址|收件人|收件地址)$/iu.test(name),
          ) ?? table.headers[0]);
      const previousAttachment = attachmentColumn.value;
      attachmentColumn.replaceChildren(noAttachment);
      for (const header of table.headers) {
        const option = el('option', header);
        option.value = header;
        attachmentColumn.append(option);
      }
      attachmentColumn.value = table.headers.includes(previousAttachment)
        ? previousAttachment
        : (table.headers.find((name) => /^(附件|attachments?)$/iu.test(name)) ?? '');
      columns.textContent =
        mode.value === 'shared'
          ? tt`${table.records.length} 个收件地址。所有人使用同一正文和共享附件。`
          : tt`已解析 ${table.records.length} 行。可用变量：${table.headers.map((header) => `{{${header}}}`).join('、')}`;
      return table;
    };
    let importedTable;
    const previewImport = () => {
      importedTable = parseMailingImport(source.value);
      const previous = column.value;
      column.replaceChildren(...importedTable.headers.map((header) => { const option = el('option', header); option.value = header; return option; }));
      column.value = importedTable.headers.includes(previous) ? previous : importedTable.headers.find((name) => /^(email|e-mail|邮箱|邮件地址|收件地址)$/iu.test(name)) ?? importedTable.headers[0];
      drawImport();
    };
    const drawImport = () => {
      if (!importedTable) return;
      const structured = tableMailingRows(importedTable, column.value);
      const nameColumn = importedTable.headers.find((name) => /^(姓名|name)$/iu.test(name));
      const result = validateMailingList(structured, { subject: t('导入预览'), text: t('导入预览') });
      importPreview.replaceChildren(el('h4', tt`导入预览 · ${structured.length} 行`));
      const grid = el('table');
      const headings = el('tr');
      for (const name of [t('来源行'), t('姓名'), t('邮箱'), t('检查结果')]) headings.append(el('th', name));
      grid.append(headings);
      for (const row of structured) {
        const tr = el('tr');
        if (result.errors.some((error) => error.rowId === row.rowId)) tr.dataset.invalid = 'true';
        for (const value of [row.sourceLine, row.fields[nameColumn] ?? '', row.address, result.errors.filter((error) => error.rowId === row.rowId).map((error) => error.message).join('；') || t('可导入')]) tr.append(el('td', String(value)));
        grid.append(tr);
      }
      const accept = button(t('加入名单'), () => {
        const additions = structured.map((row) => ({ ...row, rowId: crypto.randomUUID(), name: row.fields[nameColumn] ?? '', nameColumn, addressColumn: column.value }));
        const initialEmpty = recipientRows.length === 1 && !recipientRows[0].name && !recipientRows[0].address && !Object.keys(recipientRows[0].fields).length;
        const combined = [...(initialEmpty ? [] : recipientRows), ...additions];
        const checked = validateMailingList(combined, { subject: t('导入预览'), text: t('导入预览') });
        if (!checked.valid) { notice(checked.errors.map((error) => tt`第 ${error.line} 行：${error.message}`).join('；'), true); return; }
        recipientRows = combined; drawRecipients(); clearPreview(); ctx.dirty(true);
        notice(tt`已按原顺序加入 ${additions.length} 人，请核对名单与模板。`);
      });
      accept.disabled = !result.valid;
      importPreview.append(grid, accept);
    };
    const parseButton = button(t('解析并预览名单'), () => attempt(async () => previewImport()));
    importPanel.append(parseButton);
    column.addEventListener('change', drawImport);
    picker.addEventListener('change', () => {
      void ctx.run(() => attempt(async () => {
        const file = picker.files[0]; if (!file) return;
        if (file.size > 512 * 1024) invalid(t('名单不能超过 512 KiB。'));
        source.value = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer());
        ctx.dirty(true); previewImport();
      }));
    });
    drawRecipients();
    const template = field(t('复用已有草稿的正文和附件'), 'merge-template', 'select');
    const noTemplate = el('option', t('选择一封草稿作为模板'));
    noTemplate.value = '';
    template.append(noTemplate);
    form.append(
      button(t('查看可复用草稿'), () =>
        attempt(async () => {
          const drafts = await api('drafts/list');
          template.replaceChildren(noTemplate);
          for (const draft of drafts.filter((candidate) => candidate.status === 'draft')) {
            const option = el('option', draft.subject || t('无主题'));
            option.value = draft.id;
            template.append(option);
          }
        }),
      ),
    );
    const subject = field(t('主题模板'), 'merge-subject');
    subject.maxLength = 998;
    const text = field(t('正文模板'), 'merge-text', 'textarea');
    text.maxLength = 200000;
    activeEditor = createRichEditor(text, {
      imageUrl: ctx.imageUrl,
      files: (files, inline) => {
        void ctx.run(() => attempt(() => addFiles(files, shared, inline)));
      },
    });
    const rich = activeEditor;
    const sharedPicker = field(t('共享附件（每人都会收到）'), 'merge-shared-files');
    sharedPicker.type = 'file';
    sharedPicker.multiple = true;
    const sharedList = el('div', undefined, 'merge-attachments');
    form.append(sharedList);
    const attachmentColumn = field(t('逐人附件文件名列（可选）'), 'merge-attachment-column', 'select');
    const noAttachment = el('option', t('不使用逐人附件'));
    noAttachment.value = '';
    attachmentColumn.append(noAttachment);
    const perPicker = field(t('上传名单中引用的逐人文件'), 'merge-personal-files');
    perPicker.type = 'file';
    perPicker.multiple = true;
    const perList = el('div', undefined, 'merge-attachments');
    form.append(perList);
    form.append(
      el(
        'p',
        t('逐人附件按文件名精确匹配，多个文件用分号分隔。文件名必须唯一；无法匹配的行会单独提示，绝不发送其他人的附件。单个文件不超过 10 MiB，每封最多 10 个附件。'),
        'muted',
      ),
    );
    function drawAssets() {
      for (const [pool, list] of [
        [shared, sharedList],
        [individual, perList],
      ]) {
        list.replaceChildren();
        for (const asset of pool.values()) {
          const item = el('div', undefined, 'attachment');
          item.append(el('span', asset.filename));
          if (ctx.canPreview(asset))
            item.append(button(t('预览'), () => ctx.previewAttachment(asset)));
          item.append(
            button(t('移除'), () => {
              pool.delete(asset.filename);
              if (pool === shared) rich.removeImage(asset.id);
              ctx.dirty(true);
              clearPreview();
              drawAssets();
            }),
          );
          list.append(item);
        }
      }
    }
    async function uploadValue(content, metadata, id = crypto.randomUUID()) {
      const sha256 = [...new Uint8Array(await crypto.subtle.digest('SHA-256', content))]
        .map((byte) => byte.toString(16).padStart(2, '0'))
        .join('');
      const fingerprint = JSON.stringify([sha256, metadata]);
      const requestId = uploads.get(fingerprint) ?? id;
      uploads.set(fingerprint, requestId);
      const result = await upload({ requestId, content, sha256, metadata }, api);
      uploads.delete(fingerprint);
      return result;
    }
    async function addFiles(files, pool, inline = false) {
      if (pool === shared && pool.size + files.length > 10) invalid(t('共享附件最多 10 个。'));
      for (const file of files) {
        if (file.size > 10 * 1024 * 1024) invalid(tt`${file.name} 超过 10 MiB。`);
        if (pool.has(file.name)) invalid(tt`文件名 ${file.name} 已存在，请先移除或重命名。`);
        const asset = await uploadValue(new Uint8Array(await file.arrayBuffer()), {
          kind: 'attachment',
          filename: file.name,
          contentType: /^[\w.+-]+\/[\w.+-]+$/u.test(file.type)
            ? file.type
            : 'application/octet-stream',
        });
        pool.set(asset.filename, asset);
        if (inline && /^image\/(png|jpeg|gif|webp)$/u.test(asset.contentType))
          rich.insertImage(asset);
        ctx.dirty(true);
        clearPreview();
        drawAssets();
      }
    }
    for (const [input, pool] of [
      [sharedPicker, shared],
      [perPicker, individual],
    ])
      input.addEventListener('change', () => {
        void ctx.run(() =>
          attempt(async () => {
            await addFiles([...input.files], pool);
            input.value = '';
          }),
        );
      });
    template.addEventListener('change', () => {
      if (!template.value) return;
      void ctx.run(() =>
        attempt(async () => {
          const draft = await api('drafts/read', { id: template.value });
          subject.value = draft.content.subject;
          if (draft.content.html) rich.setHtml(draft.content.html);
          else rich.setText(draft.content.text);
          shared.clear();
          for (const id of draft.content.attachmentIds) {
            const asset = await api('attachments/read', { id, offset: 0 });
            if (shared.has(asset.filename)) invalid(t('模板有重复文件名，请先在草稿中调整。'));
            shared.set(asset.filename, asset);
          }
          ctx.dirty(true);
          clearPreview();
          drawAssets();
          notice(t('已复用模板，请检查变量、附件和发件身份。'));
        }),
      );
    });
    mode.addEventListener('change', () => {
      clearPreview();
      columns.textContent = mode.value === 'shared' ? t('所有人分别收到相同内容；彼此看不到收件名单。') : t('使用 {{列名}} 生成逐人内容。');
    });
    form.addEventListener('input', () => {
      ctx.dirty(true);
      clearPreview();
    });
    form.addEventListener('change', () => {
      ctx.dirty(true);
      clearPreview();
    });
    const makePreview = () =>
      attempt(async () => {
        validateRecipients();
        const parsedTable = parse();
        parsedPreviewTable = parsedTable;
        if (mode.value === 'shared' && /\{\{|\}\}/u.test(subject.value + rich.html()))
          invalid(t('同内容发送不能保留未替换变量，请填写最终内容或切换个性化模式。'));
        const analyzed = analyzeMailingRows(parsedTable, column.value, subject.value, text.value);
        const failures = [...analyzed.errors];
        for (const row of recipientBody.rows) {
          row.querySelector('.recipient-error')?.remove();
          const error = failures.find((failure) => failure.rowId === row.dataset.rowId);
          row.toggleAttribute('data-invalid', !!error);
          if (error) row.cells[2].append(el('small', error.message, 'recipient-error'));
        }
        preview = [];
        for (const row of analyzed.rows) {
          try {
            const assets = [...shared.values()];
            if (mode.value !== 'shared' && attachmentColumn.value) {
              const names = row.fields[parsedTable.headers.indexOf(attachmentColumn.value)]
                .split(/[;；|]/u)
                .map((name) => name.trim())
                .filter(Boolean);
              for (const name of names) {
                const asset = individual.get(name);
                if (!asset) invalid(tt`找不到附件 ${name}`);
                if (!assets.some((other) => other.id === asset.id)) assets.push(asset);
              }
            }
            if (assets.length > 10) invalid(t('共享及逐人附件合计超过 10 个'));
            const html =
              mode.value === 'shared'
                ? rich.html()
                : expandRichTemplate(rich.html(), parsedTable.headers, row.fields);
            preview.push({ ...row, html, assets });
          } catch (error) {
            failures.push({ line: row.line, message: error.message });
          }
        }
        previewBox.replaceChildren(el('legend', tt`逐人检查 · ${preview.length} 封可用邮件`));
        previewBox.hidden = false;
        if (failures.length) {
          const errorList = el('section', undefined, 'inline-error');
          errorList.append(el('strong', tt`${failures.length} 行需处理`));
          for (const error of failures)
            errorList.append(el('p', tt`第 ${error.line} 行：${error.message}`));
          errorList.append(el('p', t('请修正全部错误行后重新预览；输入和名单顺序已保留。')));
          previewBox.append(errorList);
        }
        const overview = el('details', undefined, 'merge-differences');
        overview.append(el('summary', t('查看名单字段与附件差异')));
        const layout = el('div', undefined, 'personal-preview');
        const people = el('aside', undefined, 'preview-people');
        people.setAttribute('aria-label', t('逐人预览收件人'));
        const selectedCount = el('p', tt`已选 ${preview.length} 人`, 'muted');
        people.append(el('h3', t('收件人')), selectedCount);
        const content = el('section', undefined, 'person-content');
        content.setAttribute('aria-label', t('当前收件人的最终邮件'));
        const choices = [], cards = [];
        const choose = (index) => {
          choices.forEach((node, at) => node.setAttribute('aria-current', String(at === index)));
          cards.forEach((node, at) => { node.hidden = at !== index; });
          content.scrollTop = 0;
        };
        const grid = el('table');
        const header = el('tr');
        for (const value of [
          t('行'),
          t('收件人'),
          ...parsedTable.headers.filter((key) => key !== column.value),
          t('最终附件'),
        ])
          header.append(el('th', value));
        grid.append(header);
        preview.forEach((row, index) => {
          const line = el('tr');
          const values = [
            row.line,
            row.address,
            ...row.fields.filter((_field, at) => parsedTable.headers[at] !== column.value),
            row.assets.map((asset) => asset.filename).join('、') || t('无'),
          ];
          for (const value of values) line.append(el('td', String(value)));
          grid.append(line);
          const card = el('article', undefined, 'review-card');
          card.append(el('p', tt`第 ${index + 1} / ${preview.length} 封`, 'eyebrow'), el('h3', row.subject || t('（无主题）')));
          const envelope = el('dl', undefined, 'review-envelope');
          envelope.append(el('dt', t('发件人')), el('dd', ctx.accounts().find(account => account.id === from.value)?.address ?? ''), el('dt', t('收件人')), el('dd', row.address));
          card.append(envelope, renderDraftBody(row, {
            imageUrl: (source) => ctx.imageUrl(source.replace(/^cid:/u, '').replace(/@email-workbench$/u, '')),
          }));
          const person = el('div', undefined, 'preview-person');
          const selected = el('input'); selected.type = 'checkbox'; selected.checked = true;
          selected.dataset.row = String(index); selected.setAttribute('aria-label', tt`包含 ${row.address}`);
          selected.addEventListener('change', () => { selectedCount.textContent = tt`已选 ${people.querySelectorAll('input:checked').length} 人`; });
          const choice = button('', () => choose(index));
          choice.title = row.address;
          choice.setAttribute('aria-label', row.address);
          const nameIndex = parsedTable.headers.findIndex(key => /^(姓名|name)$/iu.test(key));
          choice.append(el('strong', (nameIndex >= 0 && row.fields[nameIndex]) || row.address), el('small', row.address));
          person.append(selected, choice); people.append(person); choices.push(choice);
          for (const asset of row.assets) {
            const attachment = el('div', undefined, 'attachment');
            attachment.append(icon('file'), el('span', asset.filename));
            if (ctx.canPreview(asset)) attachment.append(button(t('预览附件'), () => ctx.previewAttachment(asset)));
            card.append(attachment);
          }
          cards.push(card); content.append(card);
        });
        choose(0);
        layout.append(people, content); previewBox.append(layout);
        overview.append(grid); previewBox.append(overview);
        const saveButton = button(t('保存选中的逐人草稿'), save, 'primary');
        saveButton.disabled = failures.length > 0;
        resultBox.replaceChildren(saveButton);
        showStep(2);
        notice(t('请核对差异表和每封完整预览。当前没有保存或发送。'));
      });
    const previewAction = button(t('预览逐人内容'), makePreview, 'primary');
    form.append(
      previewAction,
      button(t('保存为可复用模板草稿'), () =>
        attempt(async () => {
          if (!from.value || !subject.value.trim()) invalid(t('请填写发件邮箱和主题模板。'));
          const content = {
            accountId: from.value,
            to: [],
            cc: [],
            bcc: [],
            subject: subject.value,
            text: text.value,
            html: rich.html(),
            attachmentIds: [...shared.values()].map((asset) => asset.id),
          };
          await uploadValue(new TextEncoder().encode(JSON.stringify({ content })), {
            kind: 'draft',
          });
          notice(t('已保存无收件人的模板草稿，可在“复用已有草稿”中读取。'));
        }),
      ),
    );
    async function save() {
      try {
        if (!preparation) {
          if (previewBox.querySelector('.inline-error')) invalid(t('请修正全部错误行后重新预览。'));
          const selected = [...previewBox.querySelectorAll('input[data-row]:checked')].map(
            (input) => preview[Number(input.dataset.row)],
          );
          if (!selected.length) invalid(t('请至少选择一位收件人。'));
          const requestId = crypto.randomUUID();
          const payload = {
            requestId,
            title: title.value.trim(),
            accountId: from.value,
            subject: subject.value, text: text.value, html: rich.html(),
            rows: selected.map((row) => ({
              rowId: row.rowId, sourceLine: row.line, address: row.address,
              fields: Object.fromEntries(parsedPreviewTable.headers.map((key, index) => [key, row.fields[index]])),
              attachmentIds: row.assets.map((asset) => asset.id),
            })),
          };
          const content = new TextEncoder().encode(JSON.stringify(payload));
          if (content.length > 2 * 1024 * 1024) invalid(t('整批内容超过 2 MiB，请分为更小批次。'));
          preparation = {
            requestId,
            metadata: { kind: 'mailing' },
            content,
            addresses: selected.map((row) => row.address),
            sha256: [...new Uint8Array(await crypto.subtle.digest('SHA-256', content))]
              .map((byte) => byte.toString(16).padStart(2, '0'))
              .join(''),
          };
        }
        form.disabled = true;
        rich.setEditable(false);
        previewBox.disabled = true;
        back.disabled = true;
        for (const choice of steps.children) choice.disabled = true;
        const receipt = await upload(preparation, api);
        if (!receipt.drafts) throw Object.assign(new Error((receipt.errors ?? []).map((error) => tt`第 ${error.line} 行：${error.message}`).join('；') || t('名单未能保存')), { code: 'INVALID_INPUT' });
        ctx.dirty(false);
        // Per-draft actions belong in the scrollable content, never the footer.
        previewBox.disabled = false;
        previewBox.replaceChildren(
          el('legend', t('已保存的逐人草稿')),
          el('h3', tt`已保存 ${receipt.drafts.length} 封草稿`),
          el('p', t('尚未发送。可逐封编辑，或检查发送清单后统一确认。'), 'muted'),
        );
        const savedList = el('ul', undefined, 'merge-saved-list');
        receipt.drafts.forEach((ref, index) =>
          {
            const row = el('li');
            const edit = button(t('编辑草稿'), () => ctx.openDraft(ref.id));
            edit.setAttribute('aria-label', tt`编辑 ${preparation.addresses[index]}`);
            row.append(el('span', preparation.addresses[index]), edit);
            savedList.append(row);
          },
        );
        previewBox.append(savedList);
        steps.hidden = true;
        back.hidden = true;
        resultBox.replaceChildren(
          button(
            t('检查这批发送清单'),
            async () => {
              const refs = [];
              for (const original of receipt.drafts) {
                const draft = await api('drafts/read', { id: original.id });
                if (draft.status === 'draft') refs.push({ id: draft.id, revision: draft.revision });
              }
              if (refs.length) await ctx.review(refs);
              else notice(t('此批没有可再次审阅的未发送草稿。'));
            },
            'primary',
          ),
        );
        notice(t('草稿已保存。下一步检查固定清单，再在工作台确认。'));
      } catch (error) {
        if (
          preparation &&
          [
            'INVALID_INPUT',
            'DRAFT_INCOMPLETE',
            'ACCOUNT_NOT_FOUND',
            'ATTACHMENT_NOT_FOUND',
            'MESSAGE_TOO_LARGE',
            'STORAGE_FULL',
          ].includes(error.code)
        ) {
          preparation = undefined;
          form.disabled = false;
          rich.setEditable(true);
          previewBox.disabled = false;
          back.disabled = false;
          for (const choice of steps.children) choice.disabled = false;
          notice(t('此批未保存，请修改内容后重试。'), true);
        } else if (preparation) {
          resultBox.replaceChildren(
            el(
              'p',
              t('保存结果尚待核对。输入已固定，使用原请求恢复不会重复创建草稿。'),
              'review-note',
            ),
            button(t('核对并恢复这批草稿'), save),
          );
          notice(t('这批草稿尚未完成核对；没有请求发送。'), true);
        } else notice(error.message, true);
      }
    }
    const recipientsPanel = el('section', undefined, 'merge-step-panel');
    recipientsPanel.id = 'merge-recipients-panel';
    const contentPanel = el('section', undefined, 'merge-step-panel');
    contentPanel.id = 'merge-content-panel';
    const templateLabel = template.parentElement;
    let destination = recipientsPanel;
    for (const node of [...form.children]) {
      if (node === templateLabel) destination = contentPanel;
      if (node !== previewAction) destination.append(node);
    }
    const templateTools = el('details', undefined, 'merge-template-tools');
    const reuseButton = template.parentElement.nextElementSibling;
    templateTools.append(el('summary', t('复用已有草稿')), template.parentElement, reuseButton);
    const composeFields = el('section', undefined, 'merge-compose-fields');
    composeFields.append(subject.parentElement, text.parentElement);
    const individualFiles = el('details', undefined, 'merge-individual-files');
    const attachmentHelp = perList.nextElementSibling;
    individualFiles.append(el('summary', t('逐人附件（可选）')), attachmentColumn.parentElement, perPicker.parentElement, perList, attachmentHelp);
    const assetsPanel = el('aside', undefined, 'merge-assets-panel');
    assetsPanel.append(el('h3', t('附件')), sharedPicker.parentElement, sharedList, individualFiles);
    // The remaining template-save action stays with the content settings.
    assetsPanel.append(...contentPanel.children);
    contentPanel.replaceChildren(templateTools, composeFields, assetsPanel);
    const steps = el('nav', undefined, 'merge-steps');
    steps.setAttribute('aria-label', t('批量邮件准备步骤'));
    const validateRecipients = () => {
      if (!ctx.accounts().some((account) => account.id === from.value)) invalidRecipientField(from, t('请选择已连接的发件邮箱。'));
      if (!title.value.trim()) invalidRecipientField(title, t('请填写任务名称。'));
      const result = validateMailingList(recipientRows, { subject: t('名单检查'), text: t('名单检查') });
      if (!result.valid) {
        const firstErrorRow = [...recipientBody.rows].find((row) => row.dataset.rowId === result.errors[0].rowId);
        const input = firstErrorRow?.cells[2].querySelector('input') ?? title;
        invalidRecipientField(input, result.errors.map((error) => tt`第 ${error.line} 行：${error.message}`).join('；'));
      }
      parse();
    };
    for (const [index, name] of [t('收件人名单'), t('邮件内容'), t('逐人预览')].entries()) {
      const choice = button(`${index + 1} ${name}`, () => attempt(async () => {
        if (preparation) return;
        if (index > 0) validateRecipients();
        if (index === 2) await makePreview();
        else showStep(index);
      }));
      choice.replaceChildren(el('span', String(index + 1), 'step-number'), el('span', name));
      choice.setAttribute('aria-controls', [recipientsPanel.id, contentPanel.id, previewBox.id][index]);
      steps.append(choice);
    }
    const footer = el('div', undefined, 'merge-step-actions');
    const back = button(t('上一步'), () => { if (!preparation) showStep(step - 1); });
    const next = button(t('下一步：邮件内容'), () => attempt(async () => { validateRecipients(); showStep(1); }), 'primary');
    footer.append(back, next, previewAction, resultBox);
    showStep = (index) => {
      step = index;
      notice('');
      form.scrollTop = 0;
      $('detail').dataset.mergeStep = String(index);
      form.hidden = index === 2;
      recipientsPanel.hidden = index !== 0;
      contentPanel.hidden = index !== 1;
      previewBox.hidden = index !== 2 || !preview;
      resultBox.hidden = index !== 2;
      back.hidden = index === 0;
      next.hidden = index !== 0;
      previewAction.hidden = index !== 1;
      [...steps.children].forEach((choice, at) => {
        if (at === index) choice.setAttribute('aria-current', 'step');
        else choice.removeAttribute('aria-current');
      });
      $('detail').closest('.reader').scrollTop = 0;
    };
    form.replaceChildren(recipientsPanel, contentPanel);
    $('detail').append(steps, form, previewBox, footer);
    showStep(0);
    ctx.showDetail();
  }
  return { open, dispose };
}

async function upload(preparation, api) {
  const { requestId: id, content, sha256 } = preparation;
  let state = await api('uploads/begin', {
    id,
    ...(preparation.metadata ?? { kind: 'draft_batch' }),
    bytes: content.length,
    sha256,
  });
  if (state.status === 'committed') return state.result;
  if (state.status === 'cancelled') invalid(t('这批临时上传已取消。'));
  if (!Number.isInteger(state.offset) || state.offset < 0 || state.offset > content.length)
    invalid(t('上传回执格式不正确。'));
  while (state.offset < content.length) {
    const end = Math.min(state.offset + 96 * 1024, content.length);
    let raw = '';
    for (const byte of content.subarray(state.offset, end)) raw += String.fromCharCode(byte);
    state = await api('uploads/append', { id, offset: state.offset, contentBase64: btoa(raw) });
    if (state.offset !== end) invalid(t('上传进度不一致，请核对原请求。'));
  }
  return api('uploads/commit', { id });
}
