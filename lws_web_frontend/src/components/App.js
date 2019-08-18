import React from "react";
import { Route, Switch } from "react-router-dom";
import SimulationForm from "./SimulationForm";
import "./App.css";

function App() {
  return (
    <Switch>
      <Route exact path="/" component={SimulationForm} />
    </Switch>
  );
}

export default App;
