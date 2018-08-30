var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');


const Gongshang = React.createClass({

    render(){
        var data = this.props.data;
        if (data.length == 0) return null;

        return (
            <div className="float-more-desc" id="gongshang" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <a className="more-desc-close" onClick={this.ccClose}>关闭</a>

                <span className="section-header">
                    工商信息
                </span>

                <div className="m-t-20">
                    {data.map(function(result,index){
                        return <Item data={result} key={index} />
                    })}
                </div>
            </div>

        )
    },

    onMouseOver(){
        document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        document.body.style.overflow = 'auto';
    },

    ccClose(){
        $('.float-more-desc').hide();
    }

});


const Item = React.createClass({
    render(){
        var gongshang = this.props.data;
        var data = gongshang.data;
        return(
            <div className="gongshang-item">
                <div className="gongshang-name"> {gongshang.name} </div>
                <div> 成立时间：{data.fromTime}</div>
                <div> 注册资本：{data.regCapital}</div>
                <div> 注册地点：{data.base}</div>
                <div> 登记机关：{data.regInstitute}</div>
                <div> 法人：{data.legalPersonName}</div>
            </div>
        )
    }
});


module.exports = Gongshang;