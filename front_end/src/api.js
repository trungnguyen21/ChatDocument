import axios from 'axios';

axios.defaults.baseURL = 'https://stingray-app-puj9w.ondigitalocean.app';

const api = axios.create({
  baseURL: process.env.APP_API_URL,
});

export default api;
