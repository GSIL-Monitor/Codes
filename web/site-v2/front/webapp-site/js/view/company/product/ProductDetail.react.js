var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var ProductActions = require('../../../action/company/ProductActions');
var Trends = require('./trends/BasicTrends.react');
var DivFindNone = require('../../../../../react-kit/basic/DivFindNone.react');
var ProductUtil = require('../../../util/ProductUtil');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');
var Pics = require('./Pics.react');
const ProductDetail = React.createClass({
    getInitialState(){
        return {
            showAll: false
        }
    },
    render(){

        var id = this.props.id;
        var data = this.props.data;
        var artifact = data.artifact;
        var className = 'pop-bottom ';
        var arrowClass = "arrow-up product-arrow ";
        var arrowClass2 = "arrow-up2 product-arrow2 ";
        var contentDetail;

        var briefClass;
        var trendsClass;
        var desc;
        var pics;
        var more;
        var descClass;
        var picClass;
        if (artifact.description != null) {
            desc = artifact.description
            var len = desc.length;
            if (len > 300) {
                if (this.state.showAll) {
                    descClass = "item-description auto-height";
                    picClass ="product-pics hidden-pics";
                    more = <div className="desc-extend">
                        <DivExtend type="less" extend={this.extend}/>
                    </div>
                }
                else {
                    descClass = "item-description ";
                    picClass ="product-pics ";
                    more = <div className="desc-extend">
                        <DivExtend type="more" extend={this.extend}/>
                    </div>
                }
            }

        }
        className += "product-detail-xl  product-detail-xl-" + id % 3;
        arrowClass += "product-arrow-xl-" + id % 3;
        arrowClass2 += "product-arrow2-xl-" + id % 3;

        if (data.pics.length == 1) {
            var url = '/file/' + data.pics[0].link;
            pics = <img className="product-pic-image" src={url}/>;

        } else if(data.pics.length>1){
            var images= ProductUtil.getImages(data.pics);
            pics=<Pics images={images} />
        }
        if (data.navType == 'brief') {
            briefClass = 'product-content-brief product-selected-primary';
            trendsClass = 'product-content-trends ';
            if (desc || pics) {
                contentDetail = <div>
                    <div className="product-content-basic">
                        <div className={descClass}>{desc}</div>
                        {more}
                    </div>
                    <div className={picClass}>{pics}</div>
                </div>
            }
            else {
                contentDetail = <DivFindNone />;
            }
        }
        else if (data.navType == 'trend'|| !(data.navType)) {
            briefClass = 'product-content-brief';
            trendsClass = 'product-content-trends product-selected-primary ';
            contentDetail = <Trends data={data}/>
        }
        return (
            <div className={className} onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                <div className={arrowClass}></div>
                <div className={arrowClass2}></div>
                <div className="product-content m-t-5">
                    <ul>
                        <li onClick={this.trend} className={trendsClass}><a>趋势分析图</a></li>
                        <li onClick={this.brief} className={briefClass}><a>简介</a></li>
                    </ul>
                    {contentDetail}
                </div>
            </div>
        )
    },
    extend(){
        this.setState({showAll: (!this.state.showAll)});
    },
    onMouseEnter(){
        this.props.onMouseEnter();
    },

    onMouseLeave(){
        this.props.onMouseLeave();
    },

    brief(){
        ProductActions.changeNav('brief', this.props.data);

    },
    trend(){
        ProductActions.changeNav('trend', this.props.data);
    }
});


//if(data.pics.length == 0){
//    className += "product-detail  product-detail-"+id%3;
//    arrowClass += "product-arrow-"+id%3;
//    arrowClass2 += "product-arrow2-"+id%3;
//
//    content =   <div className="product-content">
//                    <div>简介：{desc}</div>
//                </div>
//
//}else


module.exports = ProductDetail;