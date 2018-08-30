var React = require('react');
var $ = require('jquery');

var CompanyStore = require('../../store/CompanyStore');
var CompanyAction = require('../../action/CompanyAction');


var Config = require('../../util/Config');
var Functions = require('../../util/Functions');

const Overview = React.createClass({

    componentDidMount() {
        var code = this.props.code;
        CompanyAction.get(code);
        CompanyStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        CompanyStore.removeChangeListener(this._onChange);
    },

    render() {
        var state = this.state;

        if(state == null){
            return null;
        }
        else{
            return (
                <div>
                    <h3>{this.state.data.company.name}</h3>
                </div>
            );
        }
    },

    _onChange(){
        this.setState({data: CompanyStore.get()});
    }

});




module.exports = Overview;

