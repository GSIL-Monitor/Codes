var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var ButtonAdd = require('../../../../../react-kit/basic/ButtonAdd.react');

var UpdateInput = require('./UpdateInput.react');
var AddFootprintList = require('../modal/footprint/AddFootprintList.react');

var old_footprints;
const UpdateFootprints = React.createClass({

    render(){
        var footprints;
        old_footprints = this.props.old;
        if(this.props.data.length > 0)
            footprints = this.props.data.map(function (result, index) {
                return <FootprintItem key={index} data={result}/>;
            })

        return(
            <section className="section-body">
                <div className="section-round">
                    <div className="section-name name4">
                        发展<br/>足迹
                    </div>
                </div>
                <div className="section-sub-item">
                    {footprints}
                    <AddFootprintList data={this.props.newFootprints}/>

                    <ButtonAdd onClick={this.add} />
                </div>
            </section>
        )
    },

    add(){
        $('#add-footprint-modal').show();
    }

});


const FootprintItem = React.createClass({
    render(){
        var data = this.props.data;
        var className= "label label-develop ";

        if(CompanyUtil.checkFootprintDiff(data, old_footprints))
            className += 'update';


        return(
            <div className={className} onClick={this.select}>
                <span>{data.footDate}</span>
                <span className="m-l-10">{data.description}</span>
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    select(){
        CompanyActions.selectFootprint(this.props.data);
    },

    delete(e){
        CompanyActions.deleteFootprint(this.props.data.id);
        $('#update-footprint-modal').hide();
        e.stopPropagation();
    }
});





module.exports = UpdateFootprints;