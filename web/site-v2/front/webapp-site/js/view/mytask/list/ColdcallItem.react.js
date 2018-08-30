var React = require('react');
var TaskUtil = require('../../../util/TaskUtil');
var CompanyInfo = require('../../../../../react-kit/company/CompanyInfo.react');


const ColdcallItem = React.createClass({
    render(){
        var data = this.props.data;
        var descClass = "item-description ";
        if (this.state != null) {
            if (this.state.selected)
                descClass = descClass + "auto-height";
        }

        var coldcallLink = "./#/coldcall/" + data.coldcallId + "/overview";
        var link = "/#/company/" + data.companyCode + "/overview";
        if (data.companyCode != null) {
            link = "./#/company/" + data.companyCode + "/overview";
        }
        else {
            link = coldcallLink;
        }
        var strScore;
        if(!this.props.admin){
            strScore= <span className="item-status">{TaskUtil.getScoreName(data.score)}</span>
        }

        var createTime = new Date(data.coldcallCreateTime).format("yyyy-MM-dd hh:mm:ss");

        var match;
        var hint;
        if(data.companyName==null){
            hint = <div className='task-hint-todo'></div>;
            match = <a className="match-error" href={link}>
                未找到相应公司
            </a>
        }else{
            if(data.score == null || data.score == 0)
                hint = <div className='task-hint-todo'></div>;
            match =  <CompanyInfo className="match-info" code={data.companyCode} name={data.companyName}/>
        }

        var sponsor = data.sponsor;
        if(sponsor ==null){
            sponsor = 'N/A';
        }


        return(
            <div className="search-list-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                {hint}
                <div className="item-head task-head">
                    <a className="item-name" href={coldcallLink} >{data.coldcallName}</a>
                    {strScore}
                    {match}

                </div>
                <div className={descClass}>{data.content}</div>
                <div className="item-meta">
                    <div>来源: {sponsor}</div>
                    <div className="soft-text">{createTime}</div>
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

module.exports = ColdcallItem;