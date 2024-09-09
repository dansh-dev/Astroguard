import { createMemoryHistory, createRouter } from 'vue-router'

import  AstroguardMainScreen from './components/AstroguardMainScreen.vue'
import AstroguardInitialSetup from './components/AstroguardInitialSetup.vue'
import AstroguardNameSetting from './components/SystemNameSetting.vue'
import PasscodeSetting from './components/PasscodeSetting.vue'
import AstroguardFacialSetup from './components/FacialRecognitionSetup.vue'
import AddSensors from './components/AddSensors.vue'
import FinalizeSetup from './components/FinalizeSetup.vue'
import SettingsScreen from './components/SettingsScreen.vue'
import SensorList from './components/SensorList.vue'
import SensorDetails from './components/SensorDetails.vue'
import websocketTest from './components/websocket.vue'
import SensorEmulation from './components/SensorEmulation.vue'

const routes = [
  { path: '/main', component: AstroguardMainScreen },
  { path: '/getstarted', component: AstroguardInitialSetup },
  { path: '/systemname', component: AstroguardNameSetting },
  { path: '/systempasscode', component: PasscodeSetting },
  { path: '/AstroguardFacialSetup', component: AstroguardFacialSetup },
  { path: '/AddSensors', component: AddSensors },
  { path: '/FinalizeSetup', component: FinalizeSetup },
  { path: '/SettingsScreen', component: SettingsScreen },
  {path: '/SensorList', component: SensorList},
  { 
    path: '/SensorDetails/:serialNumber', 
    name: 'SensorDetails',  // Add this line
    component: SensorDetails, 
    props: true 
  },
  { path: '/websocket', component: websocketTest},
  {path: '/emulator', component: SensorEmulation}
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router