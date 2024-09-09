<template class="">
  <div class="astroguard-setup-screen w-full ">
    <div v-if="popupActive" class="fixed inset-10 flex items-center justify-center bg-opacity-100 z-10" >
                <div class="bg-astro-guard-container p-6 rounded-lg shadow-lg" :class="{'animate-GreenInnerGlow': IfCorrect, 'animate-RedInnerGlow': IfIncorrect}">
                    <h2 class="text-astro-guard-white text-xl font-bold mb-4">Authenticate yourself:</h2>
                    <p class="mb-4 text-astro-guard-white">Note: Facial recognition uses the camera of the command center</p>
                    <!--  -->
                    
            <div class="password-input-container flex space-x-4">
        <div v-for="(digit, index) in password" :key="index" class="char-container flex flex-col items-center">
          <button @click="incrementDigit(index)"
            class=" text-astro-guard-white p-2 rounded text-2xl hover:text-astro-guard-green">▲</button>
          <div
            class="char-display text-3xl font-mono my-2 text-astro-guard-white rounded-full items-center justify-center ">
            {{ digit }}</div>
          <button @click="decrementDigit(index)"
            class=" text-astro-guard-white p-2 rounded text-2xl hover:text-astro-guard-green">▼</button>
        </div>
        <div class="justify-center h-full">
        <h1 class="text-astro-guard-white text-xl font-AXIS">OR</h1>
      </div>
    
      <button @click="facialArm()" class="rounded-xl hover:bg-astro-guard-lilac">
        <img :src="activateFsa" class="h-36" alt="" srcset="">
      </button>
    
        </div>
        <div class="w-full items-start justify-start flex ">
          <button @click="codeArm()"
                            class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-xl hover:bg-astro-guard-green">Use Passcode</button>
                    
        </div>
                    <div class="w-full items-end justify-end flex">
                        <button @click="cancel()"
                            class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-xl hover:bg-astro-guard-red">Cancel</button>
                    </div>
                </div>
          </div>
          <div v-if="faceScanActive" class="z-10 fixed inset-10 flex items-center justify-center bg-opacity-100">
                <div class="bg-astro-guard-container p-6 rounded-lg shadow-lg">
                    <img class="p-10" :src="fsa" alt="FacialScanActive" />
                </div>
                </div> 
    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container ">

      <div class="w-full justify-center items-center flex">

        <img class="w-80" :src="logo" alt="Logo" />
       
      </div>
    </div>
    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
      <h1 class="text-astro-guard-white text-3xl font-AXIS">Welcome to Astroguard</h1>
      <h2 class="text-astro-guard-white text-2xl font-AXIS">{{ currentDateTime }}</h2>
      <button @click="this.$router.push('emulator')"
      class="text-astro-guard-white font-JosefinSans border-4 p-2 pt-3 my-2 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-green">Emulate Sensors</button>
      <div class="flex-row md:flex-row shadow-xl">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mt-4 md:mt-0 shadow-xl ">
          <div class="border p-4 text-astro-guard-white rounded-xl h-80 justify-center flex overflow-hidden hover:bg-astro-guard-lilac">
            <div v-if="alarmState['ArmState'] == true && alarmState['TriggerState'] == false">
            <button @click="ArmDisarm()">
              <h1 class="font-AXIS text-xl">Alarm is Armed!</h1>
              <img class="p-0 max-w-80" :src="armed" alt="armed" />
            </button>
          </div>
          <div v-if="alarmState['ArmState'] == false ">
            <button @click="ArmDisarm()">
              <h1 class="font-AXIS text-xl">Alarm is Disarmed!</h1>
              <img class="p-0 max-w-80" :src="disarmed" alt="disarmed" />
            </button>
          </div>
          <div v-if="alarmState['TriggerState'] == true && alarmState['ArmState'] == true">
            <button @click="ArmDisarm()">
              <h1 class="font-AXIS text-xl">Alarm is Triggered!</h1>
              <img class="p-0 max-w-80" :src="armedAndTriggered" alt="disarmed" />
            </button>
          </div>
          </div>
          <div class="border p-4 text-astro-guard-white rounded-xl w-full overflow-y-scroll h-80">
            <div class="w-full flex"> 
              <h1 class="font-AXIS text-xl">Security Events</h1>
              <div class="w-full flex items-end justify-end"> 
                <button @click="clearNotifs()"
                class=" text-astro-guard-white rounded text-2xl hover:text-astro-guard-green">x</button>
              </div>
          </div>
            <div v-for="(notification, index) in notifications" :key="index" class="my-1 border p-4 text-astro-guard-white rounded-xl w-full">
              <h1 class="font-JosefinSans">{{notification['title']}}</h1>
              <h1 class="font-JosefinSans">{{notification['timestamp']}}</h1>
            </div>
           
          </div>
          <div class="border p-4 text-astro-guard-white rounded-xl w-full h-80">
            <h1 class="font-AXIS text-xl">Camera list</h1>
            <div v-for="(camera, index) in cameras" :key="index" class="my-1 border p-4 text-astro-guard-white rounded-xl w-full">
              <h1 class="font-JosefinSans">{{ camera['SerialNumber']}}</h1>
              <h1 class="font-JosefinSans">Last Detected: {{camera['Label']}}</h1>
              <h1 class="font-JosefinSans">{{camera['Timestamp']}}</h1>

            </div>
          </div>
        </div>
          <div class="flex my-4">
            <!-- Sensor List Section -->
            <div  class="md:w-1/4 md:mr-4 w-full bg-astro-guard-container border rounded-xl mr-0 overflow-y-scroll p-4 h-auto">
              <h2 class="text-xl font-bold font-AXIS text-astro-guard-white mb-4">Sensor List</h2>
              <!-- Sensor List Content -->
              <div v-for="(sensor, index) in sensors" :key="index" class="my-1 border p-4 text-astro-guard-white rounded-xl w-full">
              <h1 class="font-JosefinSans">{{ sensor['SerialNumber']}}</h1>
              <h1 class="font-JosefinSans">Triggered: {{ sensor['AlarmState']}}</h1>
            </div>
            
            </div>
            <div class="w-3/4 bg-astro-guard-container border rounded-xl p-4 h-auto hidden md:flex">
              <MapView v-if="mapActive" :sensors="sensors" class="w-full rounded-xl"/>
              <div class=" bg-gray-200 flex items-center justify-center">
              </div>
            </div>
            
          </div>
          <div class="w-full border rounded-xl p-4">
            <EventTimeline :events="notifications"/>
          </div>
      </div>
    </div>
    <NavBar />
  </div>
  
