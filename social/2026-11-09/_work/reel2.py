import sys, math, subprocess, os
sys.path.insert(0,'_work')
from PIL import Image, ImageDraw, ImageFilter
import helpers as B
W,H,FPS=1080,1920,30
def eo(t): t=max(0,min(1,t)); return 1-(1-t)**3
def eio(t): t=max(0,min(1,t)); return 4*t**3 if t<.5 else 1-(-2*t+2)**3/2
def eback(t,s=1.7): t=max(0,min(1,t)); t-=1; return t*t*((s+1)*t+s)+1
def bgimg(col):
    # soft vertical gradient + big faint brand circle
    im=Image.new('RGBA',(W,H),col+(255,)); d=ImageDraw.Draw(im)
    lt=tuple(min(255,int(c*1.35)+8) for c in col)
    for y in range(H):
        a=y/H; d.line([(0,y),(W,y)],fill=tuple(int(lt[i]*(1-a)+col[i]*a) for i in range(3))+(255,))
    return im
def word_layer(txt,sz,col,maxw=900,b=True):
    fo=B.f(sz,b); lines=B.wrap(txt,fo,maxw); out=[]; lh=int(sz*1.18)
    for li,ln in enumerate(lines):
        ws=ln.split(); total=fo.getlength(ln); x=(W-total)/2
        for w_ in ws:
            out.append((w_,x,li*lh,fo,col)); x+=fo.getlength(w_+' ')
    return out,len(lines)*lh
def draw_words(c,words,y0,t,stagger=.09,dur=.45):
    for i,(w_,x,dy,fo,col) in enumerate(words):
        p=eo((t-i*stagger)/dur)
        if p<=0: continue
        tmp=Image.new('RGBA',(int(fo.getlength(w_))+20,int(fo.size*1.5)),(0,0,0,0))
        ImageDraw.Draw(tmp).text((0,0),w_,font=fo,fill=col+(int(255*p),))
        c.alpha_composite(tmp,(int(x),int(y0+dy+(1-p)*50)))
