<template>
    <div class="astroguard-setup-screen w-full">
      <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container ">

        <div class="w-full justify-center items-center flex">
          <div class="flex justify-center items-center w-full md:w-auto text-astro-guard-white">
          </div>
          <img class="w-80" :src="logo" alt="Logo" />
          
        </div>
        
</div>
<div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
  <h1 class="text-astro-guard-white text-2xl font-AXIS">Sensor List</h1>
  <div class="w-full overflow-y-scroll">
    
              
              <!-- Sensor List Content -->
              <div v-for="(sensor, index) in sensors" :key="index" class="my-1 border p-4 text-astro-guard-white rounded-xl w-full">
              
              <h1 class="font-JosefinSans">Serial Number: {{ sensor['SerialNumber']}}</h1>
              <h1 class="font-JosefinSans">Last update: {{ sensor['Timestamp']}}</h1>
              <h1 class="font-JosefinSans">Currently Triggered: {{ sensor['AlarmState']}}</h1>
              <div class="w-full items-end justify-end flex">
                        <button @click="showSensorDetails(sensor['SerialNumber'])"
                            class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-xl hover:bg-astro-guard-green">Details</button>
                    </div>
            </div>
  </div>
</div>
<div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
  <h1 class="text-astro-guard-white text-2xl font-AXIS">Camera List</h1>
  <div class="w-full overflow-y-scroll">
    
              
              <!-- Sensor List Content -->
              <div v-for="(camera, index) in cameras" :key="index" class="my-1 border p-4 text-astro-guard-white rounded-xl w-full">
              
              <h1 class="font-JosefinSans">Serial Number: {{ camera['SerialNumber']}}</h1>
              <h1 class="font-JosefinSans">Last update: {{ camera['Timestamp']}}</h1>
              <h1 class="font-JosefinSans">Recently Detected: {{ camera['Label']}}</h1>
              <div class="w-full items-end justify-end flex">
                        <button @click="showSensorDetails(camera['SerialNumber'])"
                            class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-xl hover:bg-astro-guard-green">Details</button>
                    </div>
            </div>
  </div>
</div>

      <NavBar />
    </div>
  </template>
  
  <script>
  import logo from '@/assets/astroguard-logo.png';
  import NavBar from './NavBar.vue';
  import { io } from "socket.io-client";
  export default {
    name: 'SensorList',
    components: {
      NavBar
    },
    data() {
      return {
        logo,
        sensors: [],
        cameras: [],
        inactivityTimeout: null, // This will hold our timeout reference
        inactivityTime: 300000,  // 5 minutes in milliseconds
      };
    },
    methods: {
      showSensorDetails(serialNumber) {
        this.$router.push({ name: 'SensorDetails', params: { serialNumber } });
      },
      resetInactivityTimer() {
      // Clear the existing timeout
      clearTimeout(this.inactivityTimeout);

      // Start a new timeout
      this.inactivityTimeout = setTimeout(this.triggerInactiveAction, this.inactivityTime);
    },
    triggerInactiveAction() {
      // This function will be triggered after 5 minutes of inactivity

      this.$router.push('/main');
      // Add your custom logic here
    },
    handleUserActivity() {
      // Reset the inactivity timer on any user activity
      this.resetInactivityTimer();
    },
  },
  mounted() {
    // Listen for user interactions
    window.addEventListener('mousemove', this.handleUserActivity);
    window.addEventListener('keydown', this.handleUserActivity);
    window.addEventListener('click', this.handleUserActivity);

    // Start the inactivity timer when the component is mounted
    this.resetInactivityTimer();

  
      // Connect to the WebSocket server
      this.socket = io(`http://${this.$apiIp}:5000`);
      
      this.socket.on('sensor_data', (data) => {
        this.sensors = data.sensors;
        console.log(this.sensors)
      });
      this.socket.on('cctv_data', (data) => {
        this.cameras = data.cameras;
        console.log(this.cameras);
      })
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
      // Clean up the event listeners when the component is destroyed
    window.removeEventListener('mousemove', this.handleUserActivity);
    window.removeEventListener('keydown', this.handleUserActivity);
    window.removeEventListener('click', this.handleUserActivity);

    // Clear the timeout
    clearTimeout(this.inactivityTimeout);
    },

  
}
  </script>
  
  <style scoped>
  .char-container {
    width: 50px;
  }
  
  .char-display {
    width: 50px;
    height: 50px;
    display: flex;
    border: 1px solid #ccc;
  }
  </style>