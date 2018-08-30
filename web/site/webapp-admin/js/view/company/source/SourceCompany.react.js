var React = require('react');
var $ = require('jquery');


var SourceActionUtil = require('../../../action/source/SourceActionUtil');
var SourceCompanyAction = require('../../../action/source/SourceCompanyAction');
var SourceCompanyStore = require('../../../store/source/SourceCompanyStore');


var SourceCompany = React.createClass({

    getInitialState: function(){
        return {data: []};
    },

    componentDidMount() {
        SourceCompanyAction.get(this.props.id);
        SourceCompanyStore.addChangeListener(this._onChange);
    },

    render: function(){
        return(
            <div className="right-part">
                <SourceList data={this.state.data} />
            </div>
        )
    },

    _onChange() {
        var store = SourceCompanyStore.get();

        if (store != null)
            this.setState({data: store});
    }
});

var SourceList = React.createClass({
    render: function(){
        var filter = {
            name: '名称',
            fullName: '全称',
            description: '描述',
            brief: '简介',
            establishDate: '建立时间',
            headCountMin: '最小人数',
            headCountMax: '最大人数',
            locationId: '地址',
            address: '详细地址',
            phone: '联系电话'
        };

        var source = SourceActionUtil.sourceFilter(this.props.data, filter);

        return(
            <div>

                <div className="source-list">
                    { source.map(function(result){
                        return  <SourceDetail key={result.id} data={result} />;
                    })}
                </div>
            </div>
        )
    }

});


var SourceDetail =  React.createClass({

    render: function(){
        return(
            <div className="source-info">
                <div className="source-head"
                     onClick={this.handleClick}>
                    <label>{this.props.data.head.sourceName}</label>
                    <a href= {this.props.data.head.sourceUrl} target="_blank">
                        <i className="fa fa-link fa-lg"> </i>
                    </a>
                </div>

                <div className="source-detail">
                    { this.props.data.detail.map(function(result){
                        return  <SourceElement key={result} data={result} />;
                    })}

                </div>
            </div>
        )
    }
});

var SourceElement = React.createClass({
    render(){
        return(
            <div>
                {this.props.data}
            </div>
        )
    }
});


module.exports = SourceCompany;