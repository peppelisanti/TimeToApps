import sys, os, math, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,'..','..','..'))     # TimeToApps
SOC=os.path.abspath(os.path.join(HERE,'..'))                 # social/2026-11-09
W,H,FPS=1080,1920,30
GREEN=(166,224,138); WHITE=(255,255,255)
FB=ROOT+'/assets/fonts/OpenSans-SemiBold.ttf'; FR=ROOT+'/assets/fonts/OpenSans-Regular.ttf'
def F(sz,b=True): return ImageFont.truetype(FB if b else FR,sz)
BG={'payday':(15,58,46),'sub':(13,46,63),'restructure':(36,28,66),'event':(27,42,74)}
NAME={'payday':'Time to Payday','sub':'Time to Subscription','restructure':'Time to Renovate','event':'Time to Event'}
def eo(t): t=max(0,min(1,t)); return 1-(1-t)**3
def eio(t): t=max(0,min(1,t)); return 4*t**3 if t<.5 else 1-(-2*t+2)**3/2
def eback(t,s=1.7): t=max(0,min(1,t)); t-=1; return t*t*((s+1)*t+s)+1
def rmask(size,r):
    s=4; m=Image.new('L',(size[0]*s,size[1]*s),0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]*s-1,size[1]*s-1],r*s,fill=255)
    return m.resize(size,Image.LANCZOS)
def rounded(im,r):
    im=im.copy(); im.putalpha(rmask(im.size,r)); return im
def bgimg(col):
    im=Image.new('RGBA',(W,H),col+(255,)); d=ImageDraw.Draw(im)
    lt=tuple(min(255,int(c*1.35)+8) for c in col)
    for y in range(H):
        a=y/H; d.line([(0,y),(W,y)],fill=tuple(int(lt[i]*(1-a)+col[i]*a) for i in range(3))+(255,))
    return im
def layout(txt,sz,col,maxw=900,b=True):
    """*word* -> green. returns (RGBA layer W x h, height)"""
    fo=F(sz,b); toks=[]; on=False
    for w in txt.split():
        if w.startswith('*'): on=True
        toks.append((w.replace('*',''),on))
        if w.rstrip('?!.,').endswith('*'): on=False
    lines=[]; cur=[]; 
    for w,hl in toks:
        test=' '.join(x for x,_ in cur+[(w,hl)])
        if fo.getlength(test)<=maxw or not cur: cur.append((w,hl))
        else: lines.append(cur); cur=[(w,hl)]
    lines.append(cur)
    lh=int(sz*1.2); layer=Image.new('RGBA',(W,lh*len(lines)+10),(0,0,0,0)); d=ImageDraw.Draw(layer)
    for i,ln in enumerate(lines):
        total=fo.getlength(' '.join(x for x,_ in ln)); x=(W-total)/2
        for w,hl in ln:
            d.text((x,i*lh),w,font=fo,fill=(GREEN if hl else col)+(255,)); x+=fo.getlength(w+' ')
    return layer,lh*len(lines)
def with_alpha(layer,a):
    if a>=0.999: return layer
    l=layer.copy(); al=l.split()[-1].point(lambda v:int(v*a)); l.putalpha(al); return l
def logo(sz): return Image.open(ROOT+'/assets/img/logo-180.png').convert('RGBA').resize((sz,sz),Image.LANCZOS)
def footer(c,y=1760):
    c.alpha_composite(logo(56),(80,y)); ImageDraw.Draw(c).text((150,y+10),'@timetoapps.app',font=F(30,False),fill=(255,255,255,200))
def dot(c,x,y,r,col=GREEN):
    if r>0: ImageDraw.Draw(c).ellipse([x-r,y-r,x+r,y+r],fill=col)
def icon(k): return Image.open(f'{ROOT}/assets/img/{k}-icon.png').convert('RGBA')

