var React = require('react');
var $ = require('jquery');


var SourceActionUtil = require('../../../action/source/SourceActionUtil');
var SourceFundingAction = require('../../../action/source/SourceFundingAction');
var SourceFundingStore = require('../../../store/source/SourceFundingStore');


function get(){
   return SourceFundingStore.get();
}

function getArr(){
    return SourceFundingStore.getArr();
}


var PropsSetOrChangeMixin = {
    componentWillMount: function() {
        this.onPropsSetOrChange(this.props.id);
    },

    componentWillReceiveProps: function(nextProps) {
        this.onPropsSetOrChange(nextProps.id);
    }
};


var SourceFundingRound = React.createClass({

    mixins: [PropsSetOrChangeMixin],


    onPropsSetOrChange(id){
        var state = this.state;
        var store = get();
        var arr = getArr();

        if(store == null || state == null){
            SourceFundingAction.get(id);
        }else if (store.id != id){
            SourceFundingAction.get(id);
        }

    },

    componentDidMount(){
        SourceFundingStore.addChangeListener(this._onChange);
    },

    //componentWillUnmount(){
    //    SourceFundingStore.removeChangeListener(this._onChange);
    //},

    render: function(){
        var state = this.state;
        if (state == null){
            return(<div></div>)
        }else{
            return(
                <div className="right-part">
                    <SourceList data={state.source} />
                </div>
            )
        }
    },

    _onChange() {
        var store = get();

        if (store != null)
            this.setState({source: store.data});
    }
});

var SourceList = React.createClass({
    render: function(){
        var filter = {
            round: '轮次',
            roundDesc: '轮次描述',
            investment: '投资金额',
            currency:'货币',
            precise: '精确性',
            fundingDate: '投资时间',
            preMoney: '投前估值',
            postMoney: '投后估值'
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


                <div className="source-detail">
                    { this.props.data.detail.map(function(result){
                        return  <SourceElement data={result} />;
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


module.exports = SourceFundingRound;