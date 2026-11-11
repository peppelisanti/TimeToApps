import glob
class ClipScene:
    PW=700
    def __init__(s,k,cap,src,start,dur):
        s.k=k; s.dur=dur; s.src=src; s.start=start
        s.bg=bgimg(B.APPS[k]['bg'])
        w=s.PW; h=int(round(w*2868/1320)); h-=h%2
        s.w,s.h=w,h
        fr=int(w*0.035); r=int(w*0.12); s.fr=fr
        s.body=B.rounded(Image.new('RGBA',(w+2*fr,h+2*fr),(12,14,16,255)),r+fr)
        s.mask=B.rmask((w,h),r)
        s.px=(W-s.body.width)//2; s.py=350
        sh=Image.new('RGBA',(s.body.width+200,s.body.height+200),(0,0,0,0))
        a=s.body.split()[-1].point(lambda v:v*120//255); sh.paste((0,0,0,255),(100,130),a)
        s.sh=sh.filter(ImageFilter.GaussianBlur(45))
        s.cap,_=word_layer(cap,64,B.WHITE)
        s.nl=len(set(d for _,_,d,_,_ in s.cap))
        col=B.APPS[k]['bg']; lt=tuple(min(255,int(c*1.35)+8) for c in col)
        s.band=Image.new('RGBA',(W,420),(0,0,0,0)); bd=ImageDraw.Draw(s.band)
        for y in range(420):
            al=255 if y<300 else int(255*(1-(y-300)/120)); bd.line([(0,y),(W,y)],fill=lt+(al,))
        s.proc=None; s.idx=-1; s.cur=None; s.n=int(dur*FPS)
    def _open(s):
        cmd=['ffmpeg','-loglevel','error','-ss',str(s.start),'-t',str(s.dur+0.2),'-i',s.src,
             '-vf',f'scale={s.w}:{s.h}:flags=lanczos,fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-']
        s.proc=subprocess.Popen(cmd,stdout=subprocess.PIPE)
    def _frame_at(s,i):
        if s.proc is None: s._open()
        sz=s.w*s.h*3
        while s.idx<i:
            buf=s.proc.stdout.read(sz)
            if len(buf)<sz: s.idx=i; break
            s.cur=Image.frombytes('RGB',(s.w,s.h),buf); s.idx+=1
        if s.idx>=s.n-1 and s.proc.poll() is None:
            s.proc.stdout.close(); s.proc.terminate()
        return s.cur
    def frame(s,t):
        i=min(int(round(t*FPS)),s.n-1)
        v=s._frame_at(i)
        base=s.bg.copy()
        off=int((1-eo(t/0.7))*900)
        base.alpha_composite(s.sh,(s.px-100,s.py-100+off)); base.alpha_composite(s.body,(s.px,s.py+off))
        if v is not None: base.paste(v,(s.px+s.fr,s.py+s.fr+off),s.mask)
        base.alpha_composite(s.band,(0,0))
        draw_words(base,s.cap,150,t-0.25,stagger=.06)
        bw=eo((t-0.6)/0.5)
        if bw>0:
            y=int(150+s.nl*76+14)
            ImageDraw.Draw(base).rounded_rectangle([W//2-int(70*bw),y,W//2+int(70*bw),y+10],5,fill=B.GREEN)
        return base
def clip(pat): return glob.glob('clip/'+pat)[0]
PLAN={
 'event':('05-ven-reel-event',clip('Simulator*17.13.39.mp4'),'Planning a wedding?','Budget, guests, tables.',
   [("Committed vs. paid vs. budget",0.3),("Your guest list",6.0),("Seat your guests",12.6),("Each guest's menu choice",20.2)],3.6),
 'payday':('02-mar-reel-payday',clip('*17.23.51.mp4'),'Where did my salary go?','Time to find out.',
   [("Spending by category",0.5),("Compare your closed pay cycles",4.4),("See what you can spend today",46.0)],3.8),
 'sub':('03-mer-carosello-subscription',clip('*17.29.53.mp4'),'Still paying for it?','Time to check.',
   [("How much did you really use it?",1.5),("Upcoming charges at a glance",7.0),("Past and expected spending",10.6),("What rarely used ones cost you",16.0)],3.6),
 'restructure':('04-gio-post-restructure',clip('*17.35.24.mp4'),'Renovating your home?','Keep quotes apart from costs.',
   [("Committed vs. paid",0.3),("Costs room by room",3.8),("Quotes stay apart until confirmed",9.2),("Every document in one place",15.6)],3.6),
}
which=sys.argv[1]
folder,src,h1,h2,segs,d=PLAN[which]
scenes=[Hook(which,h1,h2)]+[ClipScene(which,c,src,st,d) for c,st in segs]+[End(which)]
render(scenes,folder+'/reel-clip.mp4')
