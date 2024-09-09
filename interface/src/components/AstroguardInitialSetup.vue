<template>
    <div class="flex astroguard-setup-screen items-center justify-center">
      <!-- <h1 class="text-astro-guard-white font-AXIS text-6xl px-4 py-4">Welcome to </h1> -->
      <img class="bg-no-repeat bg-cover" :src="setupImage" alt="Setup Image" />
      <button @click="this.$router.push('/systemname')" class="absolute bottom-40 text-astro-guard-white font-AXIS text-2xl border-8 rounded-full border-white p-4 hover:text-astro-guard-green">Get started</button>
      <!-- Add more setup content here -->
    </div>
  </template>
  
  <script>
  import setupImage from '@/assets/astroguard-setup-image.png'; 
  export default {
    name: 'AstroguardInitialSetup',  
    data() {
    return {
      setupImage
    };
  }
  };
  </script>
  
  <style scoped>

  </style>