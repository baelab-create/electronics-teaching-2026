import io,sys,re,os,json,html as H
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import pymupdf

ROOT=r'C:\Users\user\Downloads\electronics-teaching-2026'
PDF=r'C:\Users\user\Downloads\electronics-study\pdfs\chapter2.pdf'
BOOK_OFF=54  # printed page = pdf index + 54 (p1 -> 55)
TITLE='Chapter 2 · Diode Applications'

doc=pymupdf.open(PDF)
N=doc.page_count
os.makedirs(os.path.join(ROOT,'assets','ch2'),exist_ok=True)

# ---------- 1) SVG pages ----------
total=0
for i in range(N):
    svg=doc[i].get_svg_image(matrix=pymupdf.Identity)
    path=os.path.join(ROOT,'assets','ch2','page_%03d.svg'%(i+1))
    with open(path,'w',encoding='utf-8') as f: f.write(svg)
    total+=len(svg)
print('svg total MB: %.1f'%(total/1e6))

# ---------- 2) text layers + TEXTS ----------
def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
layers={}; TEXTS={}
span_count=0
for i in range(N):
    page=doc[i]
    TEXTS[str(i+1)]=page.get_text()
    d=page.get_text('dict')
    out=[]
    for blk in d['blocks']:
        if blk.get('type')!=0: continue
        for line in blk['lines']:
            dx,dy=line.get('dir',(1,0))
            if abs(dy)>0.05: continue  # skip rotated text
            spans=line['spans']
            if not spans: continue
            txt=''; prev=None
            for sp in spans:
                t=sp['text']
                if prev is not None:
                    gap=sp['bbox'][0]-prev['bbox'][2]
                    if gap>0.18*sp['size'] and not t.startswith(' ') and not txt.endswith(' '):
                        txt+=' '
                txt+=t; prev=sp
            if not txt.strip(): continue
            x0,y0,x1,y1=line['bbox']
            F=max(sp['size'] for sp in spans)
            base=spans[0]['origin'][1]
            top=base-0.782*F
            w=x1-x0
            if w<2: continue
            out.append('<span class="text-line" data-w="%.2f" style="left:%.3fpx;top:%.3fpx;font-size:%.3fpx;height:%.3fpx">%s</span>'
                       %(w,x0,top,F,F,esc(txt)))
            span_count+=1
    layers[i+1]=''.join(out)
print('text spans:',span_count)

# ---------- 3) sections: pages verified against 12pt heading spans + uppercase heading lines ----------
SECS=[{'num':n,'title':t,'page':p} for n,t,p in [
 ('2.1','Introduction',1),
 ('2.2','Load-Line Analysis',2),
 ('2.3','Series Diode Configurations',7),
 ('2.4','Parallel and Series–Parallel Configurations',13),
 ('2.5','AND/OR Gates',16),
 ('2.6','Sinusoidal Inputs; Half-Wave Rectification',18),
 ('2.7','Full-Wave Rectification',21),
 ('2.8','Clippers',24),
 ('2.9','Clampers',31),
 ('2.10','Networks with a DC and AC Source',34),
 ('2.11','Zener Diodes',37),
 ('2.12','Voltage-Multiplier Circuits',44),
 ('2.13','Practical Applications',47),
 ('2.14','Summary',57),
 ('2.15','Computer Analysis',58),
]]
print('sections:')
for s in SECS: print(' ',s['num'],s['page'],s['title'])

# ---------- 4) assemble chapter2.html ----------
src=open(os.path.join(ROOT,'chapter1.html'),encoding='utf-8',newline='').read()
h=src

# 4a. viewer data header
a=h.index('const W=')
b=h.index(';let scale=1,cur=22')
def js(o): return json.dumps(o,ensure_ascii=True).replace('<','\\u003c')
header=('const W=603.500,H=774.140,START=1,END=%d,SECS=%s,TEXTS=%s'%(N,js(SECS),js(TEXTS)))
h=h[:a]+header+';let scale=1,cur=1'+h[b+len(';let scale=1,cur=22'):]

# 4b. book-page offset in viewer logic
assert h.count('p-21')==1 and h.count('cur-21')==1
h=h.replace('${p-21}','${p+%d}'%BOOK_OFF).replace('${cur-21}','${cur+%d}'%BOOK_OFF)

# 4c. TOC
ta=h.index('<nav id="toc">')+len('<nav id="toc">'); tb=h.index('</nav>',ta)
toc=''.join('<a href="#pdf-%d" data-start="%d"><span class="n">%s</span><span>%s</span></a>'
            %(s['page'],s['page'],s['num'],esc(s['title'])) for s in SECS)
h=h[:ta]+toc+h[tb:]

# 4d. pages
pa=h.index('<div class="pages">')+len('<div class="pages">')
pb=h.index('</main>',pa)
shells=[]
for i in range(1,N+1):
    bp=i+BOOK_OFF
    shells.append('<div class="page-shell" id="pdf-%d" data-pdf-page="%d" data-book-page="%d">'
        '<div class="page-inner"><img class="vector-img" loading="lazy" decoding="async" src="assets/ch2/page_%03d.svg" alt="Original PDF page %d">'
        '<div class="focus-layer" aria-hidden="true"></div>'
        '<div class="text-layer">%s</div></div>'
        '<div class="page-caption"><span>textbook p. %d</span><span>PDF p. %d</span></div></div>'
        %(i,i,bp,i,i,layers[i],bp,i))
h=h[:pa]+''.join(shells)+'</div>'+h[pb:]

# 4e. chapter identity strings
h=h.replace('Chapter 1 · Semiconductor Diodes',TITLE)
h=h.replace('chapter1:','chapter2:')
h=h.replace('Chapter1_Teaching_Backup_','Chapter2_Teaching_Backup_')
h=h.replace('<h1>Chapter 1<br>Semiconductor Diodes</h1>','<h1>Chapter 2<br>Diode Applications</h1>')

open(os.path.join(ROOT,'chapter2.html'),'w',encoding='utf-8',newline='').write(h)
print('chapter2.html bytes:',len(h.encode('utf-8')))
print('remaining chapter1 refs:',h.count('chapter1'),'| Chapter 1 refs:',len(re.findall(r'Chapter 1\b',h)))
print('page_0 chapter1-asset refs:',h.count('assets/page_0'))
