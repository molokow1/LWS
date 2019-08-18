const jsonServer = require("json-server");
const casual = require("casual");
const { sim_result, sim_form } = require("./data.js");
const server = jsonServer.create();
const middlewares = jsonServer.defaults();
const port = process.env.PORT || 3000;

server.use(jsonServer.bodyParser);
server.use(middlewares);

// Add custom routes before JSON Server router
server.get("/echo", (req, res) => {
    res.jsonp(req.query);
});

server.get("/sim_result", (req, res) => {
    res.json(sim_result);
});

server.get("/sim_form", (req, res) => {
    res.json(sim_form);
})
server.listen(port, () => {
    console.log("JSON Server is running");
});
