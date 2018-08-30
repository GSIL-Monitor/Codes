var React = require('react');
var $ = require('jquery');
var Functions = require('../../../../../react-kit/util/Functions');

const MoreDesc = React.createClass({

    render(){
        var data = this.props.data;
        return (
            <div className="float-more-desc" id="more-desc" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <a className="more-desc-close" onClick={this.ccClose}>关闭</a>

                <div className="more-desc-list">
                    <DescItem name="产品描述" data={data.productDesc}/>
                    <DescItem name="产品模型" data={data.modelDesc}/>
                    <DescItem name="竞争优势" data={data.operationDesc}/>
                    <DescItem name="团队优势" data={data.teamDesc}/>
                    <DescItem name="市场行情" data={data.marketDesc}/>
                    <DescItem name="竞争对手分析" data={data.compititorDesc}/>
                    <DescItem name="项目壁垒" data={data.advantageDesc}/>
                    <DescItem name="项目计划" data={data.planDesc}/>
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

const DescItem = React.createClass({
    render(){
        var data= this.props.data;
        if(Functions.isNull(data))
            return null;
        return <div>
                    <p>{this.props.name}</p>
                    <pre>{data}</pre>
                </div>
    }
});



module.exports = MoreDesc;