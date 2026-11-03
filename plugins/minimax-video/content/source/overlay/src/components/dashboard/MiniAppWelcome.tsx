import { t, useT } from '../../i18n/locale';
import { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import '../ui/theme.css';

export function MiniAppWelcome({ onNew, onSettings, onSampleCreated }: { onNew: () => void; onSettings: () => void; onSampleCreated?: (id: string) => Promise<void> }) {
  useT();
  const [expanded, setExpanded] = useState(false);
  const [sampleBusy, setSampleBusy] = useState(false);
  const [sampleError, setSampleError] = useState('');
  async function openSample() {
    if (sampleBusy) return;
    setSampleBusy(true); setSampleError('');
    try { const project = await (await import('../../app/miniAppSample')).createMiniAppSample(); await onSampleCreated?.(project.id); }
    catch (error) { setSampleError(error instanceof Error ? error.message : t("示例创建失败，请重试")); }
    finally { setSampleBusy(false); }
  }
  return <Card className="cc-shadcn miniapp-welcome" aria-labelledby="miniapp-welcome">
    <CardHeader>
      <CardTitle id="miniapp-welcome">{t("把你的想法，剪成一段好视频")}</CardTitle>
      <CardDescription>{t("导入素材，让助手帮你整理和剪辑。每一步都能预览，由你决定是否采用。")}</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="miniapp-welcome__actions">
        <Button onClick={onNew}>{t("新建视频工程")}</Button>
        <Button variant="outline" disabled={sampleBusy} onClick={() => void openSample()}>{sampleBusy ? t("正在准备示例…") : t("打开示例")}</Button>
        <Button variant="outline" onClick={() => setExpanded(!expanded)} aria-expanded={expanded} aria-controls="miniapp-guide">{t("快速上手")}</Button>
        <Button variant="ghost" onClick={onSettings}>{t("设置与关于")}</Button>
      </div>
      {sampleError && <p role="alert">{sampleError}</p>}
      {expanded && <div id="miniapp-guide" className="miniapp-welcome__guide">
        <ol>
          <li>{t("新建工程，导入视频、图片或音频。")}</li>
          <li>{t("把素材拖入时间线，或者告诉助手你想怎么剪。")}</li>
          <li>{t("预览修改，确认后导出视频。工程保存在本机，随时继续。")}</li>
        </ol>
        <p>{t("助手使用 MiniMax Code 的模型和工具，无需在这里重复配置。")}</p>
      </div>}
    </CardContent>
  </Card>;
}
