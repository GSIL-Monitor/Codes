var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompsStore = require('../../../store/company/CompsStore');
var CompsActions = require('../../../action/company/CompsActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');
var FundingList = require('../develop/FundingList.react');
var ButtonAdd = require('../../../../../react-kit/basic/ButtonAdd.react');

var AddCompsList = require('../modal/comps/AddCompsList.react');

const UpdateComps = React.createClass({

    render(){
        if (Functions.isEmptyObject(this.props.data))
            return null;

        var data = this.props.data.updateList;
        var comps;
        if(data.length > 0){
            comps= data.map(function (result, index) {
                        return <CompItem key={index} data={result}/>;
                    })
        }


        return (
            <div className="section">
                <span className="section-header">
                    竞争对手
                </span>

                <span>
                    <a className="update-company" onClick={this.comfirm}>
                        确定
                    </a>

                    <a className="update-company" onClick={this.update}>
                        取消
                    </a>
                </span>

                <section className="section-body update-comps-body">
                    {comps}
                    <AddCompsList data={this.props.data.newList}/>
                </section>

                <ButtonAdd onClick={this.add} />
            </div>

        )
    },

    extend(){
        CompsActions.showAll();
    },

    update(){
        CompsActions.update();
    },

    comfirm(){
        CompsActions.submit();
    },

    add(){
        $('#add-comps-modal').show();
    }


});


const CompItem = React.createClass({
    render(){
        var data = this.props.data;
        var descClass = "item-description ";

        var roundName = Functions.getRoundName(data.round);
        var link = "../#/company/"+data.code+"/overview";

        var establishDate = data.establishDate;
        if(establishDate != null){
            establishDate = establishDate.substring(0,7);
        }

        var location = data.location;
        if(location != null){
            location = "@"+location;
        }

        return(
            <div className="comps-list-item update-comps-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <div className="comps-close">
                    <i className="fa fa-times fa-lg label-close right" onClick={this.delete}></i>
                </div>
                <div className="item-head">
                    <div className="left m-r-10">
                        <a className="comps-name update-comps-name" href={link} target="_blank" >{data.name}</a>
                    </div>
                    <div className="left m-r-10">{roundName}</div>
                </div>

                <div className={descClass}>{data.description}</div>
                <div>{establishDate} {location}</div>
            </div>
        )
    },

    onMouseOver(){
        this.setState({selected: true})
    },

    onMouseOut(){
        this.setState({selected: false})
    },

    delete(){
        CompsActions.delete(this.props.data.id);
    }

});

const TagItem = React.createClass({
    render(){
        return(
            <span className="label tag light-tag">
               {this.props.data}
            </span>
        )
    }
});


module.exports = UpdateComps;