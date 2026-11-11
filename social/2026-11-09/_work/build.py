import os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.expanduser('~/mnt/Developer')
OUT=os.path.join(D,'TimeToApps/social/2026-11-09')
W='_work'
FB=D+'/TimeToApps/assets/fonts/OpenSans-SemiBold.ttf'
FR=D+'/TimeToApps/assets/fonts/OpenSans-Regular.ttf'
GREEN=(166,224,138); WHITE=(255,255,255); BRAND=(16,24,32)
def f(sz,b=True): return ImageFont.truetype(FB if b else FR,sz)
APPS={
 'payday':dict(name='Time to Payday',dir='TimeToPayday',bg=(15,58,46),shots='TimeToPayday/docs/app-store/screenshots/iphone-6.9/en'),
 'sub':dict(name='Time to Subscription',dir='TimeToSub',bg=(13,46,63),shots='TimeToSub/docs/app-store/screenshots/iphone-6.9/en'),
 'restructure':dict(name='Time to Restructure',dir='TimeToRestructure',bg=(36,28,66),shots='TimeToRestructure/docs/app-store/screenshots/iphone-6.9/en'),
 'event':dict(name='Time to Event',dir='TimeToEvent',bg=None,shots='TimeToEvent/docs/app-store/screenshots/iphone-6.9/en'),
}
def icon(k):
    return Image.open(f"{D}/iOS/{APPS[k]['dir']}/{APPS[k]['dir']}/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png").convert('RGBA')
APPS['event']['bg']=icon('event').convert('RGB').getpixel((40,512))
def shot(k,n): return Image.open(f"{D}/iOS/{APPS[k]['shots']}/{n}.png").convert('RGBA')
def rmask(size,r):
    s=4; m=Image.new('L',(size[0]*s,size[1]*s),0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]*s-1,size[1]*s-1],r*s,fill=255)
    return m.resize(size,Image.LANCZOS)
def rounded(im,r):
    im=im.copy(); im.putalpha(rmask(im.size,r)); return im
