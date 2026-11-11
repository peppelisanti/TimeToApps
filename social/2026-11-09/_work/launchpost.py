import sys; sys.path.insert(0,'_work')
import helpers as B
from PIL import Image, ImageDraw, ImageFilter
W,H=1080,1350
c=Image.new('RGBA',(W,H),(16,24,32,255))
glow=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(glow).ellipse([-200,700,700,1500],fill=(40,70,50,90))
c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
d=ImageDraw.Draw(c)
l=Image.open(B.D+'/TimeToApps/assets/img/logo-180.png').convert('RGBA').resize((130,130),Image.LANCZOS)
c.alpha_composite(l,((W-130)//2,70))
B.text(c,'Time to Apps',215,38)
B.text(c,'Four small apps\nfor everyday money.',290,66,lh=1.12)
labels=[('payday','Payday',(166,224,138)),('sub','Subscription',(240,160,112)),('restructure','Restructure',(242,193,78)),('event','Event',(232,115,90))]
sz=212
for i,(k,lab,col) in enumerate(labels):
    x=[262,606][i%2]; y=[515,815][i//2]
    ic=B.rounded(B.icon(k).resize((sz,sz),Image.LANCZOS),52)
    B.paste_shadow(c,ic,(x,y),blur=24,op=120)
    fo=B.f(32); w=fo.getlength(lab); d.text((x+sz/2-w/2,y+sz+14),lab,font=fo,fill=col)
fo=B.f(42); t='COMING SOON'; sp=4
tw=sum(fo.getlength(ch) for ch in t)+sp*(len(t)-1); pw=tw+110; px=(W-pw)/2; py=1125
d.rounded_rectangle([px,py,px+pw,py+88],44,fill=B.GREEN)
x=px+55
for ch in t: d.text((x,py+16),ch,font=fo,fill=(16,24,32)); x+=fo.getlength(ch)+sp
fo=B.f(28,False); t='iOS · ANDROID'; sp=6
tw=sum(fo.getlength(ch) for ch in t)+sp*(len(t)-1); x=(W-tw)/2
for ch in t: d.text((x,1250),ch,font=fo,fill=(200,205,210)); x+=fo.getlength(ch)+sp
c.convert('RGB').save('../2026-11-07-post-lancio/post.jpg',quality=95)
