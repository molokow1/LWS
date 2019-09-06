import React from "react";
import { Route, Switch } from "react-router-dom";
import SimulationForm from "./SimulationForm";
import DevicePositionPlot from "./DevicePositionPlot";
import "./App.css";

function App() {
  return (
    <Switch>
      <Route exact path="/" component={SimulationForm} />
      <Route path="/plot" component={DevicePositionPlot} />
    </Switch>
  );
}

export default App;
