from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920; PINK=(232,80,143); WHITE=(255,255,255); DARK=(43,34,40)
F="/usr/share/fonts/opentype/inter/"
B=lambda s: ImageFont.truetype(F+"Inter-Bold.otf",s); M=lambda s: ImageFont.truetype(F+"Inter-SemiBold.otf",s)
def base():
    im=Image.new("RGB",(W,H),"black"); d=ImageDraw.Draw(im)
    d.rectangle((0,607,W,1325),fill=(70,62,66))
    d.text((W/2,900),"TA VIDÉO YOUTUBE",font=B(46),fill=(150,140,145),anchor="mm")
    d.text((W/2,960),"(horizontale, pleine largeur)",font=M(34),fill=(150,140,145),anchor="mm")
    return im,d
def line(d,y,parts,f):
    tw=sum(d.textlength(t,font=f) for t,_ in parts); x=(W-tw)/2
    for t,c in parts: d.text((x,y),t,font=f,fill=c); x+=d.textlength(t,font=f)
# A : mots-clés du hook en rose, mot du sous-titre en rose
im,d=base(); f=B(46)
line(d,455,[("Tu as ",WHITE),("TOUT essayé",PINK),(" pour maigrir ?",WHITE)],f)
line(d,520,[("Voici la ",WHITE),("vraie raison",PINK),(" :",WHITE)],f)
d.text((780,1060),"privation",font=B(44),fill=PINK,anchor="mm")
d.text((W/2,1500),"Option A",font=B(40),fill=(90,90,90),anchor="mm")
im.save("modeles/maquette_mofu_A.png")
# B : hook dans un bandeau rose arrondi, sous-titres blancs
im,d=base(); f=B(46)
for y,t in [(445,"Tu as TOUT essayé pour maigrir ?"),(518,"Voici la vraie raison :")]:
    tw=d.textlength(t,font=f); x=(W-tw)/2
    d.rounded_rectangle((x-24,y-14,x+tw+24,y+60),18,fill=PINK); d.text((x,y),t,font=f,fill=WHITE)
d.text((780,1060),"privation",font=B(44),fill=WHITE,anchor="mm")
d.text((W/2,1500),"Option B",font=B(40),fill=(90,90,90),anchor="mm")
im.save("modeles/maquette_mofu_B.png")
# C : mélange. Hook blanc, mots-clés dans un petit bandeau rose arrondi ; sous-titres blancs, mots importants en rose
im,d=base(); f=B(46)
def line_box(y,parts):
    sp=10; ws=[(t,k,d.textlength(t,font=f)) for t,k in parts]
    tw=sum(w for _,_,w in ws)+sp*sum(1 for _,k,_ in ws if k)*2; x=(W-tw)/2
    for t,k,w in ws:
        if k:
            x+=sp; d.rounded_rectangle((x-12,y-10,x+w+12,y+58),14,fill=PINK); d.text((x,y),t,font=f,fill=WHITE); x+=w+sp
        else:
            d.text((x,y),t,font=f,fill=WHITE); x+=w
line_box(450,[("Tu as ",0),("TOUT essayé",1),(" pour maigrir ?",0)])
line_box(525,[("Voici la ",0),("vraie raison",1),(" :",0)])
d.text((780,1060),"privation",font=B(44),fill=PINK,anchor="mm")
d.text((W/2,1500),"Option C (mélange)",font=B(40),fill=(90,90,90),anchor="mm")
im.save("modeles/maquette_mofu_C.png")
