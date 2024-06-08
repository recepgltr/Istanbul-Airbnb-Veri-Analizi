import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import st_folium
from datetime import datetime

st.title('İstanbul Airbnb')

# Veri yükleme
temiz_veri2 = pd.read_csv(r"https://raw.githubusercontent.com/recepgltr/Istanbul-Airbnb-Veri-Analizi/main/temiz_veri2.csv")

# İlçelerin listesi
neighbourhoods = [
    "Adalar", "Arnavutkoy", "Atasehir", "Avcilar", "Bagcilar", "Bahcelievler", "Bakirkoy", 
    "Basaksehir", "Bayrampasa", "Besiktas", "Beykoz", "Beylikduzu", "Beyoglu", "Buyukcekmece", 
    "Catalca", "Cekmekoy", "Esenler", "Esenyurt", "Eyup", "Fatih", "Gaziosmanpasa", "Gungoren", 
    "Kadikoy", "Kagithane", "Kartal", "Kucukcekmece", "Maltepe", "Pendik", "Sancaktepe", 
    "Sariyer", "Silivri", "Sile", "Sisli", "Sultanbeyli", "Sultangazi", "Tuzla", "Umraniye", 
    "Uskudar", "Zeytinburnu"
]

# Sidebar'da ilçe seçimi
selected_neighbourhood = st.sidebar.selectbox("Bir ilçe seçin", neighbourhoods)

# Seçilen ilçeye ait verileri filtreleme
filtered_data = temiz_veri2[temiz_veri2["neighbourhood"] == selected_neighbourhood]

# Mevcut oda türlerini belirleme
room_types = filtered_data['room_type'].unique().tolist()

# Sidebar'da oda türü seçimi
selected_room_type = st.sidebar.selectbox("Bir oda türü seçin", room_types)

# Seçilen oda türüne göre verileri filtreleme
filtered_data = filtered_data[filtered_data["room_type"] == selected_room_type]

if filtered_data.empty:
    st.write("Seçtiğiniz kriterlere uygun veri bulunmamaktadır.")
else:
    # Sidebar'da fiyat aralığı seçimi
    min_price = int(filtered_data['price'].min())
    max_price = int(filtered_data['price'].max())

    if min_price == max_price:
        st.sidebar.write(f"Tüm evlerin fiyatı {min_price} olduğu için fiyat aralığı seçimi yapılamamaktadır.")
        price_range = (min_price, max_price)
    else:
        price_range = st.sidebar.slider(
            "Fiyat aralığını seçin",
            min_price,
            max_price,
            (min_price, max_price)
        )

    # Seçilen fiyat aralığına göre verileri filtreleme
    filtered_data = filtered_data[(filtered_data['price'] >= price_range[0]) & 
                                  (filtered_data['price'] <= price_range[1])]

    # Sidebar'da tarih aralığı seçimi
    start_date = st.sidebar.date_input("Başlangıç tarihi", datetime.now())
    end_date = st.sidebar.date_input("Bitiş tarihi", datetime.now())

    if start_date > end_date:
        st.sidebar.error("Başlangıç tarihi bitiş tarihinden sonra olamaz")
    else:
        # Seçilen tarih aralığındaki gün sayısını hesaplama
        num_days = (end_date - start_date).days + 1

        # Toplam fiyatı hesaplama
        filtered_data['total_price'] = filtered_data['price'] * num_days

        # Toplam fiyatı sidebar'da gösterme
        st.sidebar.write(f"Seçilen tarih aralığında toplam gün sayısı: {num_days}")
        st.sidebar.write(f"Fiyat aralığına göre toplam fiyatlar güncellendi.")

        # Harita oluşturma
        map_center = [filtered_data['latitude'].mean(), filtered_data['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=12)

        # Pop-up'lar ile işaretleyiciler ekleme
        for idx, row in filtered_data.iterrows():
            popup_html = f"""
                <div>
                    <h4>{row['name']}</h4>
                    <p><b>Oda Türü:</b> {row['room_type']}</p>
                    <p><b>Fiyat:</b> ₺{row['price']} / gece</p>
                    <p><b>Toplam Fiyat:</b> ₺{row['total_price']} / {num_days} gece</p>
                    <p><a href="https://www.airbnb.com.tr/s/Istanbul--Turkey/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-07-01&monthly_length=3&monthly_end_date=2024-10-01&price_filter_input_type=2&channel=EXPLORE&query=Istanbul%2C%20Turkey&place_id=ChIJawhoAASnyhQR0LABvJj-zOE&location_bb=QiTMBUHrbjFCIz7hQeTDsg%3D%3D&date_picker_type=calendar&source=structured_search_input_header&search_type=autocomplete_click" target="_blank">Daha fazla bilgi için tıklayın</a></p>
                </div>
            """
            iframe = folium.IFrame(html=popup_html, width=300, height=200)
            popup = folium.Popup(iframe, max_width=300)
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup
            ).add_to(m)

        # Haritayı gösterme
        st_folium(m, width=800, height=600)
ortalama_fiyatlar = temiz_veri2.groupby('neighbourhood')['price'].mean().reset_index()

# Sütun grafiği şeklinde göster
ortalama_fiyatlar.plot(kind='bar', x='neighbourhood', y='price', figsize=(12, 6), legend=None)
plt.title('İlçelere Göre Ortalama Fiyatlar')
plt.xlabel('İlçe')
plt.ylabel('Ortalama Fiyat (TL)')
plt.xticks(rotation=90)
plt.show()
