var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ColdcallActions= require('../../action/ColdcallActions');
var Functions = require('../../../../react-kit/util/Functions');
var Select = require('../../../../react-kit/form/Select.react.js');

const Forward = React.createClass({
    render(){
        var data = this.props.data;

        return(
            <div>
                <ForwardSteps data={data} />
                <Colleagues data={data}/>
            </div>
        )
    }
});


const ForwardSteps = React.createClass({
   render(){
       var data = this.props.data;
       var forward_steps =data.forward_steps;
       if(forward_steps == null) return null;
       if(forward_steps.length == 0) return null;
       return(
           <div>
               <h4>转发状态</h4>
               <div className="cc-forward-steps">
                   {forward_steps.map(function (result,index) {
                       return <Step data={result}  key ={index} />
                   })}
                </div>
           </div>
       )
   }
});


const Step = React.createClass({
    render(){
        var data = this.props.data;
        var fromUser =data.fromUserName;
        var toUser = data.toUserName;
        if(null==fromUser){
            fromUser='系统分配';
        }
        return(
            <div className="cc-forward-step">
                {fromUser} -- {toUser}
            </div>
        )
    }
});


const Colleagues = React.createClass({

    render(){
        var data= this.props.data;
        var select = data.collegues;
        var value = data.forwardUser;

        var forwardBtn;
        if(value == null || value == 0){
            forwardBtn =  <button className="btn btn-gray btn-forward disabled m-l-20">转发</button>
        }else{
            forwardBtn =  <button className="btn btn-navy btn-forward m-l-20" onClick={this.click}>转发</button>
        }

        return(
            <div>
                <div className="left">
                    <Select id="select-forward"
                            value={value}
                            select={select}
                            onChange={this.change}/>
                </div>

                <div className="left">
                    {forwardBtn}
                </div>

            </div>
        )
    },

    change(e){
        ColdcallActions.selectForwardUser(e.target.value);
    },
    click(){
        ColdcallActions.forward();
    }

});


const Colleague = React.createClass({
    render(){
        return null;
    }
});


module.exports = Forward;