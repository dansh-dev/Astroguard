<template>
  <div class="astroguard-setup-screen w-full">
    <div v-if="authScreen" class="fixed inset-4 md:inset-10 flex items-center justify-center bg-opacity-100 z-10">
      <div class="bg-astro-guard-container p-4 md:p-6 rounded-lg shadow-lg w-full max-w-md mx-2"
           :class="{'animate-GreenInnerGlow': IfCorrect, 'animate-RedInnerGlow': IfIncorrect}">
        <h2 class="text-astro-guard-white text-lg md:text-xl font-bold mb-2 md:mb-4">Authenticate yourself:</h2>
        <p class="mb-4 text-sm md:text-base text-astro-guard-white">Note: Facial recognition uses the camera of the command center</p>

        <!-- Passcode Entry -->
        <div class="password-input-container flex justify-center space-x-2 md:space-x-4">
          <div v-for="(digit, index) in vPass" :key="index" class="char-container flex flex-col items-center">
            <button @click="incrementVPass(index)"
                    class="text-astro-guard-white p-1 md:p-2 rounded text-lg md:text-2xl hover:text-astro-guard-green">▲</button>
            <div class="char-display text-xl md:text-3xl font-mono my-1 md:my-2 text-astro-guard-white rounded-full items-center justify-center">
              {{ digit }}
            </div>
            <button @click="decrementVPass(index)"
                    class="text-astro-guard-white p-1 md:p-2 rounded text-lg md:text-2xl hover:text-astro-guard-green">▼</button>
          </div>
          <div class="flex items-center justify-center">
            <h1 class="text-astro-guard-white text-lg md:text-xl font-AXIS">OR</h1>
          </div>
          <button @click="facialAuth()" class="rounded-xl hover:bg-astro-guard-lilac">
            <img :src="activateFsa" class="h-20 md:h-36" alt="" />
          </button>
        </div>

        <!-- Passcode Button -->
        <div class="w-full flex justify-start mt-4">
          <button @click="codeAuth()" class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white text-lg md:text-xl hover:bg-astro-guard-green">
            Use Passcode
          </button>
        </div>

        <!-- Cancel Button -->
        <div class="w-full flex justify-end mt-4">
          <button @click="cancel()" class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white text-lg md:text-xl hover:bg-astro-guard-red">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Face Scan Active -->
    <div v-if="faceScanActive" class="fixed inset-4 md:inset-10 flex items-center justify-center bg-opacity-100 z-10">
      <div class="bg-astro-guard-container p-6 rounded-lg shadow-lg">
        <img class="p-6 md:p-10" :src="fsa" alt="Facial Scan Active" />
      </div>
    </div>

    <!-- Main Content -->
    <div class="mx-4 md:mx-10 my-4 md:my-10 p-4 md:p-10 rounded-xl shadow-xl bg-astro-guard-container">
      <div class="w-full flex justify-center">
        <img class="w-40 md:w-80" :src="logo" alt="Logo" />
      </div>
    </div>

    <div class="mx-4 md:mx-10 my-4 md:my-10 p-4 md:p-10 md:pb-10 rounded-xl shadow-xl bg-astro-guard-container">
      <h1 class="text-astro-guard-white text-2xl md:text-3xl font-AXIS">Settings</h1>
      <h2 class="text-astro-guard-white text-lg md:text-xl font-AXIS">You can edit your settings here!</h2>
      <div class="w-full flex justify-end mt-4">
        <button @click="initAuth()" class="text-astro-guard-white font-JosefinSans border-4 p-2 pt-3 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-green">
          Save all Changes
        </button>
      </div>
      <div class="py-4">
        <h2 class="text-astro-guard-white text-xl md:text-2xl">System Name: </h2>
        <input class="w-full rounded-full border-0 py-1.5 pl-2 font-JosefinSans mt-2" v-model="systemName"
               :placeholder="'Current name: ' + settings['system_name']" />
      </div>

      <div class="py-4">
        <h2 class="text-astro-guard-white text-xl md:text-2xl">New Passcode: </h2>
        <button @click="updatePasscode()" class="w-full md:w-auto text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-green">
          Click to change current password
        </button>

        <div v-if="passwordInput" class="password-input-container flex justify-center space-x-2 md:space-x-4 mt-4">
          <div v-for="(digit, index) in newPassword" :key="index" class="char-container flex flex-col items-center">
            <button @click="incrementDigit(index)"
                    class="text-astro-guard-white p-1 md:p-2 rounded text-lg md:text-2xl hover:text-astro-guard-green">▲</button>
            <div class="char-display text-xl md:text-3xl font-mono my-1 md:my-2 text-astro-guard-white rounded-full items-center justify-center">
              {{ digit }}
            </div>
            <button @click="decrementDigit(index)"
                    class="text-astro-guard-white p-1 md:p-2 rounded text-lg md:text-2xl hover:text-astro-guard-green">▼</button>
          </div>
        </div>
      </div>

      <!-- Face and Sensor Settings -->
      <div class="flex flex-col space-y-4">
        <div>
          <h2 class="text-astro-guard-white text-xl md:text-2xl">Facial Recognition: Add/Remove people</h2>
          <button @click="addEntry()" class="text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white text-2xl md:text-3xl hover:text-astro-guard-green">
            +
          </button>
        </div>

        <table class="min-w-full">
          <thead>
            <tr>
              <th class="py-2 text-astro-guard-white">Name</th>
              <th class="py-2 text-astro-guard-white">Face</th>
              <th class="py-2 text-astro-guard-white">Options</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(entry, index) in entries" :key="index">
              <td class="py-2 px-4">
                <input type="text" v-model="entry.name" :disabled="entries[index]['face']"
                       class="w-full rounded-full border-0 py-1.5 pl-2 font-JosefinSans" placeholder="Enter name" />
              </td>
              <td class="py-2 px-4">
                <button @click="scanFace(index)" :disabled="entries[index]['face']"
                        :class="{
                          'w-full text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full border-white bg-astro-guard-container hover:bg-astro-guard-green': !entries[index]['face'],
                          'w-full text-gray-100 font-JosefinSans border-4 p-2 rounded-full border-gray-400 bg-gray-300': entries[index]['face']
                        }">
                  {{ entries[index]['face'] ? 'Face Scanned ✔' : 'Scan Face' }}
                </button>
              </td>
              <td class="py-2 px-4">
                <button @click="deleteEntry(index)" class="w-full text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-red">
                  X
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div>
          <h2 class="text-astro-guard-white text-xl md:text-2xl">Sensor Settings:</h2>
          <button @click="addSensor()" class="text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white text-2xl md:text-3xl hover:text-astro-guard-green">
            +
          </button>
        </div>

        <table class="min-w-full">
          <thead>
            <tr>
              <th class="py-2 text-astro-guard-white">Serial Number</th>
              <th class="py-2 text-astro-guard-white">Options</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(sensor, index) in sensors" :key="index">
              <td class="py-2 px-4">
                <input type="text" v-model="sensor.serial" class="w-full rounded-full border-0 py-1.5 pl-2 font-JosefinSans" placeholder="Serial Number" />
              </td>
              <td class="py-2 px-4">
                <button @click="deleteSensor(index)" class="w-full text-astro-guard-white font-JosefinSans border-4 p-2 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-red">
                  X
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
      </div>


    </div>
    <NavBar />
  </div>