</template>

<script>
// import axios from 'axios';
import logo from '@/assets/astroguard-logo.png';
import disarmed from '@/assets/AlarmDisarmed.png';
import armed from '@/assets/AlarmArmed.png';
import armedAndTriggered from '@/assets/AlarmArmedTriggered.png'
import settingsIcon from '@/assets/Settings.png';
import secDot from '@/assets/SecDot.png';
import fsa from '@/assets/FSA.png';
import activateFsa from '@/assets/ActivateFSA.png';
import MapView from './MapView.vue';
import NavBar from './NavBar.vue';
import EventTimeline from './EventTimeline.vue';
import { io } from "socket.io-client";
import axios from 'axios';

import alarmSound from '@/assets/sounds/astroguard_alarm_sound.mp3'; // Static import
import lockSound from '@/assets/sounds/astroguard_lock_sound.mp3';
import errorSound from '@/assets/sounds/astroguard_error_sound.mp3'
export default {
  name: 'AstroguardMainScreen',
  components: {
    MapView,
    NavBar,
    EventTimeline
  },
  created() {
    window.setInterval(() => {
      this.currentDateTime = new Date().toLocaleString()
    }, 1000);
  },
  data() {
    return {
      fsa,
      settings: null,
      logo,
      alarmState: null,
      disarmed,
      armed,
      armedAndTriggered,
      currentDateTime: null,
      settingsIcon,
      secDot,
      activateFsa,
      alarmSound,
      lockSound,
      errorSound,
      sensors: [],
      cameras: [],
      notifications: [],
      mapActive: false,
      popup: false,
      popupActive: false,
      IfCorrect: false,
      IfIncorrect: false,
      faceScanActive: false,
      password: [0,0,0,0],
      
    }
  },
  beforeMount() {
    this.alarmState = {ArmState: false, TriggerState: true, LastArm: 'Tue, 13 Aug 2024 19:46:28 GMT', LastTrigg: 'Tue, 13 Aug 2024 18:01:46 GMT', Timestamp: 'Tue, 13 Aug 2024 19:46:28 GMT'}
    window.setInterval(() => {
      this.currentDateTime = new Date().toLocaleString()
    }, 1000);
  },
  mounted() {
      // Connect to the WebSocket server
      this.socket = io('http://'+this.$apiIp+':5000');

  
      // Listen for sensor data from the server
      this.socket.on('sensor_data', (data) => {
        this.mapActive = true;
        this.sensors = data.sensors;
      });

      this.socket.on('cctv_data', (data)=> {
        this.cameras = data.cameras;
      })
  
      // Listen for security notifications
      this.socket.on('security_notification', (msg) => {
        // console.log(msg.message)
        this.notifications = msg.message
        console.log(msg.message)
      });

      // Recieve updated alarm state
      this.socket.on('alarm_state', (alarm)=> {
        // console.log(alarm.alarm['ArmState'])
        this.alarmState = alarm.alarm;
        if(alarm.alarm['TriggerState'] == true) {
          this.playAlarmSound()
        }
        const state = JSON.stringify(alarm.alarm);
          // Save the JSON string to local storage
          localStorage.setItem("AlarmState", state);
        // console.log(this.alarmState)
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
    },

  methods: {
    async ArmDisarm() { 
      this.popupActive = true
    },
    async facialArm() {
      this.faceScanActive = true
      await axios.post('http://'+this.$apiIp+':5000/setAlarm', { "authType": 'facial' })
      
      .catch( () => {
          this.IfIncorrect = true
          this.playBadInput()
          setTimeout(() => {
            this.IfIncorrect = false
          }, 2000)
        
      });
      this.password = [0,0,0,0]
      this.IfCorrect = true
      setTimeout(() => {
        this.playLockSound()
        this.faceScanActive = false
        this.popupActive = false
        this.IfCorrect = false
      }, 2000);
      
      
      
    },
    async codeArm() {
      await axios.post('http://'+this.$apiIp+':5000/setAlarm', {"authType": 'code', "code": this.password})
      .catch((error) => {
        this.IfIncorrect = true
        this.playBadInput()
        setTimeout(() => {
          this.IfIncorrect = false
        }, 2000)
        console.log(error.status)
      })
      this.password = [0,0,0,0]
      this.IfCorrect = true
      setTimeout(() => {
        this.playLockSound()
        this.popupActive = false
        this.IfCorrect = false
      }, 2000);
    },
    async clearNotifs() {
      await axios.post(`http://${this.$apiIp}:5000/clear_security_notifications`)
    },
    incrementDigit(index) {
      if (this.password[index] < 9) {
        this.password.splice(index, 1, this.password[index] + 1);
      } else {
        this.password.splice(index, 1, 0);
      }
    },
    decrementDigit(index) {
      if (this.password[index] > 0) {
        this.password.splice(index, 1, this.password[index] - 1);
      } else {
        this.password.splice(index, 1, 9);
      }
    },
    cancel(){
      this.popupActive = false
    },
    playAlarmSound() {
      const audio = new Audio(this.alarmSound);
      audio.play();
    },
    playLockSound() {
      const audio = new Audio(this.lockSound);
      audio.play();
    },
    playBadInput() {
      const audio = new Audio(this.errorSound)
      audio.play();
    }
  },
};
</script>

<style scoped></style>