<template>
  <div class="fixed bottom-0 left-0 right-0 rounded-t-xl shadow-xl bg-astro-guard-container flex justify-around items-center p-5 sm:p-10 sm:mx-10 sm:my-10">
    <button @click="goTo('main')" class="flex flex-col items-center focus:outline-none">
      <img :src="currentRoute === '/main' ? home_active : home_inactive" class="h-8 w-8 sm:h-10 sm:w-10" />
      <span class="text-xs sm:text-s font-AXIS text-astro-guard-white">Home</span>
    </button>

    <button @click="goTo('SensorList')" class="flex flex-col items-center focus:outline-none">
      <img :src="currentRoute === '/SensorList' ? sensorlist_active : sensorlist_inactive" class="h-8 w-8 sm:h-10 sm:w-10" />
      <span class="text-xs sm:text-s font-AXIS text-astro-guard-white">Sensor List</span>
    </button>

    <button @click="goTo('SettingsScreen')" class="flex flex-col items-center focus:outline-none">
      <img :src="currentRoute === '/SettingsScreen' ? settings_active : settings_inactive" class="h-8 w-8 sm:h-10 sm:w-10" />
      <span class="text-xs sm:text-s font-AXIS text-astro-guard-white">Settings</span>
    </button>
  </div>
</template>

<script>
import home_active from '@/assets/icons/active/home-active.png';
import home_inactive from '@/assets/icons/inactive/home-inactive.png';
import sensorlist_active from '@/assets/icons/active/list-active.png';
import sensorlist_inactive from '@/assets/icons/inactive/list-inactive.png';
import settings_active from '@/assets/icons/active/settings-active.png';
import settings_inactive from '@/assets/icons/inactive/settings-inactive.png';

export default {
  name: "NavBar",
  computed: {
    currentRoute() {
      return this.$route.path;
    }
  },
  methods: {
    goTo(screen) {
      this.$router.push(screen);
    }
  },
  data() {
    return {
      home_active,
      home_inactive,
      sensorlist_active,
      sensorlist_inactive,
      settings_active,
      settings_inactive
    };
  }
}
</script>

<style scoped>
/* Optional: Add custom styles for hover or other states */
</style>