</template>


  
  <script>
import axios from 'axios';
import NavBar from './NavBar.vue';
import logo from '@/assets/astroguard-logo.png';
import fsa from '@/assets/FSA.png';
import activateFsa from '@/assets/ActivateFSA.png';
  export default {
    name: 'SettingsScreen',
    components: {
      NavBar
    },
    data() {
      return {
        entries: [],
        sensors: [],
        authType: "",
        vPass: [0,0,0,0],
            table: true,
            systemName: "",
            passwordInput: false,
            authScreen: false,
            faceScanActive: false,
            IfIncorrect: false,
            IfCorrect: false,
            logo,
            fsa,
            activateFsa,
            newPassword: [0,0,0,0],
        inactivityTimeout: null, // This will hold our timeout reference
        inactivityTime: 300000,  // 5 minutes in milliseconds
        error: null,
        settings: []
      };
    },
    methods: {
      initAuth() {
        this.authScreen = true;
      },
      facialAuth() {
        this.authType = 'facial'
        this.saveSettings()
      },
      codeAuth() {
        this.authType = 'code'
        this.saveSettings()
      },
      async saveSettings() {
        
        if(this.systemName.length>1) {
          this.settings["system_name"] = this.systemName
        }

        if(this.passwordInput == true) {
          this.settings["passcode"] = this.newPassword
        }

        this.settings["sensors"] = this.sensors
        console.log(this.entries)
        this.settings["faces"] = this.entries
        console.log(this.settings)
        const payload = {
          "settings": this.settings,
          "authType": this.authType,
          "code": this.vPass
        }

        console.log(this.settings)
        if(this.authType == "facial") {
          this.faceScanActive = true;
        }
        await axios.post(`http://${this.$apiIp}:5000/updateSettings`, payload)
        .catch( () => {
          this.IfIncorrect = true
          setTimeout(() => {
            this.IfIncorrect = false
          }, 2000)
        
      });
         setTimeout(() => {
          this.faceScanActive = false;
                  this.$router.push('/main');
                    location.reload()

         }, 2000)       
                  
                
      },
      updatePasscode() {
        this.passwordInput = true
      },
      incrementDigit(index) {
      if (this.newPassword[index] < 9) {
        this.newPassword.splice(index, 1, this.newPassword[index] + 1);
      } else {
        this.newPassword.splice(index, 1, 0);
      }
    },
    decrementDigit(index) {
      if (this.newPassword[index] > 0) {
        this.newPassword.splice(index, 1, this.newPassword[index] - 1);
      } else {
        this.newPassword.splice(index, 1, 9);
      }
    },
    incrementVPass(index) {
      if (this.vPass[index] < 9) {
        this.vPass.splice(index, 1, this.vPass[index] + 1);
      } else {
        this.vPass.splice(index, 1, 0);
      }
    },
    decrementVPass(index) {
      if (this.vPass[index] > 0) {
        this.vPass.splice(index, 1, this.vPass[index] - 1);
      } else {
        this.vPass.splice(index, 1, 9);
      }
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
      async resetSettings() {
      this.settings = localStorage.getItem("settings");
      if (this.settings) {
        const json = JSON.parse(this.settings)
        json['flag'] = 'setup'
        const response = await axios.post(`http://${this.$apiIp}/setup`, json);
        console.log(response);
      }
    },
    cancel(){
      this.authScreen = false
    },
    addEntry() {
            this.table = true;
            this.entries.push({ name: '' });
        },
        async scanFace(index) {
            const name = this.entries[index].name

            if (name.length > 1) {
                this.faceScanActive = true
                const response = await axios.post(`http://${this.$apiIp}:5000/register_face`, { "name": name });
                const data = response.data;
                this.entries[index]["face"] = data["file_path"];
                this.faceScanActive = false;
            } else {
                alert("Please input a name before scan!")
            }

        },
        deleteEntry(index) {
            this.entries.splice(index, 1);
            if (this.entries.length < 1) {
                this.table = false;
            }
        },
        addSensor() {
            this.table = true;
            this.sensors.push({ serial: '' });
        },
        updateSensors() {
            const settings = localStorage.getItem("settings");
            for (let entry of this.entries) {
                if (!entry.serial) {
                    return alert("Please fill all fields before proceeding!");
                }
            }

            this.retrievedData = JSON.parse(settings);
            console.log(this.retrievedData);
            this.retrievedData.sensors = this.entries;
            // Convert the updated data back to a JSON string
            const jsonData = JSON.stringify(this.retrievedData);

            // Save the updated JSON string to local storage
            localStorage.setItem('settings', jsonData);
            this.$router.push('/FinalizeSetup');

        },
        deleteSensor(index) {
            this.sensors.splice(index, 1);
            if (this.sensors.length < 1) {
                this.table = false;
            }
        }
    },
    mounted() {
    // Listen for user interactions
    this.settings = JSON.parse(localStorage.getItem("settings"));
    
    console.log(this.settings);
    this.entries = this.settings['faces']
    this.sensors = this.settings['sensors']
    window.addEventListener('mousemove', this.handleUserActivity);
    window.addEventListener('keydown', this.handleUserActivity);
    window.addEventListener('click', this.handleUserActivity);

    // Start the inactivity timer when the component is mounted
    this.resetInactivityTimer();
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
  
  };
  </script>
  
  <style>
  /* No need for @tailwind directives if using @import in main.css */
  </style>
  