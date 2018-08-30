var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');

const Data = React.createClass({
    mixins: [Reflux.connect(CompanyStore, 'data')],

    componentDidMount() {
        var id = this.props.id;
        //CompanyActions.getData(id);
    },

    render(){

        return(
            <div className="section">
                <span className="section-header">
                    用户数据
                </span>

                <section className="section-body">

                </section>


            </div>

        )
    }

});




module.exports = Data;