# Slide 2 e 3 del carosello Subscription con iPhone intero in verticale (che esce dal bordo in basso)
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.expanduser('~/Developer')
OUT=D+'/TimeToApps/social/2026-11-09/03-mer-carosello-subscription'
SH=D+'/iOS/TimeToSub/docs/app-store/screenshots/iphone-6.9/en'
FB=D+'/TimeToApps/assets/fonts/OpenSans-SemiBold.ttf'
BG=(13,46,63); WHITE=(255,255,255)
def rmask(size,r):
    s=4; m=Image.new('L',(size[0]*s,size[1]*s),0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]*s-1,size[1]*s-1],r*s,fill=255)
    return m.resize(size,Image.LANCZOS)
def rounded(im,r): im=im.copy(); im.putalpha(rmask(im.size,r)); return im
def iphone(n,w):
    s=Image.open(f'{SH}/{n}.png').convert('RGBA')
    h=int(s.height*w/s.width); s=s.resize((w,h),Image.LANCZOS)
    fr=int(w*0.04); r=int(w*0.14)
    W,H=w+2*fr,h+2*fr
    body=rounded(Image.new('RGBA',(W,H),(58,62,68,255)),r+fr)           # bordo metallico
    body.alpha_composite(rounded(Image.new('RGBA',(W-6,H-6),(10,11,13,255)),r+fr-3),(3,3))
    body.alpha_composite(rounded(s,r),(fr,fr))
    d=ImageDraw.Draw(body); iw,ih=int(w*0.29),int(w*0.085); iy=fr+int(w*0.026)
    d.rounded_rectangle([(W-iw)//2,iy,(W+iw)//2,iy+ih],ih//2,fill=(0,0,0,255))  # Dynamic Island
    # tasti laterali
    full=Image.new('RGBA',(W+12,H),(0,0,0,0)); dd=ImageDraw.Draw(full)
    for y0,y1 in [(0.17,0.21),(0.25,0.32),(0.34,0.41)]: dd.rounded_rectangle([0,int(H*y0),8,int(H*y1)],3,fill=(58,62,68,255))
    dd.rounded_rectangle([W+4,int(H*0.27),W+12,int(H*0.38)],3,fill=(58,62,68,255))
    full.alpha_composite(body,(6,0)); return full
def shadow_paste(c,im,xy,blur=45,op=140):
    sh=Image.new('RGBA',(im.width+blur*4,im.height+blur*4),(0,0,0,0))
    sh.paste((0,0,0,255),(blur*2,blur*2+25),im.split()[-1].point(lambda v:v*op//255))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)),(xy[0]-blur*2,xy[1]-blur*2)); c.alpha_composite(im,xy)
def text(c,txt,y,sz,maxw=920):
    fo=ImageFont.truetype(FB,sz); d=ImageDraw.Draw(c); lines=[]; line=''
    for w_ in txt.split():
        t=(line+' '+w_).strip()
        if fo.getlength(t)<=maxw: line=t
        else: lines.append(line); line=w_
    lines.append(line)
    for ln in lines: d.text(((c.width-fo.getlength(ln))/2,y),ln,font=fo,fill=WHITE); y+=int(sz*1.18)
    return y
def slide(title,n,name):
    c=Image.new('RGBA',(1080,1350),BG+(255,))
    y=text(c,title,80,56)
    p=iphone(n,540); shadow_paste(c,p,((1080-p.width)//2,y+40))
    c.convert('RGB').save(f'{OUT}/{name}',quality=95); print(name,y)
slide('Rate how much you use each subscription right after it renews','01','slide2.jpg')
slide('See how much you spend on the ones you barely use','07','slide3.jpg')
