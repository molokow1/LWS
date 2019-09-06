import Chart from "chartjs";
import React, { Component } from "react";
// import { Bubble } from 'react-chartjs-2';

const data = {
    labels: ['January'],
    datasets: [
        {
            label: 'My First dataset',
            fill: false,
            lineTension: 0.1,
            backgroundColor: 'rgba(75,192,192,0.4)',
            borderColor: 'rgba(75,192,192,1)',
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderColor: 'rgba(75,192,192,1)',
            pointBackgroundColor: '#fff',
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: 'rgba(75,192,192,1)',
            pointHoverBorderColor: 'rgba(220,220,220,1)',
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data: [{ x: 10, y: 20, r: 5 }]
        }
    ]
};
class ScatterPlot extends Component {
    constructor(props) {
        super(props);
        this.chartRef = React.createRef();
    }

    componentDidMount() {
        // const node = this.node;
        this.scatterPlot = new Chart(this.chartRef.current, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Scatter Dataset',
                    data: [{
                        x: -10,
                        y: 0
                    }, {
                        x: 0,
                        y: 10
                    }, {
                        x: 10,
                        y: 5
                    }]
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'linear',
                        position: 'bottom'
                    }]
                }
            }
        });
    }

    render() {
        return (
            <canvas
                id="scatterPlot"
                style={{ width: 800, height: 300 }}
                ref={this.chartRef}
            />

        )
    }
}

export default class DevicePositionPlot extends Component {

    constructor(props) {
        super(props);
        // props should include the data necessary to plot

    }

    componentDidMount() {
        console.log("plot mounted");
    }

    render() {
        return (

            <div className="App">
                <h1>Plot</h1>
                {/* <Bubble data={data} /> */}
                <ScatterPlot />
            </div>



        );
    }
}