class CountHook:
    tr='wipe'
    def __init__(s,k,label,amount,dec,sub,h1,h2,dur=4.8):
        s.dur=dur; s.amount=amount; s.dec=dec; s.label=label; s.sub=sub; s.bg=bgimg(BG[k])
        s.l1,s.h1=layout(h1,84,WHITE); s.l2,_=layout(h2,48,GREEN,b=False)
    def frame(s,t):
        c=s.bg.copy(); d=ImageDraw.Draw(c); lf=F(28); a=int(255*eo(t/0.5)); tr=5
        tw=sum(lf.getlength(ch)+tr for ch in s.label)-tr; x=(W-tw)/2
        for ch in s.label: d.text((x,560),ch,font=lf,fill=GREEN+(a,)); x+=lf.getlength(ch)+tr
        val=s.amount*eo((t-0.4)/1.6); ns=('${:,.%df}'%s.dec).format(val); nf=F(180)
        d.text(((W-nf.getlength(ns))/2,640),ns,font=nf,fill=WHITE+(int(255*min(1,max(0,(t-0.2)/0.4))),))
        sf=F(38,False); sa=int(235*eo((t-1.0)/0.6)); d.text(((W-sf.getlength(s.sub))/2,890),s.sub,font=sf,fill=WHITE+(sa,))
        p=eo((t-1.9)/0.5); c.alpha_composite(with_alpha(s.l1,p),(0,int(1130+(1-p)*40)))
        p2=eo((t-2.5)/0.5); c.alpha_composite(with_alpha(s.l2,p2),(0,int(1130+s.h1+24+(1-p2)*30)))
        return c

