import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import st_folium
from datetime import datetime
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

# Veri yükleme
temiz_veri2 = pd.read_csv(r"C:\Users\recep\Desktop\VERİ BİLİMİ\listings1.csv")

# Ayrık değerleri çıkarma
Q1 = temiz_veri2['price'].quantile(0.25)
Q3 = temiz_veri2['price'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

temiz_veri2 = temiz_veri2[(temiz_veri2['price'] >= lower_bound) & (temiz_veri2['price'] <= upper_bound)]

# Özellik ve hedef değişkenler
X = temiz_veri2[['latitude', 'longitude', 'room_type', 'minimum_nights', 'availability_365']]  # Özellikler
y = temiz_veri2['price']  # Hedef değişken

# Kategorik verileri sayısal verilere dönüştürme
X = pd.get_dummies(X, columns=['room_type'], drop_first=True)

# Model oluşturma ve eğitme
model = LinearRegression()
model.fit(X, y)

# Modeli kaydetme
joblib.dump(model, 'airbnb_price_prediction_model.pkl')

# Streamlit uygulaması
st.title('İstanbul Airbnb')

# İlçelerin listesi
neighbourhoods = temiz_veri2['neighbourhood'].unique().tolist()
selected_neighbourhood = st.sidebar.selectbox("Bir ilçe seçin", neighbourhoods)

# Seçilen ilçeye ait verileri filtreleme
filtered_data = temiz_veri2[temiz_veri2["neighbourhood"] == selected_neighbourhood]

if filtered_data.empty:
    st.write("Seçtiğiniz ilçede uygun veri bulunmamaktadır.")
else:
    # Fiyat aralığı seçme
    min_price = int(filtered_data['price'].min())
    max_price = int(filtered_data['price'].max())
    price_range = st.sidebar.slider(
        "Fiyat aralığını seçin",
        min_price,
        max_price,
        (min_price, max_price)
    )

    # Tarih aralığı seçme
    start_date = st.sidebar.date_input("Başlangıç tarihi", datetime.now())
    end_date = st.sidebar.date_input("Bitiş tarihi", datetime.now())

    if start_date > end_date:
        st.sidebar.error("Başlangıç tarihi bitiş tarihinden sonra olamaz")
    else:
        # Seçilen fiyat aralığına göre verileri filtreleme
        filtered_data = filtered_data[(filtered_data['price'] >= price_range[0]) & 
                                      (filtered_data['price'] <= price_range[1])]

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

        # Makine öğrenmesi modelini yükleme
        try:
            model = joblib.load('airbnb_price_prediction_model.pkl')
        except FileNotFoundError:
            st.error("Model dosyası bulunamadı. Lütfen dosya yolunu kontrol edin.")
            st.stop()

        # Gelecek yıl için tahmin yapma
        X_new = filtered_data[['latitude', 'longitude', 'room_type', 'minimum_nights', 'availability_365']]
        X_new = pd.get_dummies(X_new, columns=['room_type'], drop_first=True)

        # Tahmin işlemi
        future_prices = model.predict(X_new)

        # Geçmiş yılın fiyatını elde etme
        past_prices = filtered_data['price']

        # Fiyat artış yüzdesini hesaplama
        price_increase_percentage = ((future_prices - past_prices) / past_prices) * 100

        # Tahmin edilen fiyatları ve fiyat artış yüzdesini veriye ekleme
        filtered_data['previous_year_price'] = past_prices
        filtered_data['predicted_price_next_year'] = future_prices
        filtered_data['price_increase_percentage'] = price_increase_percentage

        st.write(filtered_data[['name', 'latitude', 'longitude', 'price', 'previous_year_price', 'predicted_price_next_year', 'price_increase_percentage']])