def paste_shadow(c,im,xy,blur=40,op=110):
    sh=Image.new('RGBA',(im.width+blur*4,im.height+blur*4),(0,0,0,0))
    a=im.split()[-1].point(lambda v:v*op//255)
    sh.paste((0,0,0,255),(blur*2,blur*2+20),a)
    sh=sh.filter(ImageFilter.GaussianBlur(blur))
    c.alpha_composite(sh,(xy[0]-blur*2,xy[1]-blur*2))
    c.alpha_composite(im,xy)
def phone(k,n,w,crop=None):
    s=shot(k,n)
    if crop: s=s.crop((0,int(s.height*crop[0]),s.width,int(s.height*crop[1])))
    h=int(s.height*w/s.width); s=s.resize((w,h),Image.LANCZOS)
    fr=int(w*0.035); r=int(w*0.12) if not crop else int(w*0.06)
    body=Image.new('RGBA',(w+2*fr,h+2*fr),(12,14,16,255))
    body=rounded(body,r+fr); body.alpha_composite(rounded(s,r),(fr,fr))
    return body
def logo(sz):
    from io import BytesIO
    im=Image.open(D+'/TimeToApps/assets/img/logo-180.png').convert('RGBA')
    return im.resize((sz,sz),Image.LANCZOS)
def wrap(text,font,maxw):
    out=[]
    for para in text.split('\n'):
        line=''
        for w_ in para.split():
            t=(line+' '+w_).strip()
            if font.getlength(t)<=maxw: line=t
            else: out.append(line); line=w_
        out.append(line)
    return out
def text(c,txt,y,sz,col=WHITE,b=True,maxw=None,align='center',x=None,lh=1.18):
    fo=f(sz,b); maxw=maxw or c.width-160; d=ImageDraw.Draw(c)
    for ln in wrap(txt,fo,maxw):
        lw=fo.getlength(ln)
        xx = (c.width-lw)/2 if align=='center' else x
        d.text((xx,y),ln,font=fo,fill=col); y+=int(sz*lh)
    return y
def canvas(bg,h=1350): return Image.new('RGBA',(1080,h),bg+(255,))
def footer(c,y=None):
    y=y or c.height-110; l=logo(56); c.alpha_composite(l,(80,y))
    ImageDraw.Draw(c).text((150,y+10),'@timetoapps.app',font=f(30,False),fill=(255,255,255,200))
def dot(c,x,y,r=22,col=GREEN):
    ImageDraw.Draw(c).ellipse([x-r,y-r,x+r,y+r],fill=col)
def appicon(c,k,xy,sz):
    c.alpha_composite(rounded(icon(k).resize((sz,sz),Image.LANCZOS),int(sz*0.225)),xy)
def save(c,name): c.convert('RGB').save(os.path.join(OUT,name),quality=95); print(name)

# ---------- MON carousel
os.makedirs(OUT+'/01-lun-carosello',exist_ok=True)
c=canvas(BRAND); l=logo(420); c.alpha_composite(rounded(l,94),(330,260))
y=text(c,'Four apps.',760,92); text(c,'One circle.',y,92,col=GREEN); footer(c); save(c,'01-lun-carosello/slide1.jpg')
mon=[('payday','Payday','See where your salary goes','01'),('sub','Subscription','Pay only for what you use','01'),('restructure','Restructure','Your renovation, under control','01'),('event','Event','Your big day, organized','01')]
for i,(k,short,claim,n) in enumerate(mon,2):
    c=canvas(APPS[k]['bg']); appicon(c,k,(80,90),120)
    ImageDraw.Draw(c).text((230,100),APPS[k]['name'],font=f(44),fill=WHITE)
    ImageDraw.Draw(c).text((230,160),'Coming soon',font=f(30,False),fill=GREEN)
    text(c,claim,280,64,align='left',x=80,maxw=920)
    p=phone(k,n,620); paste_shadow(c,p,((1080-p.width)//2,470))
    save(c,f'01-lun-carosello/slide{i}.jpg')
c=canvas(BRAND); text(c,'Coming soon',330,96)
for j,k in enumerate(['payday','sub','restructure','event']): appicon(c,k,(105+j*225,560),190)
text(c,'Coming soon on iOS & Android',900,44,b=False,col=GREEN)
footer(c); save(c,'01-lun-carosello/slide6.jpg')

# ---------- WED carousel Subscription
os.makedirs(OUT+'/03-mer-carosello-subscription',exist_ok=True)
bg=APPS['sub']['bg']
c=canvas(bg); y=text(c,'It just renewed.',420,96); text(c,'Are you actually using it?',y+30,72,col=GREEN,maxw=880); footer(c); save(c,'03-mer-carosello-subscription/slide1.jpg')
c=canvas(bg); text(c,'Rate how much you use each subscription right after it renews',110,58,maxw=900)
p=phone('sub','01',900,crop=(0.592,0.875)); paste_shadow(c,p,((1080-p.width)//2,560)); footer(c); save(c,'03-mer-carosello-subscription/slide2.jpg')
c=canvas(bg); text(c,'See how much you spend on the ones you barely use',110,58,maxw=900)
p=phone('sub','07',760,crop=(0.11,0.555)); paste_shadow(c,p,((1080-p.width)//2,470)); save(c,'03-mer-carosello-subscription/slide3.jpg')
c=canvas(bg); y=text(c,'Keep what you use.',470,84); text(c,"Cut what you don't.",y+10,84,col=GREEN); footer(c); save(c,'03-mer-carosello-subscription/slide4.jpg')
c=canvas(bg); appicon(c,'sub',(390,330),300); text(c,'Time to Subscription',720,64); text(c,'Coming soon on iOS & Android',820,40,b=False,col=GREEN); footer(c); save(c,'03-mer-carosello-subscription/slide5.jpg')

# ---------- THU post Restructure
os.makedirs(OUT+'/04-gio-post-restructure',exist_ok=True)
c=canvas(APPS['restructure']['bg']); y=text(c,'Renovating?',90,84); text(c,"Your quotes aren't expenses. Yet.",y,58,col=GREEN,maxw=900)
p=phone('restructure','05',620); paste_shadow(c,p,((1080-p.width)//2,400))
save(c,'04-gio-post-restructure/post.jpg')

# ---------- stories
os.makedirs(OUT+'/06-sab-storia-event',exist_ok=True); os.makedirs(OUT+'/07-dom-storia',exist_ok=True)
c=canvas(APPS['event']['bg'],1920); appicon(c,'event',(420,300),240); text(c,'What are you planning?',640,84,maxw=860)
d=ImageDraw.Draw(c); d.rounded_rectangle([140,1000,940,1420],40,outline=(255,255,255,90),width=4)
text(c,'(aggiungi qui lo sticker Sondaggio)',1190,30,b=False,col=(255,255,255,120))
text(c,'Time to Event · coming soon',1650,36,b=False,col=GREEN); save(c,'06-sab-storia-event/storia-sondaggio.jpg')
c=canvas(BRAND,1920); y=text(c,'This week on',380,64,b=False); text(c,'Time to Apps',y,96)
for j,k in enumerate(['payday','sub','restructure','event']):
    x=150+(j%2)*420; yy=760+(j//2)*420; appicon(c,k,(x,yy),360)
text(c,'Coming soon · iOS & Android',1650,44,col=GREEN); save(c,'07-dom-storia/storia-riepilogo.jpg')

# ---------- reels
def reel(folder,frames,dur=2.6,fade=0.5):
    os.makedirs(OUT+'/'+folder,exist_ok=True); fs=[]
    for i,fr in enumerate(frames):
        p=f'{W}/{folder}_{i}.png'; fr.convert('RGB').save(p); fs.append(p)
    cmd=['ffmpeg','-y','-loglevel','error']
    for p in fs: cmd+=['-loop','1','-t',str(dur),'-framerate','30','-i',p]
    flt=''; last='[0:v]'; off=dur-fade
    for i in range(1,len(fs)):
        o=f'[v{i}]'; flt+=f'{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={off:.2f}{o};'; last=o; off+=dur-fade
    flt+=f'{last}format=yuv420p[out]'
    cmd+=['-filter_complex',flt,'-map','[out]','-c:v','libx264','-preset','veryfast','-crf','20','-r','30','-movflags','+faststart',OUT+'/'+folder+'/reel.mp4']
    subprocess.run(cmd,check=True); print(folder)
def hook(k,a,b):
    c=canvas(APPS[k]['bg'],1920); y=text(c,a,700,104,maxw=900); text(c,b,y+20,60,col=GREEN,maxw=900); return c
def scene(k,cap,n,crop=None):
    c=canvas(APPS[k]['bg'],1920); text(c,cap,160,62,maxw=900)
    p=phone(k,n,700 if not crop else 940,crop); paste_shadow(c,p,((1080-p.width)//2,370 if not crop else 520)); return c
def end(k):
    c=canvas(APPS[k]['bg'],1920); appicon(c,k,(375,560),330); text(c,APPS[k]['name'],990,72); text(c,'Coming soon on iOS & Android',1100,44,b=False,col=GREEN); footer(c,1760); return c
reel('02-mar-reel-payday',[hook('payday','Where did my salary go?',''),scene('payday','Spending by category','03'),scene('payday','Compare your closed pay cycles','05',crop=(0.1,0.6)),end('payday')])
reel('05-ven-reel-event',[hook('event','Planning a wedding?','Budget, guests, tables.'),scene('event','Committed vs. paid vs. budget','01'),scene('event','Your guest list','03'),scene('event','Table seating','04'),end('event')])
