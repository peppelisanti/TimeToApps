import sys; sys.path.insert(0,'_work')
import helpers as B
from PIL import Image, ImageDraw
OUT='00-copertine-in-evidenza'
items=[('payday','Payday'),('sub','Subscription'),('restructure','Restructure'),('event','Event')]
def cover(bg,draw_center,name):
    c=Image.new('RGBA',(1080,1920),bg+(255,))
    draw_center(c)
    c.convert('RGB').save(f'{OUT}/{name}.jpg',quality=95)
for k,label in items:
    def dc(c,k=k):
        ic=B.icon(k).resize((560,560),Image.LANCZOS)
        c.alpha_composite(ic,(260,680))   # full-bleed icon square, highlight crop shows the letter
    cover(B.APPS[k]['bg'],dc,f'cover-{k}')
def dl(c):
    l=Image.open(B.D+'/TimeToApps/assets/img/logo-180.png').convert('RGBA').resize((560,560),Image.LANCZOS)
    c.alpha_composite(l,(260,680))
cover(B.BRAND,dl,'cover-timetoapps')
# preview: circles as Instagram shows them
pv=Image.new('RGB',(5*240+60,320),'white'); d=ImageDraw.Draw(pv)
for i,n in enumerate(['timetoapps','payday','sub','restructure','event']):
    im=Image.open(f'{OUT}/cover-{n}.jpg').crop((180,600,900,1320)).resize((200,200))
    m=Image.new('L',(200,200),0); ImageDraw.Draw(m).ellipse([0,0,199,199],fill=255)
    pv.paste(im,(30+i*240,30),m); d.ellipse([28+i*240,28,232+i*240,232],outline=(200,200,200),width=2)
    d.text((30+i*240+60,250),['Time to','Payday','Subscription','Restructure','Event'][i],fill='black',font=B.f(24,False))
pv.save('_work/rev_covers.jpg')
