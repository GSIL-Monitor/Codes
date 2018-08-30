var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FundingContent = require('../company/modal/funding/FundingContent.react');
var FooptrintContent = require('../company/modal/footprint/FootprintContent.react');
var TagContent = require('../company/modal/tag/TagContent.react');

var JobContent = require('../company/modal/team/JobContent.react');
var MemberContent = require('../company/modal/team/MemberContent.react');
var CompsContent = require('../company/modal/comps/CompsContent.react');

var Decision = require('../demoDay/score/modal/Decision.react');

var CollectionFilter = require('../collection/modal/CollectionFilter.react');

var Modal = React.createClass({

    render(){
        var content;
        var type = this.props.type;
        var comfirmName = this.props.comfirmName;
        var data = this.props.data;

        if(type == 'addFunding' || type == 'updateFunding'){
            content =  <FundingContent name={comfirmName} data={data} type={type}/>;
        }
        else if(type == 'addTag'){
            content = <TagContent name={comfirmName} data={data} />
        }
        else if(type == 'addFootprint' || type == 'updateFootprint'){
            content = <FooptrintContent  name={comfirmName} data={data}  type={type} />
        }
        else if(type == 'job'){
            content = <JobContent data={data}  />
        }
        else if(type == 'member'){
            content = <MemberContent data={data}  />
        }
        else if(type == 'addComps'){
            content = <CompsContent name={comfirmName} data={data} />
        }
        else if(type == 'demodayDecision'){
            content = <Decision data={data}/>
        }else if(type = 'collectionFilter'){
            content = <CollectionFilter name={comfirmName} data={data} />
        }

        return (
            <div className="modal" id={this.props.id}>
                <div className="modal-mask" onClick={this.handleCancel}></div>
                <div className="modal-body" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    <div className="modal-header">
                        <span className="modal-name">{this.props.name}</span>

                        <div className="close right" onClick={this.handleCancel}>
                            <span>×</span>
                        </div>
                    </div>

                    <div className="modal-content">
                        {content}
                    </div>

                </div>
            </div>

        )
    },


    handleCancel(){
        $('.modal').hide();
    },

    handleComfirm(){
        this.props.comfirm();
        $('.modal').hide();
    },

    onMouseOver(){
        document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        document.body.style.overflow = 'auto';
    }

});


module.exports = Modal;