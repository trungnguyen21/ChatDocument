import axios from 'axios';

axios.defaults.baseURL = 'https://stingray-app-puj9w.ondigitalocean.app';
axios.defaults.proxy.host = "https://stingray-app-puj9w.ondigitalocean.app"

const api = axios.create({
  baseURL: 'https://stingray-app-puj9w.ondigitalocean.app',
});

export default api;
