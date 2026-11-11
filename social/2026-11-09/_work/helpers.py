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

