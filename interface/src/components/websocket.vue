<template>
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div class="w-full max-w-md p-6 bg-white rounded-lg shadow-md">
        <h1 class="text-2xl font-semibold text-center text-gray-700">Sensor Dashboard</h1>
        
        <div class="mt-4 mb-4 h-48 overflow-y-auto bg-gray-50 p-4 rounded border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700">Sensors</h2>
          <ul>
            <li v-for="(sensor, index) in sensors" :key="index" class="text-gray-600">
              <h1>{{ sensor['serial'] }}</h1>
            </li>
          </ul>
        </div>
  
        <div class="mt-4 mb-4 h-24 overflow-y-auto bg-red-50 p-4 rounded border border-red-200">
          <h2 class="text-xl font-semibold text-red-700">Security Notifications</h2>
          <ul>
            <li v-for="(notification, index) in notifications" :key="index" class="text-red-600">
              {{ notification }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { io } from "socket.io-client";
  
  export default {
    name: "websocketTest",
    data() {
      return {
        socket: null,
        sensors: [],
        notifications: [],
      };
    },
    mounted() {
      // Connect to the WebSocket server
      this.socket = io(`http://${this.$apiIp}:5000`);

  
      // Listen for sensor data from the server
      this.socket.on('sensor_data', (data) => {
        console.log(data)
        this.sensors = data.sensors;
      });
  
      // Listen for security notifications
      this.socket.on('security_notification', (msg) => {
        this.notifications.push(msg.message);
      });
  
      // Handle connection event
      this.socket.on("connect", () => {
        console.log("Connected to WebSocket server");
      });
  
      // Handle disconnection event
      this.socket.on("disconnect", () => {
        console.log("Disconnected from WebSocket server");
      });
    },
    beforeUnmount() {
      // Clean up the socket connection when the component is destroyed
      if (this.socket) {
        this.socket.disconnect();
      }
    },
  };
  </script>
  
  <style scoped>
  /* Add any additional styling here if necessary */
  </style>
  