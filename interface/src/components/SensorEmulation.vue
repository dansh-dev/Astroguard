<template>
    <div class="input-data-form ">
      <h2>Test /input_data Endpoint</h2>
  
      <!-- Node Type Selection -->
      <label class="text-white" for="nodeType">Select Node Type:</label>
      <select v-model="nodeType" @change="resetForm">
        <option value="SN">Sensor Node</option>
        <option value="CN">Camera Node</option>
      </select>
  
      <!-- Dynamic Form for Sensor or Camera Node -->
      <form @submit.prevent="submitData">
  
        <!-- Shared Fields -->
        <div>
          <label class="text-white" for="SerialNumber">Serial Number:</label>
          <input v-model="formData.SerialNumber" required />
        </div>
  
        <div v-if="nodeType === 'SN'">
          <!-- Sensor Node Specific Fields -->
          <div>
            <label class="text-white" for="AlarmState">Alarm State:</label>
            <input class="text-white" type="checkbox" v-model="formData.AlarmState" />
          </div>
          <div>
            <label class="text-white" for="TamperState">Tamper State:</label>
            <input class="text-white" type="checkbox" v-model="formData.TamperState" />
          </div>
        </div>
  
        <div v-if="nodeType === 'CN'">
          <!-- Camera Node Specific Fields -->
          <div>
            <label class="text-white" for="Label">Label:</label>
            <input v-model="formData.Label" required />
          </div>
        </div>
  
        <!-- Shared Fields -->
        <div>
          <label class="text-white" for="Latitude">Latitude:</label>
          <input v-model="formData.Latitude" type="number" step="0.000001" required />
        </div>
  
        <div>
          <label class="text-white" for="Longitude">Longitude:</label>
          <input v-model="formData.Longitude" type="number" step="0.000001" required />
        </div>
  
        <div>
          <label class="text-white"  for="Charge">Charge (%):</label>
          <input v-model="formData.Charge" type="number" min="0" max="100" required />
        </div>
  
        <div>
          <label class="text-white" for="SignalStrength">Signal Strength (%):</label>
          <input v-model="formData.SignalStrength" type="number" min="-999" max="999" required />
        </div>
  
        <!-- Submit Button -->
        <button type="submit" class="text-astro-guard-white font-JosefinSans border-4 p-2 pt-3 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-green">
          Submit sensor data
        </button>
        
  
      </form>
      <button @click="this.$router.push('/main');" class="text-astro-guard-white font-JosefinSans border-4 p-2 pt-3 rounded-full bg-astro-guard-container border-white hover:bg-astro-guard-green">
          Back to home screen
        </button>
      <!-- Display Result -->
      <div v-if="responseMessage">
        <h3>Response:</h3>
        <pre>{{ responseMessage }}</pre>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        nodeType: "SN", // Default to sensor node
        formData: {
          SerialNumber: "",
          AlarmState: false,
          TamperState: false,
          Latitude: "",
          Longitude: "",
          Charge: "",
          SignalStrength: "",
          Label: "" // Used only for Camera Node (CN)
        },
        responseMessage: null
      };
    },
    methods: {
      resetForm() {
        // Reset form data when node type changes
        this.formData = {
          SerialNumber: "",
          AlarmState: false,
          TamperState: false,
          Latitude: "",
          Longitude: "",
          Charge: "",
          SignalStrength: "",
          Label: "" // Reset Label
        };
      },
      async submitData() {
        // Set up the payload dynamically based on node type
        let payload = { ...this.formData };
        if (this.nodeType === "CN") {
          // Camera Node
          payload = {
            SerialNumber: this.formData.SerialNumber,
            Label: this.formData.Label,
            Latitude: this.formData.Latitude,
            Longitude: this.formData.Longitude,
            Charge: this.formData.Charge,
            SignalStrength: this.formData.SignalStrength
          };
        } else if (this.nodeType === "SN") {
          // Sensor Node
          payload = {
            SerialNumber: this.formData.SerialNumber,
            AlarmState: this.formData.AlarmState,
            TamperState: this.formData.TamperState,
            Latitude: this.formData.Latitude,
            Longitude: this.formData.Longitude,
            Charge: this.formData.Charge,
            SignalStrength: this.formData.SignalStrength
          };
        }
  
        // Send POST request
        try {
          const response = await fetch(`http://${this.$apiIp}:5000/input_data`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
          });
          const result = await response.json();
          this.responseMessage = JSON.stringify(result, null, 2);
        } catch (error) {
          this.responseMessage = "Error: " + error.message;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .input-data-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 10px;
  }
  
  label {
    display: block;
    margin: 10px 0 5px;
  }
  
  input,
  select {
    width: 100%;
    padding: 8px;
    margin-bottom: 10px;
  }
  
  pre {
    background-color: #f4f4f4;
    padding: 10px;
    border-radius: 5px;
  }
  </style>
  