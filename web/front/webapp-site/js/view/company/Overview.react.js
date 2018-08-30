var React = require('react');
var $ = require('jquery');

var CompanyStore = require('../../store/CompanyStore');
var CompanyAction = require('../../action/CompanyAction');

var Section = require('./Section.react');
var OverviewNav = require('./OverviewNav.react');
var CompanyHeader = require('./CompanyHeader.react');
var CompanyBasic = require('./CompanyBasic.react');


var Functions = require('../../../../react-kit/util/Functions');

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
            var company = this.state.data.company;

            var roundName = Functions.getRoundName(company.round);
            console.log(company);

            //var sections = [];
            //var section_basic = {header: "公司信息", data: [{name:"简介", content: company.description}]}
            //sections.push(section_basic);


            var id = 0;
            return (
                <div>

                    <CompanyHeader data={company} />

                    <OverviewNav />

                    <CompanyBasic data={company} />


                </div>

            );
        }
    },

    _onChange(){
        this.setState({data: CompanyStore.get()});
    }

});







module.exports = Overview;

