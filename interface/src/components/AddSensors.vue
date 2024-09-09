<template>
    <div class="astroguard-setup-screen w-full">
        <img class="p-10" :src="logo" alt="Logo" />
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">
            <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Sensor Setup</h1>
        </div>
        <div class="mx-10 my-10 p-10 rounded-xl shadow-xl bg-astro-guard-container">

            <div class="container mx-auto p-4">
                <div class="flex mb-4">
                    <h1 class="text-3xl text-astro-guard-white font-JosefinSans">Add Sensors</h1>
                    <div class="w-full"></div>
                    <button @click="addSensor"
                        class="mx-2 text-astro-guard-white font-JosefinSans border-4 p-2 bg-astro-guard-container rounded-full border-white text-3xl hover:text-astro-guard-green">
                        +
                    </button>
                </div>
                <table class="min-w-full " v-if="this.table">
                    <thead>
                        <tr>
                            <th class="py-2 text-astro-guard-white">Serial Number</th>
                            <th class="py-2 text-astro-guard-white">Options</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(entry, index) in entries" :key="index">
                            <td class="py-2 px-4 ">
                                <input type="text" v-model="entry.serial"
                                    class="w-full rounded-full border-0 py-1.5 pl-2 font-JosefinSans"
                                    placeholder="Serial Number" />
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

                <div v-if="this.table" class="w-full justify-end flex p-5">
                    <button @click="updateSensors()"
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
export default {
    name: 'AddSensors',
    data() {
        return {
            logo,
            retrievedData: null,
            entries: [],
            table: null,
        };
    },
    methods: {
        addSensor() {
            this.table = true;
            this.entries.push({ serial: '' });
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
        deleteEntry(index) {
            this.entries.splice(index, 1);
            if (this.entries.length < 1) {
                this.table = false;
            }
        }
    }
};
</script>

<style scoped></style>