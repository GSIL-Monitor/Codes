var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ProductStore = require('../../../store/company/ProductStore');
var ProductActions = require('../../../action/company/ProductActions');

var Functions = require('../../../../../react-kit/util/Functions');
var ProductDetail = require('./ProductDetail.react');
var View = require('../../../../../react-kit/util/View');

const ProductList = React.createClass({
    render(){
        return (
            <div className="product-list">
                {this.props.data.map(function (result, index) {
                    return <ProductItem key={index} id={index+1} data={result}/>;
                })}
            </div>
        )
    }
});


const ProductItem = React.createClass({

    render (){
        var item = this.props.data;
        var className = Functions.getArtifactLogo(item.artifact.type);

        var productInfo;
        var detail;
        var pic;
        var selectClass = "product ";

        if (item.artifact.type == 4010) {
            productInfo = <a className="a-button m-t-10"
                             href={item.artifact.link}
                             title={item.artifact.link}
                             target="_blank">
                {item.artifact.link}
            </a>
        } else {
            productInfo = item.artifact.name;
        }

        if (item.pics.length > 0) {
            pic = <a className="right text-soft m-t--10">产品图片</a>
        }

        // check artifact type
        var artifactType = item.artifact.type;
        var isShow = (artifactType == 4010 || artifactType == 4040 || artifactType == 4050);
        if (this.state != null) {
            if (isShow&&(this.state.selected || this.state.detailSelected)) {
                selectClass += "product-hover";
                detail = <ProductDetail data={item} id={this.props.id}
                                        onMouseEnter={this.detailMouseEnter}
                                        onMouseLeave={this.detailMouseLeave}/>
            }
        }

        var link;
        if (item.artifact.type != 4020)
            link = item.artifact.link;

        return (
            <div className={selectClass} onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                <div>
                    <a href={link} title={link} target="_blank">
                        <i className={'fa fa-2x product-logo '+className}></i>
                    </a>

                    <div className="product-info">
                        {productInfo}
                    </div>

                    {pic}

                </div>

                {detail}

            </div>
        )
    },

    onMouseEnter(e){
        this.setState({selected: true});
        if(!this.props.data.selected){
            ProductActions.getTrends(this.props.data.artifact.id,this.props.data.artifact.type,30);
        }
        //View.fix_product(e);
    },

    onMouseLeave(e){
        this.setState({selected: false});
        //View.fix();
    },

    detailMouseEnter(){
        this.setState({detailSelected: true})
    },

    detailMouseLeave(){
        this.setState({detailSelected: false});
        //View.fix();
    }

});


module.exports = ProductList;