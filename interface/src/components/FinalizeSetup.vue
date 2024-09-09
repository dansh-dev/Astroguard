<template>
    <div class="astroguard-setup-screen w-full">
        <img class="p-10" :src="logo" alt="Logo" />
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
            <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Finalize Setup</h1>
        </div>
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
            <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Your settings are as follows:</h1>
            <h2 class=" text-astro-guard-white font-JosefinSans"> System name: {{ this.settings["system_name"] }}
            </h2>
            <h2 class=" text-astro-guard-white font-JosefinSans"> System Passcode:
                {{ this.settings["passcode"]["value"] }}</h2>
            <div v-if="this.faces_list">
                <h2 class="text-2xl text-astro-guard-white font-JosefinSans"> Faces:</h2>
                <Ul class="list-disc">
                    <li class=" text-astro-guard-white font-JosefinSans" v-for="(entry, index) in settings['faces']"
                        :key="index">Name: {{ entry['name'] }} Path: {{ entry['face'] }}</li>
                </Ul>
            </div>
            
        </div>
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container items-end justify-end flex">
            <button @click="this.$router.push('/getstarted')"
                class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-red">
                Return to start
            </button>
            <button @click="postSetup()"
                        class=" text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">
                        Confirm
                    </button>
                </div>
    </div>
</template>

<script>
import logo from '@/assets/astroguard-logo.png';
import axios from 'axios';
export default {
    name: 'FinalizeSetup',
    data() {
        return {
            logo,
            settings: null,
            faces_list: false
        };
    },
    methods: {
        async postSetup() {
            if(this.settings) {
                this.settings['flag'] = 'system'
                const response = await axios.post(`http://${this.$apiIp}:5000/setup`, this.settings);
                if(response.status === 200){
                    this.$router.push('/main');

                }else{
                    return alert('Server error')
                }
            }
        },
    },
    created() {
        const local_settings = localStorage.getItem("settings");
        if (local_settings) {
            this.settings = JSON.parse(local_settings);

            if (this.settings['faces'][0]) {
                this.faces_list = true;
            } 

        }
    }
};
</script>

<style scoped></style>