class ClipScene:
    PW=680; tr='fade'
    def __init__(s,k,head,sub,src,start,dur=4.6,first=False):
        s.dur=dur; s.src=src; s.start=start; s.first=first; s.tr='wipe' if first else 'fade'; s.bg=bgimg(BG[k])
        w=s.PW; h=int(round(w*2868/1320)); h-=h%2; s.w,s.h=w,h
        fr=int(w*0.035); r=int(w*0.12); s.fr=fr
        s.body=rounded(Image.new('RGBA',(w+2*fr,h+2*fr),(12,14,16,255)),r+fr); s.mask=rmask((w,h),r)
        s.px=(W-s.body.width)//2; s.py=440
        sh=Image.new('RGBA',(s.body.width+200,s.body.height+200),(0,0,0,0))
        a=s.body.split()[-1].point(lambda v:v*120//255); sh.paste((0,0,0,255),(100,130),a)
        s.sh=sh.filter(ImageFilter.GaussianBlur(45))
        s.lh,hh=layout(head,76,WHITE,maxw=980); s.ls,_=layout(sub,44,GREEN,b=False); s.hh=hh
        col=BG[k]; lt=tuple(min(255,int(c*1.35)+8) for c in col)
        s.band=Image.new('RGBA',(W,470),(0,0,0,0)); bd=ImageDraw.Draw(s.band)
        for y in range(470):
            al=255 if y<350 else int(255*(1-(y-350)/120)); bd.line([(0,y),(W,y)],fill=lt+(al,))
        s.proc=None; s.idx=-1; s.cur=None; s.n=int(dur*FPS)
    def _open(s):
        s.proc=subprocess.Popen(['ffmpeg','-loglevel','error','-ss',str(s.start),'-t',str(s.dur+0.3),'-i',s.src,
            '-vf',f'scale={s.w}:{s.h}:flags=lanczos,fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    def _vf(s,i):
        if s.proc is None: s._open()
        sz=s.w*s.h*3
        while s.idx<i:
            buf=s.proc.stdout.read(sz)
            if len(buf)<sz: s.idx=i; break
            s.cur=Image.frombytes('RGB',(s.w,s.h),buf); s.idx+=1
        if s.idx>=s.n-1 and s.proc.poll() is None: s.proc.stdout.close(); s.proc.terminate()
        return s.cur
    def frame(s,t):
        v=s._vf(min(int(round(t*FPS)),s.n-1)); base=s.bg.copy()
        off=int((1-eo(t/0.7))*900) if s.first else 0
        base.alpha_composite(s.sh,(s.px-100,s.py-100+off)); base.alpha_composite(s.body,(s.px,s.py+off))
        if v is not None: base.paste(v,(s.px+s.fr,s.py+s.fr+off),s.mask)
        base.alpha_composite(s.band,(0,0))
        if os.environ.get('CAPF')=='1':
            out=1-eio((t-(s.dur-0.2))/0.2)
            a1=min(eo((t-0.15)/0.3),out); a2=min(eo((t-0.45)/0.3),out)
        else:
            out=1-eio((t-(s.dur-0.25))/0.25)
            a1=min(eo((t-0.25)/0.4),out); a2=min(eo((t-0.7)/0.4),out)
        base.alpha_composite(with_alpha(s.lh,a1),(0,int(130+(1-a1)*36)))
        base.alpha_composite(with_alpha(s.ls,a2),(0,int(130+s.hh+14+(1-a2)*24)))
        return base

class End:
    tr='wipe'
    def __init__(s,k,dur=2.8):
        s.dur=dur; s.bg=bgimg(BG[k]); s.ic=rounded(icon(k).resize((320,320),Image.LANCZOS),72)
        s.nm,_=layout(NAME[k],74,WHITE); s.cs,_=layout('Coming soon on iOS & Android',44,GREEN,b=False)
    def frame(s,t):
        c=s.bg.copy(); p=eback(t/0.55); sz=max(1,int(320*p))
        c.alpha_composite(s.ic.resize((sz,sz),Image.BILINEAR),((W-sz)//2,int(720-sz/2)))
        a=eo((t-0.35)/0.4); c.alpha_composite(with_alpha(s.nm,a),(0,960)); a=eo((t-0.8)/0.4); c.alpha_composite(with_alpha(s.cs,a),(0,1075))
        dot(c,W//2,1250,int(22*eback((t-1.1)/0.4)))
        footer(c); return c

def render(scenes,out):
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',out]
    pr=subprocess.Popen(cmd,stdin=subprocess.PIPE); last=None
    for sc in scenes:
        n=int(sc.dur*FPS); tr=0.5 if sc.tr=='wipe' else 0.25
        for i in range(n):
            t=i/FPS; fr=sc.frame(t)
            if last is not None and t<tr:
                p=eio(t/tr)
                if sc.tr=='wipe':
                    R=int(math.hypot(W,H)/2*p)+1; m=Image.new('L',(W,H),0)
                    ImageDraw.Draw(m).ellipse([W//2-R,H//2-R,W//2+R,H//2+R],fill=255)
                    comp=last.copy(); comp.paste(fr,(0,0),m)
                    ImageDraw.Draw(comp).ellipse([W//2-R,H//2-R,W//2+R,H//2+R],outline=GREEN,width=16); fr=comp
                else: fr=Image.blend(last.convert('RGB'),fr.convert('RGB'),p)
            pr.stdin.write(fr.convert('RGB').tobytes())
        last=sc.frame(sc.dur-1/FPS)
    pr.stdin.close(); pr.wait(); print('OK',out,flush=True)

def clip(p): return glob.glob(SOC+'/clip/'+p)[0]
PLAN={
 'payday':('02-mar-reel-payday',clip('*17.23.51.mp4'),('REMAINING THIS CYCLE',1845.11,2,'left of your $3,200.00 budget.'),
   'Where did my salary go?','Time to find out.',
   [("Every dollar, *sorted*","Spending by category",0.5),
    ("Better than *last month*?","Compare your closed pay cycles",4.4),
    ("Log a spend in *a few taps*","Amount, category, done",39.5),
    ("What can I *spend today*?","Always one glance away",46.0)]),
 'sub':('03-mer-carosello-subscription',clip('*17.29.53.mp4'),('SUBSCRIPTIONS THIS MONTH',272.64,2,'across 13 active subscriptions.'),
   'Still paying for it?','Time to check.',
   [("Did you *really* use it?","Rate every subscription",1.5),
    ("No *surprise* charges","Upcoming charges at a glance",7.0),
    ("Where is it *heading*?","Past and expected spending",10.6),
    ("$94.98 on things you *barely use*","See what rarely used ones cost you",16.0)]),
 'restructure':('04-gio-post-restructure',clip('*17.35.24.mp4'),('COMMITTED SO FAR',46500,0,'of a $50,000 budget.'),
   'Renovating your home?','Keep quotes apart from costs.',
   [("What have you *committed*?","Committed vs. paid, at a glance",0.3),
    ("Where does the money *go*?","Costs room by room",3.8),
    ("A quote isn't a cost *yet*","Quotes stay apart until you confirm",9.2),
    ("Every receipt in *one place*","Quotes, invoices, warranties",15.6)]),
 'event':('05-ven-reel-event',clip('Simulator*17.13.39.mp4'),('COMMITTED SO FAR',20530,0,'of a $25,000 budget.'),
   'Planning a wedding?','Budget, guests, tables.',
   [("*142* days to go","Committed vs. paid vs. budget",0.3),
    ("Who's *coming*?","Your guest list",6.0),
    ("Who sits *where*?","Seat your guests",12.6),
    ("Meat or *fish*?","Each guest's menu choice",20.2)]),
}
if __name__=='__main__':
    k=sys.argv[1]; folder,src,cnt,h1,h2,segs=PLAN[k]
    scenes=[CountHook(k,cnt[0],cnt[1],cnt[2],cnt[3],h1,h2,dur=float(os.environ.get('DUR_HOOK','4.8')))]
    for i,(hd,sb,st) in enumerate(segs): scenes.append(ClipScene(k,hd,sb,src,st,dur=float(os.environ.get('DUR_CLIP','4.6')),first=(i==0)))
    scenes.append(End(k))
    render(scenes,os.environ.get('OUT') or f'{SOC}/{folder}/reel-v5.mp4')
