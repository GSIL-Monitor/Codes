var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserHomeStore = require('../../store/UserHomeStore');
var UserHomeActions = require('../../action/UserHomeActions');

var Functions = require('../../../../react-kit/util/Functions');



const UserHome = React.createClass({

    mixins: [Reflux.connect(UserHomeStore, 'data')],

    componentWillMount() {
        UserHomeActions.init(this.props.type);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.type == nextProps.type) return;
        UserHomeActions.init(nextProps.type);
    },


    render() {
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var selected = data.type;


        if(this.props.from == 'mobile'){
            return(
                <div className="m-home-nav">
                    <UserHomeItem count={data.cnt_task} selected={selected} type="task" name="我的任务" />
                    <UserHomeItem count={data.cnt_publish}  selected={selected} type="publish" name="发布的任务" />
                    <UserHomeItem count={data.cnt_discovery}  selected={selected} type="discovery"  name="我的发现" />
                </div>
            )
        }

        return(
            <div className="user-home">
                <div className="user-home-list">

                    <UserHomeItem count={data.cnt_task} selected={selected} type="task" name="我的任务" />
                    <UserHomeItem count={data.cnt_publish}  selected={selected} type="publish" name="发布的任务" />
                    <UserHomeItem count={data.cnt_discovery}  selected={selected} type="discovery"  name="我的发现" />

                </div>
            </div>

        )
    }

});


const UserHomeItem = React.createClass({
    render(){
        var count = this.props.count;
        if(count > 0){
            count = count > 99?99:count;
            count = <div className="task-count">{count}</div>
        }else{
            count = null;
        }

        var className;
        if(this.props.selected == this.props.type){
            className = 'active';
        }

        return (
            <div className= {className} onClick={this.click}>
                <span className="left">{this.props.name}</span>
                {count}
            </div>
        )
    },

    click(){
        UserHomeActions.changeTask(this.props.type);
    }
});







module.exports = UserHome;

