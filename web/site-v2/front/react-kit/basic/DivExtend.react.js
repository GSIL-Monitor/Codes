var React = require('react');
var $ = require('jquery');

const DivExtend = React.createClass({
    render(){
        var type = this.props.type;
        var extend;
        if(type == 'less'){
            extend = <a className="a-button a-extend" onClick={this.extend}>
                        收起<i className="fa fa-angle-up m-l-5"></i>
                    </a>
        }else{
            extend = <a className="a-button a-extend" onClick={this.extend}>
                展开<i className="fa fa-angle-down m-l-5"></i>
            </a>
        }

        return (
                <div className="div-extend">
                    {extend}
                </div>
            )
    },

    extend(){
        this.props.extend();
    }
});


module.exports = DivExtend;
