from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from akcnet.forms import SignUpForm
from ipware import get_client_ip
import csv
import sys
import os
import time
import sqlite3 as sql



def main(request):
    ip, is_routable = get_client_ip(request)
    duzen = request.GET.get("duzen", "populer")
    sayfa = request.GET.get("sayfa", "1")

    def tarihbul(tarih):
        named_tuple = time.localtime()
        anlik = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
        sure=0
        sure+=(int(anlik[0:4])-int(tarih[0:4]))*365*24*60
        sure+=(int(anlik[5:7])-int(tarih[5:7]))*30*24*60
        sure+=(int(anlik[8:10])-int(tarih[8:10]))*24*60
        sure+=(int(anlik[11:13])-int(tarih[11:13]))*60
        sure+=(int(anlik[14:16])-int(tarih[14:16]))
        sure-=180
        if sure < 60:
            return(f"{round(sure)} dakika önce")
        elif sure < 24*60:
            return(f"{round(sure/60)} saat önce")
        elif sure < 30*24*60:
            return(f"{round(sure/(60*24))} gün önce")
        elif sure < 365*24*60:
            return(f"{round(sure/(60*24*30))} ay önce")
        else:
            return(f"{round(sure/(60*24*365))} yıl önce")

    baslik=[]
    forum=[]
    yazar=[]
    tarih=[]
    metin=[]
    metinler=[]
    id=[]
    yorumsayi=[]
    tur=[]
    sure=[]

    fdb = sql.connect('./dbs/forum.db')
    im = fdb.cursor()
    im.execute("SELECT baslik,kategori,kullanici,tarih,metin_id,id,tur FROM konu ORDER BY tarih DESC Limit 20;")
    konular = im.fetchall()
    for i in konular:
        baslik.append(i[0][:26])
        forum.append(i[1])
        yazar.append(i[2])
        tarih.append(tarihbul(i[3]))
        metin.append(i[4])
        id.append(i[5])
        tur.append(i[6])
        im.execute(f"SELECT count(konu_id) FROM yorum WHERE konu_id={i[5]};")
        yorumsayi.append(im.fetchall()[0][0])
    icerik = len(id)
    for i in range(len(metin)):
        im.execute(f"SELECT metin FROM metin WHERE id={metin[i]}")
        m = im.fetchall()
        metinler.append(m[0][0][:64])
        if len(m[0][0])/800<1:
            sure.append(str(round((len(m[0][0])/800)*60))+" saniye")
        else:
            sure.append(str(round(len(m[0][0])/800)).split(".")[0]+" dakika")


    context={
    'duzen' : duzen,
    'baslik' : baslik,
    'forum' : forum,
    'metin' : metinler,
    'tur' : tur,
    'sure' : sure,
    'yazar' : yazar,
    'tarih' : tarih,
    'yorum' : yorumsayi,
    'okunmamis' : ["? Okunmamış Mesaj"]*10,
    'id' : id,
    }

    return render(request, "index.html", context)

