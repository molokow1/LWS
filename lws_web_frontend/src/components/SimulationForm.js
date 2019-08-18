import React, { Component } from "react";
import axios from "axios";
import { makeStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
// export default function SimulationForm() {
//   return (
//     <div>
//       <h1>HELLO WORLD</h1>
//     </div>
//   );
// }
const useStyles = makeStyles(theme => ({
  button: {
    margin: theme.spacing(1)
  },
  input: {
    display: "none"
  }
}));

export default class SimulationForm extends React.Component {
  componentDidMount() {
    axios.get("/sim_result").then(res => {
      console.log(res.data);
    });
  }

  render() {
    return (
      <div>
        <h1>HELLO</h1>
        <Button variant="outlined" color="primary">
          Test Button
        </Button>
      </div>
    );
  }
}
