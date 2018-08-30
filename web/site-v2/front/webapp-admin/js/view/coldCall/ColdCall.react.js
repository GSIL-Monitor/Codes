var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var ColdCallActions = require('../../action/ColdCallActions');
var ColdCallStore = require('../../store/ColdCallStore');
var ColdCallList = require('./ColdCallList.react');
var Loading = require('../../../../react-kit/basic/Loading.react');
var View = require('../../../../react-kit/util/View');

const PropsSetOrChange = {
    componentWillMount() {
        this.onPropsSetOrChange(this.props.type);
    },

    componentWillReceiveProps(nextProps) {
        this.onPropsSetOrChange(nextProps.type);
    }
};

const ColdCall = React.createClass({

    mixins: [Reflux.connect(ColdCallStore, 'data'), PropsSetOrChange],

    onPropsSetOrChange(type) {
        ColdCallActions.getInitData(type);
    },

    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },

    render(){
        if(Functions.isEmptyObject(this.state)){
            return null;
        }
        var total = this.state.data.total;
        var match_total = this.state.data.match_total;
        var unmatch_total = this.state.data.unmatch_total;
        var data = this.state.data;
        var loading;
        if(data.loading) loading = <Loading />;

        return (
            <div className="main-body">

                <div className="admin-head ">
                    <h3 >Cold Call</h3>
                </div>
                <div>
                <ul className="tab-ul">
                    <ColdCallItem type="0"
                                  name="待匹配的coldCall"
                                  count={unmatch_total}
                                  data={data}
                                />
                    <ColdCallItem type="1"
                                  name="已匹配的coldCall"
                                  count={match_total}
                                  data={data}
                                 />
                    <li className="tab-li tab-li-xl admin-task-count">
                        <span>总数:</span>
                        <span className="m-l-10">{total}</span>
                    </li>

                </ul>

                    </div>
                <div>
                <ColdCallList  data={data}/>
                    {loading}
                </div>
            </div>
      )
    },
    scroll(){
        if(View.bottomLoad(100)){
            ColdCallActions.listMore(this.state.data.coldCall_Type);
        }
    }

});

const ColdCallItem=React.createClass({
    render(){
        var className= "tab-li tab-li-xl ";
        var couDiv;
        var count= this.props.count>99?99:this.props.count;
        var count_className="match-count ";
        if(this.props.type == this.props.data.coldCall_Type){
            className += "active";
        }
        if(this.props.type==1){
            count_className+=" count_bg"
        }
        if(this.props.count > 0){
            couDiv = <div className={count_className}>{count}</div>
        }

        return (
            <li className={className}>
                <a onClick={this.click}>
                    {this.props.name}
                    {couDiv}
                </a>
            </li>
        )
    },

    click(){
        ColdCallActions.changeType(parseInt(this.props.type));
    }

});


module.exports = ColdCall;

