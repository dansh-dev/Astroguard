<template>
  <div id="map" class="h-96 z-0"></div>
</template>

<script>
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

export default {
  name: 'MapView',
  props: {
    sensors: {
      type: Array,
      required: true
    }
  },
  mounted() {
    const map = new maplibregl.Map({
      container: 'map',
      style: {
        version: 8,
        sources: {
          'osm-tiles': {
            type: 'vector',
            tiles: [`http://${this.$apiIp}:8000/data/osm/{z}/{x}/{y}.pbf`],
            maxzoom: 14
          }
        },
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: { 'background-color': '#dcedff' }
          },
          {
            id: 'landcover',
            type: 'fill',
            source: 'osm-tiles',
            'source-layer': 'landcover',
            paint: { 'fill-color': '#21a179' }
          },
          {
            id: 'boundary',
            type: 'line',
            source: 'osm-tiles',
            'source-layer': 'boundary',
            paint: {
              'line-color': '#21a179',
              'line-width': 2
            }
          },
          {
            id: 'water',
            type: 'fill',
            source: 'osm-tiles',
            'source-layer': 'water',
            paint: { 'fill-color': '#3188e4' }
          },
          {
            id: 'landuse',
            type: 'fill',
            source: 'osm-tiles',
            'source-layer': 'landuse',
            paint: { 'fill-color': '#156149' }
          },
          {
            id: 'buildings',
            type: 'fill-extrusion',
            source: 'osm-tiles',
            'source-layer': 'building',
            paint: {
              'fill-extrusion-color': '#acacac',
              'fill-extrusion-height': ['get', 'render_height'],
              'fill-extrusion-base': ['get', 'render_min_height'],
              'fill-extrusion-opacity': 0.9
            }
          },
          {
            id: 'roads',
            type: 'line',
            source: 'osm-tiles',
            'source-layer': 'transportation',
            paint: {
              'line-color': '#535353',
              'line-width': 2
            }
          }
        ]
      },
      center: [14.45095, 35.8822], // Coordinates for Malta
      zoom: 12 
    });

    console.log(this.sensors)
    this.sensors.forEach(sensor => {
      console.log(sensor['Latitude'])
      new maplibregl.Marker()
        .setLngLat({lat: sensor['Latitude'], lng: sensor['Longitude']})
        .setPopup(new maplibregl.Popup().setHTML(`
          <h3>Sensor: ${sensor.SerialNumber}</h3>
          <p>Alarm State: ${sensor.AlarmState}</p>
          <p>Tamper State: ${sensor.TamperState}</p>
          <p>Charge: ${sensor.Charge}%</p>
          <p>Signal Strength: ${sensor.SignalStrength}</p>
          <p>Timestamp: ${new Date(sensor.Timestamp).toLocaleString()}</p>
        `))
        .addTo(map);
    });

    map.on('load', function () {
      console.log('Map loaded');
    });

    map.on('error', function (e) {
      console.error('Map error:', e);
    });
  }
};
</script>

<style></style>
