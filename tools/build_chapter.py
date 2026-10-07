# -*- coding: utf-8 -*-
"""Generate chapterN.html for the Teaching Edition from the student-site PDF.

chapter1.html is the template: the viewer data header (W/H/START/END/SECS/TEXTS),
TOC, page shells + text layers are replaced, every 'chapter1:' key prefix becomes
'chapterN:', and lecture-scope gray marks (from MARKS phrase configs, derived from
the professor's class-notes marking criteria) are baked into each page's focus-layer.

Run from the repo root:  python tools/build_chapter.py 3 4 5
"""
import io,sys,re,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import pymupdf

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR=r'C:\Users\user\Downloads\electronics-study\pdfs'
W,H=603.5,774.14

def norm(t):
    t=t.lower()
    t=re.sub(r'[^a-z0-9.%°]+',' ',t)
    return ' '.join(t.split())

# ---------------- per-chapter config ----------------
# SECS pages verified against 12pt heading spans; titles canonical (Boylestad 11e).
CFG={
2:dict(title='Chapter 2 · Diode Applications',book_off=54,
 secs=[('2.1','Introduction',1),('2.2','Load-Line Analysis',2),('2.3','Series Diode Configurations',7),
 ('2.4','Parallel and Series\u2013Parallel Configurations',13),('2.5','AND/OR Gates',16),
 ('2.6','Sinusoidal Inputs; Half-Wave Rectification',18),('2.7','Full-Wave Rectification',21),
 ('2.8','Clippers',24),('2.9','Clampers',31),('2.10','Networks with a DC and AC Source',34),
 ('2.11','Zener Diodes',37),('2.12','Voltage-Multiplier Circuits',44),('2.13','Practical Applications',47),
 ('2.14','Summary',57),('2.15','Computer Analysis',58)],
 marks=[
  (1,1,['load-line analysis','equivalent circuits','rectification','clipper','clamper']),
  (2,6,['load line','q-point','point of operation','intersection','characteristics of the','network equation','0.78','18.5','9.22']),
  (7,12,['0.7 v','kirchhoff','7.3','3.32','series']),
  (13,15,['parallel','28.18','14.09','0.7 v']),
  (18,20,['half-wave','rectification','dc level','average value','0.318','vdc']),
  (21,23,['full-wave','bridge','0.636','two diodes','twice']),
 ],
 figs=(1,23,['2.1','2.2','2.3','2.28','2.29','2.44','2.45','2.46','2.47','2.48','2.53','2.54','2.55','2.56','2.57','2.58'])),
3:dict(title='Chapter 3 · Bipolar Junction Transistors',book_off=128,
 secs=[('3.1','Introduction',1),('3.2','Transistor Construction',2),('3.3','Transistor Operation',2),
 ('3.4','Common-Base Configuration',3),('3.5','Common-Emitter Configuration',8),
 ('3.6','Common-Collector Configuration',15),('3.7','Limits of Operation',16),
 ('3.8','Transistor Specification Sheet',17),('3.9','Transistor Testing',21)],
 marks=[
  (1,1,['bell','1947','transistor','vacuum','shockley','bardeen','brattain','point-contact','miniaturization']),
  (2,2,['npn','pnp','emitter','base','collector','doped','sandwiched','three']),
  (2,3,['forward-biased','reverse-biased','majority','minority','depletion']),
  (3,7,['common-base','alpha','input impedance','output impedance','current gain','voltage gain','amplif']),
  (8,14,['common-emitter','beta','current gain','amplif','switch']),
  (15,16,['common-collector','emitter-follower','impedance-matching','impedance matching','buffer','input impedance','output impedance']),
 ],
 figs=(1,16,['3.3','3.4','3.5','3.6','3.7','3.8','3.12','3.13','3.20'])),
4:dict(title='Chapter 4 · DC Biasing\u2014BJTs',book_off=159,
 secs=[('4.1','Introduction',1),('4.2','Operating Point',2),('4.3','Fixed-Bias Configuration',4),
 ('4.4','Emitter-Bias Configuration',10),('4.5','Voltage-Divider Bias Configuration',16),
 ('4.6','Collector Feedback Configuration',22),('4.7','Emitter-Follower Configuration',27),
 ('4.8','Common-Base Configuration',28),('4.9','Miscellaneous Bias Configurations',30),
 ('4.15','pnp Transistors',51)],
 marks=[
  (1,1,['0.7 v','amplif','dc supply','energy','conservation']),
  (2,3,['biasing','operating point','quiescent','q-point','active region','cutoff','saturation','temperature']),
  (4,9,['fixed-bias','open circuit','capacitive','coupling','base\u2013emitter loop','collector\u2013emitter loop','load line','saturation','vce  vcc','ic sat']),
  (10,15,['emitter-bias','stability','emitter resistor','improved','less sensitive','robust']),
  (16,21,['voltage-divider','th\u00e9venin','thevenin','rth','eth','exact','approximate','stable']),
  (33,34,['summary','table 4.1']),
 ],
 figs=(1,21,['4.1','4.4','4.5','4.6','4.10','4.12','4.13','4.14','4.15','4.17','4.19','4.22','4.24','4.28','4.29','4.30','4.31','4.32'])),
5:dict(title='Chapter 5 · BJT AC Analysis',book_off=252,
 secs=[('5.1','Introduction',1),('5.2','Amplification in the AC Domain',1),('5.3','BJT Transistor Modeling',2),
 ('5.4','The r\u2091 Transistor Model',5),('5.5','Common-Emitter Fixed-Bias Configuration',10),
 ('5.6','Voltage-Divider Bias',13),('5.7','CE Emitter-Bias Configuration',15),
 ('5.8','Emitter-Follower Configuration',21),('5.9','Common-Base Configuration',25)],
 marks=[
  (1,1,['small-signal','amplification','superposition']),
  (2,4,['equivalent circuit','model','dc ground','coupling','bypass','short circuit','small-signal','input impedance','output impedance','voltage gain']),
  (5,9,['26 mv','dependent','controlled source','diode','resistance']),
  (10,12,['fixed-bias','phase shift','180','zi','zo','av']),
  (13,14,['voltage-divider']),
  (15,20,['unbypassed','zb','stability','without the']),
  (21,24,['emitter-follower','close to 1','in phase','buffer','impedance matching']),
  (25,26,['common-base','no phase','low input impedance','high output impedance']),
  (40,41,['summary','table 5.1']),
 ],
 figs=(1,26,['5.3','5.4','5.5','5.6','5.7','5.8','5.10','5.11','5.16','5.20','5.21','5.22','5.23','5.24','5.26','5.27','5.29','5.30','5.36','5.37','5.42','5.43'])),
}