class Hook:
    def __init__(s,k,a,b,dur=2.4):
        s.bg=bgimg(B.APPS[k]['bg']); s.dur=dur
        s.wa,ha=word_layer(a,108,B.WHITE); s.wb,hb=word_layer(b,62,B.GREEN) if b else ([],0)
        s.y=(H-ha-hb-30)//2; s.ha=ha
    def frame(s,t):
        c=s.bg.copy(); z=1+0.04*t/s.dur
        draw_words(c,s.wa,s.y,t); draw_words(c,s.wb,s.y+s.ha+30,t-0.5)
        # green dot pops after text
        p=eback((t-0.9)/0.4); 
        if p>0: B.dot(c,W//2,int(s.y-90),int(26*p))
        return c
class Scene:
    def __init__(s,k,cap,n,focus,zoom=1.45,dur=3.4):
        s.k=k; s.dur=dur; s.bg=bgimg(B.APPS[k]['bg']); s.zoom=zoom
        s.ph=B.phone(k,n,720); sh=Image.new('RGBA',(s.ph.width+200,s.ph.height+200),(0,0,0,0))
        a=s.ph.split()[-1].point(lambda v:v*120//255); sh.paste((0,0,0,255),(100,130),a)
        s.sh=sh.filter(ImageFilter.GaussianBlur(45))
        s.px=(W-s.ph.width)//2; s.py=420
        fr=int(720*0.035); sw=720; shh=s.ph.height-2*fr
        s.fx=s.px+fr+focus[0]*sw; s.fy=s.py+fr+focus[1]*shh
        s.cap,_=word_layer(cap,64,B.WHITE)
        s.band=Image.new('RGBA',(W,420),(0,0,0,0)); col=B.APPS[k]['bg']; lt=tuple(min(255,int(c*1.35)+8) for c in col)
        bd=ImageDraw.Draw(s.band)
        for y in range(420):
            a=255 if y<300 else int(255*(1-(y-300)/120)); bd.line([(0,y),(W,y)],fill=lt+(a,))
    def frame(s,t):
        base=s.bg.copy()
        p=eo(t/0.8); off=int((1-p)*900)
        base.alpha_composite(s.sh,(s.px-100,s.py-100+off)); base.alpha_composite(s.ph,(s.px,s.py+off))
        zp=eio((t-1.0)/(s.dur-1.4)); z=1+(s.zoom-1)*zp
        if z>1.001:
            cx=W/2+(s.fx-W/2)*zp; cy=H/2+(s.fy-H/2)*zp; w=W/z; h=H/z
            x0=min(max(cx-w/2,0),W-w); y0=min(max(cy-h/2,0),H-h)
            base=base.crop((int(x0),int(y0),int(x0+w),int(y0+h))).resize((W,H),Image.BILINEAR)
        base.alpha_composite(s.band,(0,0))
        draw_words(base,s.cap,150,t-0.25,stagger=.06)
        bw=eo((t-0.6)/0.5)
        if bw>0: ImageDraw.Draw(base).rounded_rectangle([W//2-int(70*bw),int(150+len(set(d for _,_,d,_,_ in s.cap))*76+14),W//2+int(70*bw),int(150+len(set(d for _,_,d,_,_ in s.cap))*76+24)],5,fill=B.GREEN)
        return base
class End:
    def __init__(s,k,dur=2.6):
        s.k=k; s.dur=dur; s.bg=bgimg(B.APPS[k]['bg'])
        s.ic=B.rounded(B.icon(k).resize((340,340),Image.LANCZOS),76)
        s.nm,_=word_layer(B.APPS[k]['name'],74,B.WHITE); s.cs,_=word_layer('Coming soon on iOS & Android',44,B.GREEN,b=False)
    def frame(s,t):
        c=s.bg.copy(); p=eback(t/0.55); sz=max(1,int(340*p))
        ic=s.ic.resize((sz,sz),Image.BILINEAR); c.alpha_composite(ic,((W-sz)//2,int(720-sz/2)))
        draw_words(c,s.nm,960,t-0.35,stagger=.07); draw_words(c,s.cs,1075,t-0.8,stagger=.05)
        pr=(t-1.3)%1.2/1.2 if t>1.3 else None
        if pr is not None:
            r=int(26+40*pr); ImageDraw.Draw(c).ellipse([W//2-r,1250-r,W//2+r,1250+r],outline=B.GREEN+(int(255*(1-pr)),),width=6)
        B.dot(c,W//2,1250,int(22*eback((t-1.1)/0.4)) or 0)
        B.footer(c,1760); return c
def render(scenes,out,tr=.45):
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',out]
    pr=subprocess.Popen(cmd,stdin=subprocess.PIPE); last=None
    for si,sc in enumerate(scenes):
        n=int(sc.dur*FPS)
        for i in range(n):
            t=i/FPS; fr=sc.frame(t)
            if last is not None and t<tr:
                p=eio(t/tr); R=int(math.hypot(W,H)/2*p)+1
                m=Image.new('L',(W,H),0); ImageDraw.Draw(m).ellipse([W//2-R,H//2-R,W//2+R,H//2+R],fill=255)
                comp=last.copy(); comp.paste(fr,(0,0),m)
                ImageDraw.Draw(comp).ellipse([W//2-R,H//2-R,W//2+R,H//2+R],outline=B.GREEN,width=16)
                fr=comp
            pr.stdin.write(fr.convert('RGB').tobytes())
        last=sc.frame(sc.dur-1/FPS)
    pr.stdin.close(); pr.wait(); print(out)
which=sys.argv[1]
if which=='payday':
    render([Hook('payday','Where did my salary go?','Time to find out.'),
            Scene('payday','Spending by category','03',(0.5,0.40)),
            Scene('payday','Compare your closed pay cycles','05',(0.5,0.38),zoom=1.6),
            End('payday')],'02-mar-reel-payday/reel.mp4')
else:
    render([Hook('event','Planning a wedding?','Budget, guests, tables.'),
            Scene('event','Committed vs. paid vs. budget','01',(0.5,0.52),zoom=1.55,dur=3.0),
            Scene('event','Your guest list','03',(0.5,0.30),zoom=1.6,dur=3.0),
            Scene('event','Table seating','04',(0.5,0.62),zoom=1.5,dur=3.0),
            End('event')],'05-ven-reel-event/reel.mp4')