def konu(request, id):
    def tarihbul(tarih):
        named_tuple = time.localtime()
        anlik = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
        sure=0
        sure+=(int(anlik[0:4])-int(tarih[0:4]))*365*24*60
        sure+=(int(anlik[5:7])-int(tarih[5:7]))*30*24*60
        sure+=(int(anlik[8:10])-int(tarih[8:10]))*24*60
        sure+=(int(anlik[11:13])-int(tarih[11:13]))*60
        sure+=(int(anlik[14:16])-int(tarih[14:16]))
        sure-=180
        if sure < 60:
            return(f"{round(sure)} dakika önce")
        elif sure < 24*60:
            return(f"{round(sure/60)} saat önce")
        elif sure < 30*24*60:
            return(f"{round(sure/(60*24))} gün önce")
        elif sure < 365*24*60:
            return(f"{round(sure/(60*24*30))} ay önce")
        else:
            return(f"{round(sure/(60*24*365))} yıl önce")

    fdb = sql.connect('./dbs/forum.db')
    im = fdb.cursor()
    im.execute(f"SELECT baslik,metin_id,kullanici,tarih,tur,kategori FROM konu WHERE id={id}")
    veri=im.fetchall()[0]
    baslik=veri[0]
    metin_id=veri[1]
    yazar=veri[2]
    tarih=tarihbul(veri[3])
    tur=veri[4]
    forum=veri[5]
    im.execute(f"SELECT metin FROM metin WHERE id={metin_id}")
    metin=im.fetchall()[0][0]
    sure=len(metin)/800
    if sure<1:
        sure=str(sure*60).split(".")[0]+" saniye"
    else:
        sure=str(sure).split(".")[0]+" dakika"

    yorum=[]
    kullanici=[]
    tarihy=[]
    listeveri=[]
    im.execute(f"SELECT metin_id,kullanici,tarih,sira,altyorum FROM yorum WHERE konu_id={id} ORDER BY sira, tarih ")
    yorumveri = im.fetchall()

    for i in yorumveri:
        yorumid = i[0]
        im.execute(f"SELECT metin FROM metin WHERE id={yorumid}")
        veri3=im.fetchall()
        yorum.append(veri3[0][0])
        listeveri.append(list(i)+list(veri3[0]))
        kullanici.append(i[1])
        tarihy.append(i[2])
    yorumsayi = len(yorumveri)

    for i in range(len(yorumveri)):
        listeveri[i][2] = tarihbul(listeveri[i][2])

    try:
        listeveri[1] = listeveri[1][:10]
    except:
        None

    im = fdb.cursor()
    im.execute(f"SELECT anahtar FROM anahtar WHERE konu_id={id}")
    anahtarlar=im.fetchall()
    anahtar=[]
    for i in anahtarlar:
        x=[]
        em = fdb.cursor()
        em.execute(f"SELECT count(anahtar) FROM anahtar WHERE anahtar='{i[0]}';")
        sayi = em.fetchall()
        x.append(i[0])
        x.append(sayi[0][0])
        anahtar.append(x)

    context={
    "metin":metin,
    "baslik":baslik,
    "tarih":tarih,
    "yazar":yazar,
    "tur":tur,
    "forum":forum,
    "sure":sure,
    "yorumsayi":yorumsayi,
    "yorumveri":listeveri,
    "id": f"{id}",
    "yorumlink": f"{id}/yorumyap1",
    "bosbirakma": request.GET.get("bosbirakma",None),
    "anahtarlar": anahtar,
    }
    return render(request, "konu.html", context)


def konuac(request):
    return render(request, "konuac.html", {"hata":request.GET.get("hata",None)})


def konuac1(request):
    kullanici = request.GET.get("kullanici","")[:16]
    baslik = request.GET.get("baslik",None)
    metin = request.GET.get("metin",None)
    tur = request.GET.get("tur",None)
    anahtar = (request.GET.get("anahtar",None)).split(",")
    kategori = request.GET.get("forum",None)

    if len(kullanici)<4 or len(baslik)<5 or len(metin)<5:
        return HttpResponseRedirect("/konuac?hata=bosbirakma")

    fdb = sql.connect('./dbs/forum.db')
    im = fdb.cursor()
    im.execute(f'INSERT INTO metin(metin) VALUES("{metin}");')
    im.execute("SELECT id FROM metin ORDER BY -id LIMIT 1;")
    id=im.fetchall()[0][0]
    im.execute(f'INSERT INTO konu(baslik,kullanici,tarih,metin_id,kategori,tur) VALUES("{baslik}","{kullanici}",DATETIME(),"{id}","{kategori}","{tur}");')
    fdb.commit()
    fdb.close()

    for i in anahtar:
        i=str(i.strip())
        fdb = sql.connect('./dbs/forum.db')
        em = fdb.cursor()
        em.execute("SELECT id FROM konu ORDER BY -id LIMIT 1;")
        id = em.fetchall()[0][0]
        im = fdb.cursor()
        im.execute(f"INSERT INTO anahtar(konu_id,anahtar) VALUES({id},'{i}');")
        fdb.commit()
        fdb.close()

    return HttpResponseRedirect("/")

def yorumyap1(request,id):
    yazar = str(request.GET.get("yazar",""))[:16]
    metin = str(request.GET.get("metin",None))


    if len(yazar)>3 and len(metin)>10:
        fdb = sql.connect('./dbs/forum.db')
        im = fdb.cursor()
        im.execute(f'SELECT count(*) FROM yorum WHERE konu_id={id} AND altyorum=0;')
        sira = int(im.fetchall()[0][0])+1
        em = fdb.cursor()
        em.execute(f'INSERT INTO metin(metin) VALUES("{metin}");')
        bm = fdb.cursor()
        bm.execute('SELECT id FROM metin ORDER BY -id LIMIT 1;')
        metin=bm.fetchall()[0][0]
        dm = fdb.cursor()
        dm.execute(f"INSERT INTO yorum(konu_id,kullanici,tarih,metin_id,sira,altyorum) VALUES({id},'{yazar}',DATETIME(),{metin},{int(sira)},0);");
        fdb.commit()
        fdb.close()
        return HttpResponseRedirect(f"/konu/{id}")
    else:
        return HttpResponseRedirect(f"/konu/{id}?bosbirakma=True#yorum-kutusu")

