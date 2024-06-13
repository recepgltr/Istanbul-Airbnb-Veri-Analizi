import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

# Veri yükleme
temiz_veri2 = pd.read_csv("https://raw.githubusercontent.com/recepgltr/Istanbul-Airbnb-Veri-Analizi/main/deneme1.csv")

# Ayrık değerleri çıkarma
Q1 = temiz_veri2['price'].quantile(0.25)
Q3 = temiz_veri2['price'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

temiz_veri2 = temiz_veri2[(temiz_veri2['price'] >= lower_bound) & (temiz_veri2['price'] <= upper_bound)]

# Enflasyon oranını ekleme (örnek olarak %126 eklenmiştir)
temiz_veri2['inflation_rate'] = 1,26  # %126 enflasyon oranı

# Özellik ve hedef değişkenler
X = temiz_veri2[['latitude', 'longitude', 'room_type', 'minimum_nights', 'availability_365', 'inflation_rate']]
y = temiz_veri2['price']

# Kategorik verileri sayısal verilere dönüştürme
X = pd.get_dummies(X, columns=['room_type'], drop_first=True)

# Model oluşturma ve eğitme
model = LinearRegression()
model.fit(X, y)

# Modeli kaydetme
joblib.dump(model, 'airbnb_price_prediction_model_with_inflation.pkl')
import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import st_folium
from datetime import datetime
import joblib

# Veri yükleme
temiz_veri2 = pd.read_csv("https://raw.githubusercontent.com/recepgltr/Istanbul-Airbnb-Veri-Analizi/main/deneme1.csv")

# Ayrık değerleri çıkarma
Q1 = temiz_veri2['price'].quantile(0.25)
Q3 = temiz_veri2['price'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

temiz_veri2 = temiz_veri2[(temiz_veri2['price'] >= lower_bound) & (temiz_veri2['price'] <= upper_bound)]

# Enflasyon oranını ekleme (örnek olarak %75 eklenmiştir)
temiz_veri2['inflation_rate'] = 0.75  # %75 enflasyon oranı

# Streamlit uygulaması
st.title('İstanbul Airbnb')
neighbourhoods = [
    "Adalar", "Arnavutkoy", "Atasehir", "Avcilar", "Bagcilar", "Bahcelievler", "Bakirkoy", 
    "Basaksehir", "Bayrampasa", "Besiktas", "Beykoz", "Beylikduzu", "Beyoglu", "Buyukcekmece", 
    "Catalca", "Cekmekoy", "Esenler", "Esenyurt", "Eyup", "Fatih", "Gaziosmanpasa", "Gungoren", 
    "Kadikoy", "Kagithane", "Kartal", "Kucukcekmece", "Maltepe", "Pendik", "Sancaktepe", 
    "Sariyer", "Silivri", "Sile", "Sisli", "Sultanbeyli", "Sultangazi", "Tuzla", "Umraniye", 
    "Uskudar", "Zeytinburnu"
]

selected_neighbourhood = st.sidebar.selectbox("Bir ilçe seçin", neighbourhoods)

filtered_data = temiz_veri2[temiz_veri2["neighbourhood"] == selected_neighbourhood]

room_types = filtered_data['room_type'].unique().tolist()
selected_room_type = st.sidebar.selectbox("Bir oda türü seçin", room_types)
filtered_data = filtered_data[filtered_data["room_type"] == selected_room_type]

if filtered_data.empty:
    st.write("Seçtiğiniz ilçede uygun veri bulunmamaktadır.")
else:
    min_price = int(filtered_data['price'].min())
    max_price = int(filtered_data['price'].max())
    price_range = st.sidebar.slider(
        "Fiyat aralığını seçin",
        min_price,
        max_price,
        (min_price, max_price)
    )

    start_date = st.sidebar.date_input("Başlangıç tarihi", datetime.now())
    end_date = st.sidebar.date_input("Bitiş tarihi", datetime.now())

    if start_date > end_date:
        st.sidebar.error("Başlangıç tarihi bitiş tarihinden sonra olamaz")
    else:
        filtered_data = filtered_data[(filtered_data['price'] >= price_range[0]) & 
                                      (filtered_data['price'] <= price_range[1])]

        num_days = (end_date - start_date).days + 1
        filtered_data['total_price'] = filtered_data['price'] * num_days

        st.sidebar.write(f"Seçilen tarih aralığında toplam gün sayısı: {num_days}")
  
        map_center = [filtered_data['latitude'].mean(), filtered_data['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=12)

        # Pop-up'ların rengini fiyatına göre belirleme
        def get_color(price):
            if price < 200:
                return 'green'
            elif 200 <= price < 400:
                return 'blue'
            elif 400 <= price < 600:
                return 'orange'
            else:
                return 'red'

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
                popup=popup,
                icon=folium.Icon(color=get_color(row['price']))
            ).add_to(m)

        st_folium(m, width=800, height=600)

        try:
            model = joblib.load('airbnb_price_prediction_model_with_inflation.pkl')
        except FileNotFoundError:
            st.error("Model dosyası bulunamadı. Lütfen dosya yolunu kontrol edin.")
            st.stop()

        X_new = filtered_data[['latitude', 'longitude', 'room_type', 'minimum_nights', 'availability_365', 'inflation_rate']]
        X_new = pd.get_dummies(X_new, columns=['room_type'], drop_first=True)
        if X_new.empty:
            st.error("Filtreleme sonucunda tahmin yapılacak veri bulunamadı.")
            st.stop()
        if 'room_type_Private room' not in X_new.columns:
            X_new['room_type_Private room'] = 0
        if 'room_type_Shared room' not in X_new.columns:
            X_new['room_type_Shared room'] = 0

        st.title('Gelecek Yılki Fiyat Tahmini')
        future_prices = model.predict(X_new)
        past_prices = filtered_data['price']
        price_increase_percentage = ((future_prices - past_prices) / past_prices) * 100

        filtered_data['previous_year_price'] = past_prices
        filtered_data['predicted_price_next_year'] = future_prices
        filtered_data['price_increase_percentage'] = price_increase_percentage

        st.write(filtered_data[['name', 'latitude', 'longitude', 'price', 'previous_year_price', 'predicted_price_next_year', 'price_increase_percentage']])
