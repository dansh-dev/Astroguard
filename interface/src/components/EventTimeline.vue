<template>
    <h2 class="text-xl font-bold font-AXIS text-astro-guard-white mb-4">Event Timeline</h2>
    <div class="w-full justify-center items-center flex"><h3 class="text-astro-guard-white font-AXIS">NOW</h3></div>
    <div class="timeline-container">
        
      <div class="timeline">
        
        <div
          v-for="(event, index) in events"
          :key="index"
          class="timeline-item"
        >
          <div class="timeline-content">
            <div class="timestamp">{{ formatDate(event.timestamp) }}</div>
            <div class="title">{{ event.title }}</div>
            <div class="description">{{ event.message }}</div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "EventTimeline",
    props: {
    events: {
      type: Array,
      required: true
    }
  },
    data() {
      return {
      };
    },
    methods: {
      formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      },
    },
  };
  </script>
  
  <style>
  .timeline-container {
    display: flex;
    justify-content: center;
    padding: 20px;
    overflow-y: scroll;
  }
  
  .timeline {
    position: relative;
    margin: 20px 0;
    padding: 10px 0;
    width: 100%;
    max-width: 600px;
  }
  
  .timeline::before {
    content: '';
    position: absolute;
    width: 2px;
    background-color: #00ffaa;
    top: 0;
    bottom: 0;
    left: 50%;
    margin-left: -1px;
  }
  
  .timeline-item {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding: 10px 0;
    position: relative;
  }
  
  .timeline-item:nth-child(even) {
    justify-content: flex-end;
  }
  
  .timeline-item::before {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #00ff80;
    top: 15px;
    left: 50%;
    margin-left: -5px;
  }
  
  .timeline-content {
    max-width: 200px;
    background-color: #f9fafb;
    padding: 10px;
    border-radius: 8px;
    text-align: left;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .timestamp {
    font-size: 12px;
    color: #6b7280;
  }
  .title {
    margin-top: 4px;
    font-size: 18px;
    color: #111827;
  }
  .description {
    margin-top: 4px;
    font-size: 16px;
    color: #111827;
  }
  </style>
  