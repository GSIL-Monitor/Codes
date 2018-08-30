var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var CollectionActions = require('../../action/collection/CollectionActions');
var CollectionUtil=require('../../util/CollectionUtil');

const CollectionList = React.createClass({

    render(){
        var data = this.props.data;
        var selected = data.selected;
        var customCols = data.customCols;
        var custom;
        if(customCols.length>0){
            custom= customCols.map(function (result, index) {
                return <CustomCollectionItem key={index} data={result}/>;
            }.bind(this))
        }
        var hotCols=data.hotCols;
        var hot;
        if(hotCols.length>0){
            hot= hotCols.map(function (result, index) {
                return <CollectionItem key={index} data={result}/>;
            }.bind(this))
        }

        return(
            <div className="collection-list">
                <h3>我的集合</h3>

                <div className="collection-self">
                    {custom}
                    <AddNewCollection />
                </div>

                <h3 className="m-t-10">热门集合</h3>

                <div className="collection-system">
                    <div className="collection-list-item">
                        <div className="collection-select"><i className="fa fa-plus"></i></div>
                        <div className="collection-name" onClick={this.faClick}>FA每日精选</div>
                    </div>

                    <div className="collection-list-item">
                        <div className="collection-select"><i className="fa fa-plus"></i></div>
                        <div className="collection-name">每日新产品</div>
                    </div>
                    {hot}
                </div>
            </div>
        )
    },

    faClick(){
        var sysCols=this.props.data.sysCols;
        if(sysCols.length>0){
            window.location.href = '/#/collection/'+CollectionUtil.getSysColsId(sysCols);
        }else{
            return;
        }

    }

});



const CollectionItem = React.createClass({
    render(){
        var data=this.props.data;
        var plus;
        var classSelect;
        if(data.active=='Y'){
            plus= <i className="fa fa-check"></i>;
            classSelect="collection-selected";
        }
        else{
            plus= <i className="fa fa-plus" onClick={this.follow}></i>
            classSelect="collection-select";
        }

        return (
            <div className="collection-list-item">
                <div className={classSelect}>{plus}</div>
                <div className="collection-name" onClick={this.click}>{data.name}</div>
            </div>
        )
    },
    click(){
        window.location.href = '/#/collection/'+this.props.data.id;
    },
    //关注此collection
    follow(){
        CollectionActions.follow(this.props.data.id);
    }
});


const AddNewCollection = React.createClass({

    render(){
        return(
            <div className="collection-list-item">
                <div className="add-new-collection" onClick={this.click}>
                    <i className="fa fa-plus"></i>
                    新增集合
                </div>
            </div>
        )
    },

    click(){
        window.location.href = './#/new/collection';
    }

});

const CustomCollectionItem = React.createClass({
    render(){
        return (
            <div className="collection-list-item">
                <div className="collection-selected"><i className="fa fa-check"></i></div>
                <div className="collection-name" onClick={this.click}>{this.props.data.name}</div>
            </div>
        )
    },
    click(){
        window.location.href = '/#/collection/'+this.props.data.id;
    }
});





module.exports = CollectionList;

