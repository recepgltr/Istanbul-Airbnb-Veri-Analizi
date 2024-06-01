import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import st_folium

st.title('İstanbul Airbnb')

# Veri yükleme
temiz_veri2 = pd.read_csv(r"C:\Users\recep\Desktop\VERİ BİLİMİ\temiz_veri2.csv")

# İlçelerin listesi (baş harflerine göre sıralanmış)
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

    # Harita oluşturma
    map_center = [filtered_data['latitude'].mean(), filtered_data['longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=12)

    # Pop-up'lar ile işaretleyiciler ekleme
    for idx, row in filtered_data.iterrows():
        popup_html = f"""
            <div>
                <h4>{row['name']}</h4>
                <p><b>Oda Türü:</b> {row['room_type']}</p>
                <p><b>Fiyat:</b> ${row['price']} / gece</p>
                <p><a href="https://www.airbnb.com/rooms/{row['id']}" target="_blank">Daha fazla bilgi için tıklayın</a></p>
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
