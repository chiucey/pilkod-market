// 根据明确的发布区域设置默认语言，不覆盖用户保存的 cc.locale 或下载区域。
import {readFile, writeFile, unlink, mkdir, cp, realpath} from 'node:fs/promises';
import {resolve, join} from 'node:path';
const [directory, region] = process.argv.slice(2);
if (!directory || !['cn','us'].includes(region)) throw new Error('Usage: node package-region.mjs <package-directory> <cn|us>');
const root=resolve(directory);
const writeJSON=(p,v)=>writeFile(join(root,p),JSON.stringify(v,null,2)+'\n');
const readJSON=async p=>JSON.parse(await readFile(join(root,p),'utf8'));
const plugin=await readJSON('.minimax-plugin/plugin.json');plugin.name='minimax-video';plugin.version='1.1.6';plugin.displayName='MiniMax Video';plugin.skills=['skills/code-video/SKILL.md','skills/lucid/SKILL.md'];
if(region==='us') {
 plugin.description='Local video editing with a multitrack timeline, captions, an AI editing assistant, and MP4/MP3 export. Adapted from OpenChatCut (AGPL-3.0-or-later).';
 plugin.exampleQueries=['Open MiniMax Video and create a video project','Review my current video and propose edits for me to preview'];
 const mcp=await readJSON('servers.mcp.json');mcp.mcpServers.openchatcut.description='Read video projects, prepare editing drafts, edit timelines, and submit changes for review.';await writeJSON('servers.mcp.json',mcp);
 const translations=JSON.parse(await readFile(new URL('./backend-en.json',import.meta.url),'utf8'));
 for(const file of ['setup-server.mjs','install-dependencies.mjs','lazy-resources.mjs']) {
  const path=join(root,'miniapp/node',file);let text=await readFile(path,'utf8');
  for(const [zh,en] of Object.entries(translations).sort((a,b)=>b[0].length-a[0].length)) text=text.replaceAll(zh,en.replaceAll("'", "\\'"));
  await writeFile(path,text);
 }
}
await writeJSON('.minimax-plugin/plugin.json',plugin);
for(const file of ['index.html','setup.html']) {
 const path=join(root,'miniapp/client',file);let html=await readFile(path,'utf8');
 html=html.replace(/<html lang="[^"]*"/,`<html lang="${region==='cn'?'zh-CN':'en'}"`);await writeFile(path,html);
}
const metadata=await readJSON('miniapp/node/upstream.json');metadata.downloadRegion=region==='cn'?'cn':'global';metadata.buildId=`minimax-video-1.1.6-${region}`;await writeJSON('miniapp/node/upstream.json',metadata);
console.log(`Prepared ${region} MiniMax Video ${plugin.version}`);

// 上游遗留的空扩展索引未被当前代码引用；扩展发现已使用 registry API。
for (const path of ['miniapp/client/plugins/index.json', 'miniapp/node/remotion-bundle/plugins/index.json', 'miniapp/node/remotion-bundle/public/plugins/index.json']) {
 const text=await readFile(join(root,path),'utf8').catch(error=>{if(error.code==='ENOENT')return null;throw error});
 if(text!==null) { if(text.trim()!=='[]')throw new Error('Unexpected legacy plugin index contents'); await unlink(join(root,path)); }
}

await mkdir(join(root,'skills/code-video'),{recursive:true});
await writeFile(join(root,'skills/code-video/SKILL.md'),await readFile(new URL('../skills/code-video/SKILL.md',import.meta.url),'utf8'));

const lucidSource=new URL('../skills/lucid/',import.meta.url);
if(await realpath(lucidSource)!==await realpath(join(root,'skills/lucid')).catch(()=>null)) await cp(lucidSource,join(root,'skills/lucid'),{recursive:true});
