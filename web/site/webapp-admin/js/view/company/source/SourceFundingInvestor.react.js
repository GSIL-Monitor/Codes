var React = require('react');
var $ = require('jquery');


var SourceActionUtil = require('../../../action/source/SourceActionUtil');
var SourceFundingAction = require('../../../action/source/SourceFundingAction');
var SourceFundingStore = require('../../../store/source/SourceFundingStore');


function get(){
    return SourceFundingStore.getFundingInvestor();
}


var PropsSetOrChangeMixin = {
    componentWillMount: function() {
        this.onPropsSetOrChange(this.props.id);
    },

    componentWillReceiveProps: function(nextProps) {
        this.onPropsSetOrChange(nextProps.id);
    }
};


var SourceFundingInvestor = React.createClass({

    mixins: [PropsSetOrChangeMixin],

    onPropsSetOrChange(id){

        SourceFundingAction.getFundingInvestorRel(id);
    },

    componentDidMount(){
        SourceFundingStore.addInvestorChangeListener(this._onChange);
    },

    componentWillUnmount(){
        SourceFundingStore.removeChangeListener(this._onChange);
    },


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
            investment: '投资金额',
            currency:'货币',
            precise: '精确性'
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
        var id = -1;
        return(
            <div className="source-info">

                <div className="source-detail">
                    { this.props.data.detail.map(function(result){
                        return  <SourceElement key={id++} data={result} />;
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


module.exports = SourceFundingInvestor;