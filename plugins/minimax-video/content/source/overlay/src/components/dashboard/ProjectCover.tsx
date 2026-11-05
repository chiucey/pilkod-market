import { t, useT } from '../../i18n/locale';
import { useState } from 'react';
import { Icon } from '../icons';
import './projectCover.css';

export function ProjectCover({ src, name }: { src?: string; name: string }) {
  useT();
  const [failedSrc, setFailedSrc] = useState<string>();
  return <span className="cc-project-cover">
    {src && src !== failedSrc
      ? <img src={src} alt={`${name} · ${t("工程封面")}`} draggable={false} loading="lazy" decoding="async" onError={() => setFailedSrc(src)} />
      : <span className="cc-project-cover__placeholder"><Icon name="video" size={30} /><strong>{name}</strong><small>{src ? t("封面暂不可用 · 可打开工程查看") : t("尚无封面 · 从导入素材开始")}</small></span>}
    <span className="cc-project-cover__open"><Icon name="play" size={16} />{t("打开工程")}</span>
  </span>;
}
