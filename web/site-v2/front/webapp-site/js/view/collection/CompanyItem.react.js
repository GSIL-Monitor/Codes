var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var CompanyInfo = require('../../../../react-kit/company/CompanyInfo.react');
var SectorList = require('../../../../react-kit/company/SectorList.react');
var TagList = require('../../../../react-kit/company/TagList.react');
var CollectionUtil = require('../../util/CollectionUtil');
var CollectionActions = require('../../action/collection/CollectionActions');

const CompanyItem = React.createClass({

    render(){
        //var data = this.props.data.company;
        var data  = this.props.data;
        var collection = this.props.data.collection;
        var updateTime = this.props.data.updateTime;
        var score = this.props.data.score;
        var descClass = "item-description ";
        if (this.state != null) {
            if (this.state.selected)
                descClass = descClass + "auto-height";
        }
        var time;
        if (updateTime) {
            time = CollectionUtil.countDateDiff(updateTime);
        }

        var roundName = Functions.getRoundName(data.round);

        var establishDate = data.establishDate;
        if (establishDate != null) {
            establishDate = establishDate.substring(0, 7);
        }

        var location = data.location;
        if (location != null) {
            location = "@" + location;
        }
        var hot;
        var warm;
        if (score == 4) {
            hot = <div className="followed-hot">
                <i className="fa fa-check"></i>
                重点跟进
            </div>;
            warm = <div className="follow-warm" onClick={this.warm}>
                <i className="fa fa-plus"></i>
                随便聊聊
            </div>

        }
        else if (score == 3) {
            hot = <div className="follow-hot" onClick={this.hot}>
                <i className="fa fa-plus"></i>
                重点跟进
            </div>;
            warm = <div className="followed-warm">
                <i className="fa fa-check"></i>
                随便聊聊
            </div>
        }
        else {

            hot = <div className="follow-hot" onClick={this.hot}>
                <i className="fa fa-plus"></i>
                重点跟进
            </div>;
            warm = <div className="follow-warm" onClick={this.warm}>
                <i className="fa fa-plus"></i>
                随便聊聊
            </div>
        }

        collection = {name:'FA每日精选'};

        return (
            <div className="timeline-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <div className="collect-time">{time}</div>
                <div className='timeline-collection'>
                    <div onClick={this.click}>{collection.name}</div>
                </div>

                <div className="timeline-info">
                    <div className="item-head">
                        <CompanyInfo className="item-name" code={data.code} name={data.name}/>
                        <span className="item-round">{roundName}</span>
                        <SectorList data={data.sectors}/>

                        <div className="timeline-operate">
                            {hot}
                            {warm}
                        </div>
                    </div>

                    <div className={descClass}>{data.description}</div>
                    <div className="item-meta">
                        <TagList data={data.tags}/>
                    </div>
                    <div className="item-meta">
                        <div className="left m-r-20">
                            {establishDate} {location}
                        </div>
                    </div>

                </div>

            </div>
        )
    },

    onMouseOver(){
        this.setState({selected: true})
    },

    onMouseOut(){
        this.setState({selected: false})
    },

    warm(){
        CollectionActions.dealUserScore(3,this.props.data.company.code);
    },

    hot(){
        CollectionActions.dealUserScore(4,this.props.data.company.code);
    },

    click(){
        window.location.href = '/#/collection/'+this.props.data.collection.id
    }

});

module.exports = CompanyItem;
