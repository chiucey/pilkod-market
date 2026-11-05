import { t, useT } from './i18n/locale';
import './index.css';
import './miniappTypography.css';
import './components/ui/theme.css';
import './setup.css';
import {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Button} from './components/ui/button';
import {initSkins} from './skins';
document.documentElement.classList.add('miniapp-host');
initSkins();
type Status = {state:string; message:string; platform:string; region?:string; token:string};
function Setup() {
  useT();
  const [status,setStatus]=useState<Status>();
  const [error,setError]=useState('');
  useEffect(()=>{
    let stopped=false;
    const poll=async()=>{try {
      const response=await fetch('/__setup/status',{cache:'no-store'});
      if(response.status===404) {location.reload();return;}
      if(!response.ok) throw Error(t("暂时无法连接，请稍后重试"));
      const value=await response.json() as Status;
      if(!stopped) {setStatus(value);setError(''); if(value.state==='ready')location.reload();}
    } catch(e) {if(!stopped)setError(e instanceof Error?e.message:t("连接失败"));}};
    void poll(); const timer=setInterval(()=>void poll(),1500);
    return ()=>{stopped=true;clearInterval(timer);};
  },[]);
  const install=async(region:string)=>{
    if(!status)return;
    try {const response=await fetch('/__setup/install',{method:'POST',headers:{'Content-Type':'application/json','X-Setup-Token':status.token},body:JSON.stringify({region})});
      if(!response.ok)throw Error(t("无法开始准备，请重试"));
      setStatus({...status,state:'installing',message:t("正在准备下载…")});
    } catch(e) {setError(e instanceof Error?e.message:t("连接失败"));}
  };
  const busy=!status || status.state==='installing' || status.state==='checking';
  return <main className="miniapp-setup"><section className="cc-shadcn miniapp-setup__card">
    <h1>MiniMax Video</h1><h2>{t("准备视频编辑环境")}</h2>
    <p>{t("首次使用需要下载视频处理组件。完成后保存在这台电脑，后续打开无需重复下载。")}</p>
    <p>{t("系统：")}{status?.platform ?? t("正在识别")}</p>
    <p role="status" aria-live="polite">{status?.message ?? t("正在检查网络并准备下载…")}</p>
    {status?.state==='error' && <Button onClick={()=>void install('auto')}>{t("重新尝试")}</Button>}
    <details>
      <summary>{t("下载遇到问题？")}</summary>
      <p>{t("已自动选择可用下载源。必要时可手动切换，已保存的工程不会受影响。")}</p>
      <div className="miniapp-setup__choices">
        <Button variant="outline" disabled={busy} onClick={()=>void install('cn')}>{t("中国大陆下载源")}</Button>
        <Button variant="outline" disabled={busy} onClick={()=>void install('global')}>{t("海外下载源")}</Button>
      </div>
    </details>
    {error && <p role="alert">{error}</p>}
  </section></main>;
}
void import('./i18n/locale').then(async ({ensureLocaleDict, getLocale}) => { await ensureLocaleDict(getLocale()); createRoot(document.getElementById('root')!).render(<Setup/>); });