def yanitla(request):
    mesajid= request.GET.get("mesaj",1)
    id= request.GET.get("konu",1)

    def tarihbul(tarih):
        named_tuple = time.localtime()
        anlik = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
        sure=0
        sure+=(int(anlik[0:4])-int(tarih[0:4]))*365*24*60
        sure+=(int(anlik[5:7])-int(tarih[5:7]))*30*24*60
        sure+=(int(anlik[8:10])-int(tarih[8:10]))*24*60
        sure+=(int(anlik[11:13])-int(tarih[11:13]))*60
        sure+=(int(anlik[14:16])-int(tarih[14:16]))
        sure-=180
        if sure < 60:
            return(f"{round(sure)} dakika önce")
        elif sure < 24*60:
            return(f"{round(sure/60)} saat önce")
        elif sure < 30*24*60:
            return(f"{round(sure/(60*24))} gün önce")
        elif sure < 365*24*60:
            return(f"{round(sure/(60*24*30))} ay önce")
        else:
            return(f"{round(sure/(60*24*365))} yıl önce")

    fdb = sql.connect('./dbs/forum.db')
    im = fdb.cursor()
    im.execute(f"SELECT baslik,metin_id,kullanici,tarih,tur,kategori FROM konu WHERE id={id}")
    veri=im.fetchall()[0]
    baslik=veri[0]
    metin_id=veri[1]
    yazar=veri[2]
    tarih=tarihbul(veri[3])
    tur=veri[4]
    forum=veri[5]
    im.execute(f"SELECT metin FROM metin WHERE id={metin_id}")
    metin=im.fetchall()[0][0]
    sure=len(metin)/800
    if sure<1:
        sure=str(sure*60).split(".")[0]+" saniye"
    else:
        sure=str(sure).split(".")[0]+" dakika"

    yorum=[]
    kullanici=[]
    tarihy=[]
    listeveri=[]
    im.execute(f"SELECT metin_id,kullanici,tarih,sira,altyorum FROM yorum WHERE konu_id={id} AND sira={mesajid} ORDER BY sira, tarih ")
    yorumveri = im.fetchall()

    for i in yorumveri:
        yorumid = i[0]
        im.execute(f"SELECT metin FROM metin WHERE id={yorumid}")
        veri3=im.fetchall()
        yorum.append(veri3[0][0])
        listeveri.append(list(i)+list(veri3[0]))
        kullanici.append(i[1])
        tarihy.append(i[2])
    yorumsayi = len(yorumveri)

    for i in range(len(yorumveri)):
        listeveri[i][2] = tarihbul(listeveri[i][2])

    try:
        listeveri[1] = listeveri[1][:10]
    except:
        None

    context={
    "metin":metin,
    "baslik":baslik,
    "tarih":tarih,
    "yazar":yazar,
    "tur":tur,
    "forum":forum,
    "sure":sure,
    "yorumsayi":yorumsayi,
    "yorumveri":listeveri,
    "id": f"{id}",
    "yorumlink": f"konu/{id}/yorumyap1/{mesajid}",
    "bosbirakma": request.GET.get("bosbirakma",None)
    }
    return render(request, "konu.html", context)

def yanityap1(request,id,sira):
    yazar = str(request.GET.get("yazar",""))[:16]
    metin = str(request.GET.get("metin",None))

    if len(yazar)>3 and len(metin)>20:
        fdb = sql.connect('./dbs/forum.db')
        em = fdb.cursor()
        em.execute(f'INSERT INTO metin(metin) VALUES("{metin}");')
        bm = fdb.cursor()
        bm.execute('SELECT id FROM metin ORDER BY -id LIMIT 1;')
        metin=bm.fetchall()[0][0]
        dm = fdb.cursor()
        dm.execute(f"INSERT INTO yorum(konu_id,kullanici,tarih,metin_id,sira,altyorum) VALUES({id},'{yazar}',DATETIME(),{metin},{sira},1);");
        fdb.commit()
        fdb.close()
        return HttpResponseRedirect(f"/konu/{id}#{sira}")
    else:
        return HttpResponseRedirect(f"/konu/{id}?bosbirakma=True#yorum-kutusu")


def kaydol(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('')
    else:
        form = SignUpForm()
    return render(request, 'kaydol.html', {'form': form})
