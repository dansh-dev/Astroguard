<template>
  <div class="astroguard-setup-screen w-full">
    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
      <div class="w-full justify-center items-center flex">
        <div class="flex justify-center items-center w-full md:w-auto text-astro-guard-white"></div>
        <img class="w-80" :src="logo" alt="Logo" />
      </div>
    </div>
    <div v-if="sensor" class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container text-astro-guard-white">
      <h2 class="text-xl font-bold mb-4">Sensor Details ({{ sensor.SerialNumber }})</h2>
      <ul class="list-disc pl-5">
        <li><strong>Location:</strong> Latitude:{{ sensor.Latitude }} Longitude: {{ sensor.Longitude }}</li>
        <li><strong>Alarm State:</strong> {{ sensor.AlarmState }}</li>
        <li><strong>Tamper State:</strong> {{ sensor.TamperState }}</li>
        <li><strong>Charge:</strong> {{ sensor.Charge }}%</li>
        <li><strong>Signal Strength:</strong> {{ sensor.SignalStrength }} dBm</li>
        <li><strong>Timestamp:</strong> {{ sensor.Timestamp }}</li>
      </ul>
      <h2 class="text-xl font-bold mb-4">Map view for ({{ sensor.SerialNumber }}):</h2>
      <MapView v-if="sensor" :sensors="sensorArr" class="w-full rounded-xl" />
      <button @click="this.$router.push('/SensorList');" class="text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">Back</button>
    </div>
    <div v-if="camera" class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container text-astro-guard-white">
      <h2 class="text-xl font-bold mb-4">Camera Details ({{ camera.SerialNumber }})</h2>
      <ul class="list-disc pl-5">
        <li><strong>Last Object Detected:</strong> {{ camera.Label }}</li>
        <li><strong>Location:</strong> Latitude:{{ camera.Latitude }} Longitude: {{ camera.Longitude }}</li>
        <li><strong>Charge:</strong> {{ camera.Charge }}%</li>
        <li><strong>Signal Strength:</strong> {{ camera.SignalStrength }} dBm</li>
        <li><strong>Timestamp:</strong> {{ camera.Timestamp }}</li>
      </ul>

      <!-- Label Selection Section -->
      <h2 class="text-xl font-bold mb-4">Allowed Labels</h2>
      <div v-if="cameraSetup && cameraSetup.AllowedLabels && cameraSetup.AllowedLabels.length > 0">
        <div v-for="label in totalSelectableLabels" :key="label" class="flex items-center mb-2">
          <input type="checkbox" :value="label" v-model="selectedLabels" class="mr-2"/>
          <label>{{ label }}</label>
        </div>
        <button @click="saveSetup" class="text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">Save</button>
      </div>

      <h2 class="text-xl font-bold mb-4">Map view for ({{ camera.SerialNumber }}):</h2>
      <MapView v-if="camera" :sensors="cameraArr" class="w-full rounded-xl" />

      <button @click="this.$router.push('/SensorList');" class="text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">Back</button>
    </div>
  </div>
</template>

<script setup>
import logo from '@/assets/astroguard-logo.png';
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { io } from 'socket.io-client';
import axios from 'axios';
import MapView from './MapView.vue';

const sensor = ref(null);
const camera = ref(null);
const cameraSetup = ref(null);
const selectedLabels = ref([]);
const totalSelectableLabels = ['person', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
const sensors = ref([]);
const cameras = ref([]);
const sensorArr = [];
const cameraArr = [];
const route = useRoute();
const serialNumber = route.params.serialNumber;
let socket = null;

onMounted(() => {
  // Fetch camera setup from the Flask server
  axios.post(`http://${this.$apiIp}:5000/getCamSetup`, {
    SerialNumber: serialNumber
  }, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    cameraSetup.value = response.data || {};
    // Initialize selectedLabels with all allowed labels
    if (cameraSetup.value.AllowedLabels) {
      selectedLabels.value = [...cameraSetup.value.AllowedLabels];
    }
    console.log(selectedLabels.value)
  })
  .catch(error => {
    console.error('Error fetching camera setup:', error);
  });

  // WebSocket connection for real-time data
  socket = io(`http://${this.$apiIp}:5000`);

  // Handle connection event
  socket.on("connect", () => {
    console.log("Connected to WebSocket server");
  });

  // Receive sensor data from WebSocket
  socket.on("sensor_data", (data) => {
    sensors.value = data.sensors;
    // Find the sensor by serial number
    sensor.value = sensors.value.find(s => s.SerialNumber === serialNumber);
    sensorArr.push(sensor.value);

    if (sensor.value) {
      console.log("Sensor found:", sensor.value);
    } else {
      console.log("No sensor found with Serial Number:", serialNumber);
    }
  });

  socket.on("cctv_data", (data) => {
    cameras.value = data.cameras;
    // Find the camera by serial number
    camera.value = cameras.value.find(s => s.SerialNumber === serialNumber);
    cameraArr.push(camera.value);

    if (camera.value) {
      console.log("Camera found:", camera.value);
    } else {
      console.log("No camera found with Serial Number:", serialNumber);
    }
  });

  // Handle disconnection event
  socket.on("disconnect", () => {
    console.log("Disconnected from WebSocket server");
  });
});

onUnmounted(() => {
  if (socket) {
    socket.disconnect();
    console.log("Socket connection closed");
  }
});

// Save the updated camera setup
function saveSetup() {
  const updatedSetup = {
    ...cameraSetup.value,
    AllowedLabels: selectedLabels.value,
  };

  axios.post('http://'+this.$apiIp+':5000/UpdateCamConfig', updatedSetup, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('Setup updated successfully:', response.data);
    window.location.reload()
  })
  .catch(error => {
    console.error('Error updating setup:', error);
  });
}
</script>
