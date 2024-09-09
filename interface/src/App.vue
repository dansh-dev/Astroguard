<template>
  <div id="app"  class="min-h-screen flex bg-gray-100">
    <div class="max-w-screen w-full bg-astro-guard-bg shadow-md min-h-screen flex " :class="{'animate-RedInnerGlow': TriggerState}" >
      <RouterView class=""/>

    </div>
  </div>
</template>

<script>
import axios from 'axios';
import './main.css';
import { RouterView } from 'vue-router';

export default {
  name: 'App',
  components: {
    RouterView
  },
  data() {
    return {
      AlarmState: null,
      TriggerState: false,
      error: null,
      intervalId: null, // To store the interval ID
    };
  },
  mounted() {
    this.startLocalStorageCheck();
  },
  beforeUnmount() {
    this.stopLocalStorageCheck();
  },
  methods: {
    startLocalStorageCheck() {
      this.intervalId = setInterval(() => {
        this.checkLocalStorage();
      }, 1000); // Check every second
    },
    stopLocalStorageCheck() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
      }
    },
    checkLocalStorage() {
      
      const storedValue = JSON.parse(localStorage.getItem('AlarmState'));
      if (storedValue == null) {
        const filler = JSON.stringify({
          "ArmState": false,
                "TriggerState": false,
                "LastArm": '',
                "LastTrigg": '',
                "Timestamp": ''
        })
        localStorage.setItem('AlarmState', filler)
      }
      if (storedValue['TriggerState'] == true) {
        this.TriggerState = true
      }
      if (storedValue['TriggerState'] == false) {
        this.TriggerState = false
      }

      if (storedValue !== this.AlarmState) {
        this.AlarmState = storedValue;
    }
  },
    async fetchData() {
      try {
        const response = await axios.get(`http://${this.$apiIp}:5000/setup`);
        console.log(this.$apiIp);
        console.log(response.data.flag)
        if (response.data.flag === 'setup') {
          const settings = JSON.stringify(response.data);
          // Save the JSON string to local storage
          localStorage.setItem("settings", settings);
          this.$router.push('/getstarted')
        }
        if (response.data.flag === 'system') {
          const settings = JSON.stringify(response.data);
          // Save the JSON string to local storage
          localStorage.setItem("settings", settings);
          this.$router.push('/main')
        }
      } catch (error) {
        this.error = 'Error fetching setup data';
        console.error(error);
      }
    }
  },
  created() {
    this.fetchData();
  },

};
</script>

<style>
/* No need for @tailwind directives if using @import in main.css */
</style>
