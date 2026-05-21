import io
import folium
import os

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
import pandas as pd

from folium.plugins import FastMarkerCluster

CALLBACK = '''
            function (row) {
                var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "red", label: "myTest"});
                var icon = L.AwesomeMarkers.icon({
                    icon: 'info-sign',
                    iconColor: 'white',
                    markerColor: 'green',
                    prefix: 'glyphicon',
                    extraClasses: 'fa-rotate-0'
                    });
            marker.setIcon(icon);
            var popup = L.popup({maxWidth: "300"});
            const display_text = {text: row[2]};
            var mytext = L.DomUtil.create("div", "display_text");
            mytext.textContent = display_text.text;           

            const myNewText = "<b>" + {text: row[2]}.text + "</b><br>" + {text: row[3]}.text + "<br>" + "Posted on: " + {text: row[4]}.text;

            popup.setContent(myNewText);
            marker.bindPopup(popup);
            return marker};
'''


class CustomMapView(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, data={}):
        super().__init__()

        self.data = self.processData(data)
        self.map = self.fastMapBuilder()

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())

    def processData(self, data):
        studioInfo = pd.read_csv(os.path.join('src', 'utils', 'studioData.csv'))
        out = data.merge(studioInfo, on=['Studio', 'City', 'Country'], how='left').fillna(0)
        out['info'] = out.apply(lambda row: f"{row.Studio} - {row['Job Title']}", axis=1)
        return out
    
    def fastMapBuilder(self):
        f = folium.Figure(width=1000, height=500)
        map = folium.Map(location=[37, -102], tiles="Cartodb Positron", max_bounds=True,
        zoom_start=1.5, min_zoom=2).add_to(f)

        map.add_child(FastMarkerCluster(self.data[[ 'Latitude', 'Longitude', 'info', 'Source/Contact', 'Date']].values.tolist(), callback=CALLBACK))
        return map


if __name__ == "__main__":
    pass



