const baseURL = process.env.NODE_ENV === "development" ? "http://localhost:8000/api" : "https://theforevercanvas.com/api"

module.exports = { baseURL }