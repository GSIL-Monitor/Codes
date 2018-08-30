var React = require('react');
var TaskUtil = require('../../../util/TaskUtil');

var CompanyInfo = require('../../../../../react-kit/company/CompanyInfo.react');

const CompanyItem = React.createClass({
    render(){
        var data = this.props.data;
        var descClass = "item-description ";
        if (this.state != null) {
            if (this.state.selected)
                descClass = descClass + "auto-height";
        }
        var time;
        if(data.assignTime != null)
            time = new Date(data.assignTime).format("yyyy-MM-dd hh:mm:ss");
        else
            time = new Date(data.coldcallCreateTime).format("yyyy-MM-dd hh:mm:ss");

        var strScore = TaskUtil.getScoreName(data.score);
        var hint;
        if(data.score == 0 || data.score == null)
            hint = <div className='task-hint-todo'></div>;

        var from = this.props.from;
        var source;
        if(from == 'recommend'){
            source = <div>来源: 系统分配</div>
        }

        return(
            <div className="search-list-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                {hint}
                <div className="item-head">
                    <CompanyInfo className="item-name" code={data.companyCode} name={data.companyName}/>
                    <span className="item-status">{strScore}</span>
                </div>
                <div className={descClass}>{data.content}</div>
                <div className="item-meta">
                    {source}
                    <div className="soft-text">{time}</div>
                </div>
            </div>
        )
    },

    onMouseOver(){
        this.setState({selected: true})
    },

    onMouseOut(){
        this.setState({selected: false})
    }

});

module.exports = CompanyItem;