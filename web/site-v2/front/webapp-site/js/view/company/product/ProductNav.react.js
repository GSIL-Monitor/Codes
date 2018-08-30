var React = require('react');

var ProductActions = require('../../../action/company/ProductActions');
var Functions = require('../../../../../react-kit/util/Functions');

const ProductNav = React.createClass({
    render(){
        var data = this.props.data;
        var types = data.types;
        var selected = data.selectedType;
        var count = data.count;

        return (
            <div className="product-nav">
                <ul className="tab-ul">
                    {types.map(function(type, index){
                        return <ProductNavItem key={index}
                                               data={type}
                                               selected={selected}
                                               count={count}/>
                    }.bind(this))}

                </ul>
            </div>
        )
    }

});

const ProductNavItem = React.createClass({
    render(){
        var typeName = Functions.getArtifactTypeName(this.props.data);
        var count;
        var className = "tab-li ";
        if (this.props.data == this.props.selected) {
            count = <div className="product-count">{this.props.count}</div>;
            className += "active";
        }

        return <li className={className}>
                    <a onClick={this.changeType}>
                        {typeName}
                        {count}
                    </a>
                </li>
    },

    changeType(){
        ProductActions.changeType(this.props.data);
    }

});

module.exports = ProductNav;