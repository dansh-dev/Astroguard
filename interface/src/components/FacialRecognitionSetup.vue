<template>
    <div class="astroguard-setup-screen w-full">
        <img class="p-10" :src="logo" alt="Logo" />
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
            <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Facial Recognition Setup</h1>
        </div>
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
            <div v-if="popup" class="fixed inset-10 flex items-center justify-center bg-opacity-100">
                <div class="bg-astro-guard-container p-6 rounded-lg shadow-lg">
                    <h2 class="text-astro-guard-white text-xl font-bold mb-4">Are you sure?</h2>
                    <p class="mb-4 text-astro-guard-white">Are you sure that you don't want facial recognition features
                        to function?</p>
                    <p class="mb-4 text-gray-400">You can set this up at a later date.</p>
                    <div class="w-full items-end justify-end">
                        <button @click="cancel"
                            class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-xl hover:bg-astro-guard-red">Close</button>
                        <button @click="updateFaces('skip')"
                            class=" text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-xl hover:bg-astro-guard-green">Confirm</button>
                    </div>
                </div>
            </div>
            <div v-if="faceScanActive" class="fixed inset-10 flex items-center justify-center bg-opacity-100">
                <div class="bg-astro-guard-container p-6 rounded-lg shadow-lg">
                    <img class="p-10" :src="fsa" alt="FacialScanActive" />
                </div>
            </div>
            <div class="container mx-auto p-4">
                <div class="flex mb-4">
                    <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Add People</h1>
                    <div class="w-full"></div>
                    <button @click="addEntry"
                        class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-3xl hover:text-astro-guard-green">
                        +
                    </button>
                </div>
                <table class="min-w-full " v-if="this.table">
                    <thead>
                        <tr>
                            <th class="py-2 text-astro-guard-white">Name</th>
                            <th class="py-2 text-astro-guard-white">Face</th>
                            <th class="py-2 text-astro-guard-white">Options</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(entry, index) in entries" :key="index">
                            <td class="py-2 px-4 ">
                                <input type="text" v-model="entry.name"
                                    class="w-full rounded-full border-0 py-1.5 pl-2 font-JosefinSans"
                                    placeholder="Enter name" />
                            </td>
                            <td class="py-2 px-4">
                                <button @click="scanFace(index)" :disabled="entries[index]['face']" :class="{
                                    'w-full text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:bg-astro-guard-green':
                                        !entries[index]['face'],
                                    'w-full text-gray-100 font-JosefinSans border-4 p-2 bg-gray-300 rounded-full border-gray-400':
                                        entries[index]['face']
                                }">
                                    {{ entries[index]['face'] ? 'Face Scanned ✔' : 'Scan Face' }}
                                </button>
                            </td>
                            <td class="py-2 px-4">
                                <button @click="deleteEntry(index)"
                                    class="w-full text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:bg-astro-guard-red">
                                    X
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div v-if="!this.table" class="w-full justify-end flex p-5">
                    <button @click="skip()"
                        class=" text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-red">
                        Skip
                    </button>

                </div>
                <div v-if="this.table" class="w-full justify-end flex p-5">
                    <button @click="updateFaces('update')"
                        class=" text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white hover:text-astro-guard-green">
                        Confirm
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import logo from '@/assets/astroguard-logo.png';
import fsa from '@/assets/FSA.png'
import axios from 'axios';
export default {
    name: 'AstroguardFacialSetup',
    data() {
        return {
            entries: [],
            table: null,
            logo,
            fsa,
            retrievedData: null,
            popup: false,
            faceScanActive: false,
        };
    },
    methods: {
        updateFaces(mode) {
            const settings = localStorage.getItem("settings");
            if (mode === 'skip') {
                if (settings) {
                    this.retrievedData = JSON.parse(settings);
                    console.log(this.retrievedData);
                    this.retrievedData.faces = [];
                    // Convert the updated data back to a JSON string
                    const jsonData = JSON.stringify(this.retrievedData);

                    // Save the updated JSON string to local storage
                    localStorage.setItem('settings', jsonData);
                    this.$router.push('/AddSensors');
                }
            }
            if (mode === 'update') {
                if (settings) {

                    for (let entry of this.entries) {
                        if (!entry.name || !entry.face) {
                            return alert("Please fill all required fields before proceeding!");
                        }
                    }


                    this.retrievedData = JSON.parse(settings);
                    console.log(this.retrievedData);
                    this.retrievedData.faces = this.entries;
                    // Convert the updated data back to a JSON string
                    const jsonData = JSON.stringify(this.retrievedData);

                    // Save the updated JSON string to local storage
                    localStorage.setItem('settings', jsonData);
                    this.$router.push('/AddSensors');
                }

            }
            // Parse the JSON string back to an object

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
        skip() {
            this.popup = true;

        },
        cancel() {
            this.popup = false;
        },
    },
};
</script>

<style scoped>
.container {
    max-width: 800px;
}
</style>