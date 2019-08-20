import axios from 'axios'

const mockserver = "http://localhost:4000";

export default axios.create({
    baseURL: mockserver
})