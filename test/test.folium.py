import folium

# Center on the Senate of Rome
Map = folium.Map(location=[41.892929, 12.485366],zoom_start=4.5)

Map.save("test.html")