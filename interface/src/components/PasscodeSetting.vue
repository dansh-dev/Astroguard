<template>
  <div class="astroguard-setup-screen w-full">
    <img class="p-10" :src="logo" alt="Logo" />
    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
      <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Create a passcode</h1>
    </div>
    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container justify-center items-center flex">

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

      </div>
    </div>

    <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container justify-center items-center flex">
      <p class="text-astro-guard-white">Do not forget this passcode</p>
      <button @click="updatePassword()"
        class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">Confirm</button>
    </div>
  </div>
</template>

<script>
import logo from '@/assets/astroguard-logo.png';
export default {
  data() {
    return {
      logo,
      password: [0, 0, 0, 0] // Initialize with digits
    };
  },
  methods: {
    async updatePassword() {
      // Retrieve the JSON string from local storage
      const settings = localStorage.getItem("settings");
      // Parse the JSON string back to an object
      if (settings) {
        this.retrievedData = JSON.parse(settings);
        console.log(this.retrievedData);
        const newPassword = this.password ;
        console.log(newPassword);
       
          this.retrievedData.passcode = newPassword;
          // Convert the updated data back to a JSON string
          const jsonData = JSON.stringify( this.retrievedData);

          // Save the updated JSON string to local storage
          localStorage.setItem('settings', jsonData);
          this.$router.push('/AstroguardFacialSetup');
          // Next page
      } else {
        alert("No data found in local storage!");
      }
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
    }
  }
};
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