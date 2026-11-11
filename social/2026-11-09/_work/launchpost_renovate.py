import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..','..'))
FB=ROOT+'/assets/fonts/OpenSans-SemiBold.ttf'; FR=ROOT+'/assets/fonts/OpenSans-Regular.ttf'
GREEN=(166,224,138); WHITE=(255,255,255)
def f(sz,b=True): return ImageFont.truetype(FB if b else FR,sz)
def rmask(size,r):
    s=4; m=Image.new('L',(size[0]*s,size[1]*s),0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]*s-1,size[1]*s-1],r*s,fill=255); return m.resize(size,Image.LANCZOS)
def rounded(im,r): im=im.copy(); im.putalpha(rmask(im.size,r)); return im
def paste_shadow(c,im,xy,blur=40,op=110):
    sh=Image.new('RGBA',(im.width+blur*4,im.height+blur*4),(0,0,0,0))
    a=im.split()[-1].point(lambda v:v*op//255); sh.paste((0,0,0,255),(blur*2,blur*2+20),a)
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)),(xy[0]-blur*2,xy[1]-blur*2)); c.alpha_composite(im,xy)
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
def text(c,txt,y,sz,col=WHITE,b=True,maxw=None,lh=1.18):
    fo=f(sz,b); maxw=maxw or c.width-160; d=ImageDraw.Draw(c)
    for ln in wrap(txt,fo,maxw): d.text(((c.width-fo.getlength(ln))/2,y),ln,font=fo,fill=col); y+=int(sz*lh)
    return y
def icon(k): return Image.open(f'{ROOT}/assets/img/{k}-icon.png').convert('RGBA')
W,H=1080,1350
c=Image.new('RGBA',(W,H),(16,24,32,255))
glow=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(glow).ellipse([-200,700,700,1500],fill=(40,70,50,90))
c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
d=ImageDraw.Draw(c)
l=Image.open(ROOT+'/assets/img/logo-180.png').convert('RGBA').resize((130,130),Image.LANCZOS)
c.alpha_composite(l,((W-130)//2,70))
text(c,'Time to Apps',215,38)
text(c,'Four small apps\nfor everyday money.',290,66,lh=1.12)
labels=[('payday','Payday',(166,224,138)),('sub','Subscription',(240,160,112)),('restructure','Renovate',(242,193,78)),('event','Event',(232,115,90))]
sz=212
for i,(k,lab,col) in enumerate(labels):
    x=[262,606][i%2]; y=[515,815][i//2]
    ic=rounded(icon(k).resize((sz,sz),Image.LANCZOS),52); paste_shadow(c,ic,(x,y),blur=24,op=120)
    fo=f(32); w=fo.getlength(lab); d.text((x+sz/2-w/2,y+sz+14),lab,font=fo,fill=col)
fo=f(42); t='COMING SOON'; sp=4
tw=sum(fo.getlength(ch) for ch in t)+sp*(len(t)-1); pw=tw+110; px=(W-pw)/2; py=1125
d.rounded_rectangle([px,py,px+pw,py+88],44,fill=GREEN)
x=px+55
for ch in t: d.text((x,py+16),ch,font=fo,fill=(16,24,32)); x+=fo.getlength(ch)+sp
fo=f(28,False); t='iOS · ANDROID'; sp=6
tw=sum(fo.getlength(ch) for ch in t)+sp*(len(t)-1); x=(W-tw)/2
for ch in t: d.text((x,1250),ch,font=fo,fill=(200,205,210)); x+=fo.getlength(ch)+sp
c.convert('RGB').save(os.path.join(ROOT,'social/2026-11-07-post-lancio/post.jpg'),quality=95)
print('ok')
