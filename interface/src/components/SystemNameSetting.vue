<template>
  <div class="astroguard-setup-screen w-full">
    <img class="p-10" :src="logo" alt="Logo" />
    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
      <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Thank you for choosing Astroguard!</h1>
      <p class="text-l text-astro-guard-white font-JosefinSans">Follow the steps to get your installation up and
        running!</p>
    </div>
    <div class="mx-10 p-10 rounded-xl shadow-xl bg-astro-guard-container flex ">
      <p class=" mx-2 text-2xl text-astro-guard-white font-JosefinSans">Assign a name for this installation:</p>
      <input class="rounded-full border-0 py-1.5 pl-2 font-JosefinSans" v-model="systemName"
        placeholder="eg: Farm house" />
        <div>
        <button @click="updateName()"
          class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">Confirm</button>
      </div>
    </div>
    <div class="w-full items-center justify-center flex">
      <img class="p-10" :src="planet" alt="Logo" />
      <p class=" mx-2 text-2xl text-astro-guard-white font-JosefinSans"></p>
    </div>

  </div>
</template>

<script>
import logo from '@/assets/astroguard-logo.png';
import planet from '@/assets/planet.png';
export default {
  name: 'AstroguardNameSetting',
  data() {
    return {
      logo,
      planet,
      retrievedData: null,
      systemName: ""
    };
  },
  methods: {
    async updateName() {
      // Retrieve the JSON string from local storage
      const settings = localStorage.getItem("settings");
      // Parse the JSON string back to an object
      if (settings) {
        this.retrievedData = JSON.parse(settings);
        console.log(this.retrievedData);
        const newName = { value: this.systemName };
        console.log(newName);
        if (newName.value.length > 1) {
          this.retrievedData.system_name = newName.value;
          // Convert the updated data back to a JSON string
          const jsonData = JSON.stringify( this.retrievedData);

          // Save the updated JSON string to local storage
          localStorage.setItem('settings', jsonData);
          this.$router.push('/systempasscode');
          // Next page
        } else {
          alert("Input a name please");
        }
      } else {
        alert("No data found in local storage!");
      }
    }
  },
};
</script>

<style scoped></style>