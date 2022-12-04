import numpy as np
import pandas as pd
import datetime as dt
pd.set_option("display.max_columns",None)
pd.set_option("display.float_format",lambda x: "%.3f" % x)

#flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz.

df=pd.read_csv("flo_data_20k.csv")
df.head()


#Veri setinde
#a. İlk 10 gözlem,
df.head(10)

#b. Değişken isimleri,

df.columns
#c. Betimsel istatistik,

df.describe()
#d. Boş değer,
df.isnull().sum()
#e. Değişken tipleri, incelemesi yapınız.

df.dtypes

#Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Her bir müşterinin toplam
#alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df["totalCV"]=df["customer_value_total_ever_offline"]+df["customer_value_total_ever_online"]
df["totalordernum"]=df["order_num_total_ever_offline"]+df["order_num_total_ever_offline"]

#Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

df.dtypes

df.head()

for i in df.columns:
    if "date" in i:
        df[i]=df[i].astype("datetime64")

#Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.

df.groupby("order_channel").agg({"master_id":"count",
                                 "totalordernum":"sum",
                                 "totalCV":"sum"})

#En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

df.sort_values("totalCV",ascending=False).head(10)["master_id"]

#En fazla siparişi veren ilk 10 müşteriyi sıralayınız.

df.sort_values("totalordernum",ascending=False).head(10)["master_id"]


#veri ön hazırlık sürecini fonksiyonlaştırınız

def onhazirlik(df):
    df["totalCV"]=df["customer_value_total_ever_offline"]+df["customer_value_total_ever_online"]
    df["totalordernum"]=df["order_num_total_ever_offline"]+df["order_num_total_ever_offline"]
    for i in df.columns:
        if "date" in i:
            df[i]=df[i].astype("datetime64")

    return(df)

onhazirlik(df)

df.head()
df.info()

#RFM METRİKLERİNİN HESAPLANMASI



#recency=son alışveriş yaptığı günden bugune kadar olan süre
#frequency=bir müşterinin toplam yaptığı alşveriş sayısı
#monetary=Bir müşterinin yaptığı toplam harcama


#Müşteri özelinde Recency, Frequency ve Monetary metriklerini hesaplayınız.

todaydate=dt.datetime(2022,11,12)


#Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
rfm=df.groupby("master_id").agg({"last_order_date":lambda x: todaydate-x.max(),
                             "totalordernum":lambda y:y.sum(),
                             "totalCV":lambda z:z.sum()})

#Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.
rfm.columns=["recency","frequency","monetary"]
rfm.head()

#: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
rfm["recency_score"]=pd.qcut(rfm["recency"],5,labels=[5,4,3,2,1])
rfm["frequency_score"]=pd.qcut(rfm["frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
rfm["monetary_score"]=pd.qcut(rfm["monetary"],5,labels=[1,2,3,4,5])
rfm


 # recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.

rfm["RFScore"]=rfm["recency_score"].astype("str")+rfm["frequency_score"].astype("str")
rfm



#Oluşturulan RF skorları için segment tanımlamaları yapınız.
seg_map={
    r"[1-2][1-2]":"hibernating",
    r"[1-2][3-4]":"at_risk",
    r"[1-2]5":"cant_loose",
    r"3[1-2]":"about to sleep",
    r"33":"need_attention",
    r"[3-4][4-5]":"loyal_customers",
    r"41":"promising",
    r"51":"new_customers",
    r"[4-5][2-3]":"potential_loyalists",
    r"5[4-5]" : "champions"
}

#Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz

rfm["segment"]=rfm["RFScore"].replace(seg_map,regex=True)
rfm

#Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.

rfm.describe().T
rfm[["segment","frequency","recency","monetary"]].groupby("segment").agg(["mean","count"])
#RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz

#champions,loyal_customers,kadın kategorisini bulup csv olarak kaydediniz.

new_df=df[(df["interested_in_categories_12"]).str.contains("KADIN")]
new_rfm=rfm[(rfm["segment"]=="loyal_customers")|(rfm["segment"]=="champions")]
finalrfm1=new_df.merge(new_rfm,on="master_id",how="left")

finalrfm1.dropna()
finalrfm1.to_csv("finalrfm1.csv")

#cant_loose,hibernating ve new_Customers müşterilerin idlerini bulup csv dosyası olarak kaydediniz.
new2_df=df[(df["interested_in_categories_12"]).str.contains("ERKEK","COCUK")]
new2_rfm=rfm[(rfm["segment"]=="cant_loose")|(rfm["segment"]=="hibernating")|(rfm["segment"]=="new_customers")]
finalrfm2=new2_df.merge(new2_rfm,on="master_id",how="left")
finalrfm2.dropna()
finalrfm2.to_csv("finalrfm2.csv")






