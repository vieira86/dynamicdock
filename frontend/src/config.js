const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000'
};

console.log('API URL:', config.apiUrl); // Debug line

export default config;
