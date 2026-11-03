#!/usr/bin/env python3
"""生成短剧剧本DOCX交付文档"""
import zipfile, os, json

OUT = '/workspace/剧本文档.docx'

def p(t, fl=None, sz='21', bd=False, it=False, co='000000', ind=0, be=80, af=60, al='left'):
    if not t and not fl: return '<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr></w:p>'
    rp = '<w:rPr>'
    if bd: rp += '<w:b/><w:bCs/>'
    if it: rp += '<w:i/><w:iCs/>'
    if co != '000000': rp += f'<w:color w:val="{co}"/>'
    if sz != '21': rp += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    rp += '</w:rPr>'
    sd = f'<w:shd w:val="clear" w:fill="{fl}"/>' if fl else ''
    ij = f'<w:ind w:left="{ind}"/>' if ind else ''
    jc = f'<w:jc w:val="{al}"/>' if al != 'left' else ''
    tx = str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    ppr = f'<w:pPr>{sd}<w:spacing w:before="{be}" w:after="{af}"/>{ij}{jc}</w:pPr>'
    return f'<w:p>{ppr}<w:r>{rp}<w:t xml:space="preserve">{tx}</w:t></w:r></w:p>'

X = []

def sh(t): X.append(p(t, fl='1E3A5F', sz='30', bd=True, co='FFFFFF', ind=160, be=200, af=80))
def sb(t): X.append(p(t, sz='22', bd=True, co='1A1A1A', be=140, af=40))
def bd(t): X.append(p(t, sz='22', co='1A1A1A', ind=320, be=30, af=30))
def bk(): X.append(p('', be=40, af=40))
def ed(n='1'): X.append(p(f'第{n}集完', sz='24', bd=True, co='FFFFFF', fl='333333', be=140, af=80, al='center'))
def tr(t): X.append(p(t, sz='20', co='C41E3A', be=100, af=40, al='center', it=True))
def h2(t): X.append(p(t, fl='1E3A5F', sz='22', bd=True, co='FFFFFF', be=140, af=40))
def ac(t): X.append(p(t, sz='21', co='444444', ind=160, be=40, af=20))
def dl(t): X.append(p(t, sz='21', co='1A1A1A', ind=320, be=20, af=20))
def io(t): X.append(p(t, sz='21', co='7B1D6E', ind=320, be=20, af=20, it=True))
def vo(t): X.append(p(t, sz='21', co='003A8C', ind=320, be=20, af=20, bd=True))

def ep(n, sc, tra='', wc=''):
    for hdr, lines in sc:
        h2(hdr)
        for k, t in lines:
            if k == 'a': ac(t)
            elif k == 'd': dl(t)
            elif k == 'i': io(t)
            elif k == 'v': vo(t)
    if tra: tr(tra)
    if wc: X.append(p(f'字数：约{wc}字', sz='19', co='888888', be=20, af=10, al='right'))
    ed(str(n)); bk()

def ch(n, d, qs):
    X.append(p(n, fl='EEF2F7', sz='24', bd=True, co='1E3A5F', ind=160, be=120, af=40))
    X.append(p(d, sz='21', co='1A1A1A', ind=320, be=30, af=20))
    for q in qs: X.append(p(q, sz='21', co='C41E3A', ind=320, be=20, af=20))
    X.append(p('', be=30, af=30))

# ═══════════════════════════════════════
# 在此区域填入剧本内容
# ═══════════════════════════════════════

# ── 基本信息 + 人物小传 ──
sh('一、剧本基本信息')
sb('1. 题材'); bd('都市重生 系统金手指 代际和解 治愈甜')
sb('2. 集数 / 总字数'); bd('____集 x 约____字/集')
sb('3. 世界观'); bd('时间/空间/核心规则描述')
sb('4. 数字体系')
bd('基础金：____万，到账集数：第X集 / 金手指来源：____ / 主角收入：____元/月 / 反派负债：____万')

bk()
sh('二、人物小传')
ch('姓名  角色定位  |  年龄  |  身份',
   '家庭出身/成长背景。\n前世：____\n重生后：____\n【原罪】____\n【性格底色】____\n【核心信条】____',
   ['「台词1」', '「台词2」'])

# ── 分集大纲 ──
sh('三、分集大纲（____集完整版）')
# 格式：X.append(p(f'第X集  标题', sz='23', bd=True, co='C41E3A', be=120, af=30))
#       X.append(p(f"【事件】{事件}", sz='21', co='555555', ind=320, be=10, af=20))
#       for lb, co, col in [('【开头发吸引】','1A6B3A'),('【爆点】','C41E3A'),...]:

bk()
sh('四、正文脚本（____集完整版）')
X.append(p('剧本格式：▲动作 / （OS）内心独白 / （VO）系统音 / 【】场景标注 / 角色名：台词', sz='20', co='888888', be=60, af=80))

# ═══════════════════════════════════════
# 剧集正文从这里开始
# ═══════════════════════════════════════
# ep(集数, [
#     ('【集-N 场景  时间  事件】', [
#         ('a', '▲动作描写。'),
#         ('d', '角色名：台词内容。'),
#         ('i', '（OS）内心独白内容。'),
#         ('v', '（VO）系统/旁白内容。'),
#     ]),
# ], '【下集预告】……', 约____字)

# ═══════════════════════════════════════
# 构建DOCX
# ═══════════════════════════════════════
styles = '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault/><w:pPrDefault/></w:docDefaults><w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/></w:style></w:styles>'
rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
ct = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
doc_rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
doc_props = '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Version>16.00</Version></Properties>'
sect = '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
body = ''.join(X) + f'<w:p><w:pPr>{sect}</w:pPr></w:p>'
doc_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
           f'<w:body>{body}</w:body></w:document>')
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct)
    z.writestr('_rels/.rels', doc_rels)
    z.writestr('word/document.xml', doc_xml)
    z.writestr('word/styles.xml', styles)
    z.writestr('word/_rels/document.xml.rels', rels)
    z.writestr('docProps/app.xml', doc_props)
print(f'OK: {OUT} ({os.path.getsize(OUT)} bytes, {len(X)} paragraphs)')
