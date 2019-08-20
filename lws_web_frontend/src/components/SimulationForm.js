import React, { Component } from "react";
import API from './API'
import { makeStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";


function AllSelectElements(props) {
    var ret = []
    const settings = props.settings
    for (let s in settings) {
        console.log(s)
        console.log(settings[s].selections)
        ret.push(
            <SelectElement label={s} selections={settings[s].selections} />
        )
    }
    return ret
}

function SelectElement(props) {
    return (
        <React.Fragment>
            <InputLabel htmlFor={props.label}>
                {props.label}
            </InputLabel>
            <Select value="test" inputProps={{
                name: props.label,
                id: props.label,
            }}>
                <MenuItems selections={props.selections} />
            </Select>
        </React.Fragment>
    )
}

function MenuItems(props) {
    var ret = []
    for (var s in props.selections) {
        ret.push(
            <MenuItem value={s}>{props.selections[s]}</MenuItem>
        )
    }
    return ret
}

export default class SimulationForm extends Component {
    constructor(props) {
        super(props);
        this.state = { formdata: null }

    }

    componentDidMount() {
        // // const data = this.obtainFormData();
        // const res = await API.get('/sim_form');
        // this.setState({ formdata: res.data })
        // return Promise.resolve()
        API.get("/sim_form").then(res => {
            if (res) this.setState({ formdata: res.data })
        })
    }

    render() {
        // console.log(this.state.formdata.regional_settings)
        if (!this.state.formdata) {
            return (
                <div>
                    <h1>loading..</h1>
                </div>
            );
        } else {
            const form = this.state.formdata
            console.log(form)
            return (
                <div>
                    <h1>Simulation Parameters</h1>
                    <form action="">
                        <h1>{form.regional_settings.header}</h1>
                        <FormControl>
                            <AllSelectElements settings={form.regional_settings.settings} />
                        </FormControl>
                    </form>
                </div>
            );

        }

    }
}