def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def js(o): return json.dumps(o,ensure_ascii=True).replace('<','\\u003c')

def build(ch):
    cfg=CFG[ch]
    doc=pymupdf.open(os.path.join(PDF_DIR,'chapter%d.pdf'%ch))
    N=doc.page_count
    outdir=os.path.join(ROOT,'assets','ch%d'%ch)
    os.makedirs(outdir,exist_ok=True)
    total=0
    for i in range(N):
        svg=doc[i].get_svg_image(matrix=pymupdf.Identity)
        with open(os.path.join(outdir,'page_%03d.svg'%(i+1)),'w',encoding='utf-8') as f: f.write(svg)
        total+=len(svg)
    # text layers + TEXTS + line records for marking
    layers={};TEXTS={};recs={}
    nspan=0
    for i in range(N):
        page=doc[i]
        TEXTS[str(i+1)]=page.get_text()
        d=page.get_text('dict')
        out=[];rr=[]
        for blk in d['blocks']:
            if blk.get('type')!=0: continue
            for line in blk['lines']:
                dx,dy=line.get('dir',(1,0))
                if abs(dy)>0.05: continue
                spans=line['spans']
                if not spans: continue
                txt='';prev=None
                for sp in spans:
                    t=sp['text']
                    if prev is not None:
                        gap=sp['bbox'][0]-prev['bbox'][2]
                        if gap>0.18*sp['size'] and not t.startswith(' ') and not txt.endswith(' '):
                            txt+=' '
                    txt+=t;prev=sp
                if not txt.strip(): continue
                x0,y0,x1,y1=line['bbox']
                F=max(sp['size'] for sp in spans)
                top=spans[0]['origin'][1]-0.782*F
                w=x1-x0
                if w<2: continue
                out.append('<span class="text-line" data-w="%.2f" style="left:%.3fpx;top:%.3fpx;font-size:%.3fpx;height:%.3fpx">%s</span>'%(w,x0,top,F,F,esc(txt)))
                rr.append((x0,top,w,F,norm(txt)))
                nspan+=1
        layers[i+1]=''.join(out);recs[i+1]=rr
    # lecture-scope marks from phrase configs
    marks={i:[] for i in range(1,N+1)}
    def add(p,x0,top,w,F):
        h=F/H
        marks[p].append({'x':x0/W,'y':top/H-h*0.14,'w':w/W,'h':h*1.28})
    stats={}
    for p0,p1,phrases in cfg['marks']:
        for p in range(p0,min(p1,N)+1):
            for x0,top,w,F,nt in recs[p]:
                if any(ph in nt for ph in phrases):
                    add(p,x0,top,w,F);stats[p]=stats.get(p,0)+1
    f0,f1,figs=cfg['figs']
    figres=[re.compile(r'fig\. ?'+re.escape(f)+r'(?![0-9])') for f in figs]
    for p in range(f0,min(f1,N)+1):
        for x0,top,w,F,nt in recs[p]:
            if any(rx.search(nt) for rx in figres):
                add(p,x0,top,w,F);stats[p]=stats.get(p,0)+1
    # section heading lines of covered sections
    covered=set()
    for p0,p1,_ in cfg['marks']: covered.update(range(p0,p1+1))
    for num,_,pg in cfg['secs']:
        if pg in covered:
            for x0,top,w,F,nt in recs[pg]:
                if nt.startswith(num+' ') or nt==num:
                    add(pg,x0,top,w,F)
    # dedupe overlapping marks on the same line
    for p in marks:
        seen=set();uniq=[]
        for m in marks[p]:
            k=(round(m['y'],4),round(m['x'],3))
            if k in seen: continue
            seen.add(k);uniq.append(m)
        marks[p]=uniq
    total_marks=sum(len(v) for v in marks.values())
    # assemble from template
    src=open(os.path.join(ROOT,'chapter1.html'),encoding='utf-8',newline='').read()
    h=src
    a=h.index('const W=');b=h.index(';let scale=1,cur=22')
    SECS=[{'num':n,'title':t,'page':p} for n,t,p in cfg['secs']]
    h=h[:a]+('const W=603.500,H=774.140,START=1,END=%d,SECS=%s,TEXTS=%s'%(N,js(SECS),js(TEXTS)))+';let scale=1,cur=1'+h[b+len(';let scale=1,cur=22'):]
    assert h.count('${p-21}')==1 and h.count('${cur-21}')==1
    h=h.replace('${p-21}','${p+%d}'%cfg['book_off']).replace('${cur-21}','${cur+%d}'%cfg['book_off'])
    ta=h.index('<nav id="toc">')+len('<nav id="toc">');tb=h.index('</nav>',ta)
    toc=''.join('<a href="#pdf-%d" data-start="%d"><span class="n">%s</span><span>%s</span></a>'%(s['page'],s['page'],s['num'],esc(s['title'])) for s in SECS)
    h=h[:ta]+toc+h[tb:]
    pa=h.index('<div class="pages">')+len('<div class="pages">');pb=h.index('</main>',pa)
    shells=[]
    for i in range(1,N+1):
        bp=i+cfg['book_off']
        mi=''.join('<i style="left:%.4f%%;top:%.4f%%;width:%.4f%%;height:%.4f%%"></i>'%(m['x']*100,m['y']*100,m['w']*100,m['h']*100) for m in marks[i])
        shells.append('<div class="page-shell" id="pdf-%d" data-pdf-page="%d" data-book-page="%d">'
            '<div class="page-inner"><img class="vector-img" loading="lazy" decoding="async" src="assets/ch%d/page_%03d.svg" alt="Original PDF page %d">'
            '<div class="focus-layer" aria-hidden="true">%s</div>'
            '<div class="text-layer">%s</div></div>'
            '<div class="page-caption"><span>textbook p. %d</span><span>PDF p. %d</span></div></div>'
            %(i,i,bp,ch,i,i,mi,layers[i],bp,i))
    h=h[:pa]+''.join(shells)+'</div>'+h[pb:]
    h=h.replace('Chapter 1 · Semiconductor Diodes',cfg['title'])
    h=h.replace('chapter1:','chapter%d:'%ch)
    h=h.replace('Chapter1_Teaching_Backup_','Chapter%d_Teaching_Backup_'%ch)
    h=h.replace('<h1>Chapter 1<br>Semiconductor Diodes</h1>','<h1>Chapter %d<br>%s</h1>'%(ch,esc(cfg['title'].split(' · ')[1])))
    open(os.path.join(ROOT,'chapter%d.html'%ch),'w',encoding='utf-8',newline='').write(h)
    print('ch%d: pages %d, svg %.1fMB, spans %d, marks %d (pages with marks: %d), html %.2fMB'%(
        ch,N,total/1e6,nspan,total_marks,sum(1 for v in marks.values() if v),len(h.encode('utf-8'))/1e6))
    print('  leftover chapter1 refs:',h.count('chapter1'),'Chapter 1:',len(re.findall(r'Chapter 1\b',h)))
    return total_marks

if __name__=='__main__':
    for arg in sys.argv[1:]:
        build(int(arg))
