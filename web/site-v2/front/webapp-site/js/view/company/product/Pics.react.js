var React = require('react');
var ReactDOM = require('react-dom');
var ReactSwipe = require('react-swipe');
var ProductUtil = require('../../../util/ProductUtil');

const Pics = React.createClass({
    getInitialState(){
        return{
            pos:0,
            selected:false
        }
    },
    render(){
        var images = this.props.images;
        var pos = this.state.pos;
        var left;
        var right;
        var classNamePre="product-pic-pre ";
        var classNameNext="product-pic-next ";
        //if(pos==0){
        //    classNamePre+='un-visibility';
        //}
        //else if(pos==(images.length-1)){
        //    classNameNext+='un-visibility';
        //}
        //else{
        //    classNamePre="product-pic-pre ";
        //    classNameNext="product-pic-next ";
        //}

        if(this.state.selected){
            if(pos==0){
                left =  <span className={classNamePre}>
                    <i className="fa fa-angle-left fa-4x text-gray" />
                </span>;
                right=  <a  onClick={this.next} className={classNameNext}>
                    <i className="fa fa-angle-right fa-4x " />
                </a>;
            }
            else if(pos==(images.length-1)){
                left =  <a onClick={this.prev} className={classNamePre}>
                    <i className="fa fa-angle-left fa-4x " />
                </a>;
                right = <span onClick={this.next} className={classNameNext}>
                    <i className="fa fa-angle-right fa-4x text-gray" />
                </span>;
            }else{
                left =  <a onClick={this.prev} className={classNamePre}>
                    <i className="fa fa-angle-left fa-4x " />
                </a>;
                right=  <a  onClick={this.next} className={classNameNext}>
                    <i className="fa fa-angle-right fa-4x " />
                </a>;
            }
        }else{
            left=null;
            right=null;
        }



        return (
            <div className="product-pic-swipe" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                <EncapReactSwipe images={images}  ref="swipe"/>
                {left}
                {right}
            </div>
        );
    },

    prev(){
        this.refs.swipe.prev();
        var pos =this.refs.swipe.getPos();
        this.setState({pos:pos});
    },

    next(){
        this.refs.swipe.next();
        var pos =this.refs.swipe.getPos();
        this.setState({pos:pos});
    },
    onMouseEnter(){
        this.setState({selected:true});
    },
    onMouseLeave(){
        this.setState({selected:false});
    }

});

const EncapReactSwipe = React.createClass({

    shouldComponentUpdate(nextProps){
        return ProductUtil.needUpdate(nextProps,this.props);
    },

    render(){
        var images = this.props.images;
        var id=0;
       return (
           <ReactSwipe continuous={false} ref="swipe" key={images.length}>
               {images.map(function (data) {
                   id++;
                   return <ImageItem key={id} data={data} />
               }.bind(this))}
           </ReactSwipe>
       )
    },
    prev(){
        this.refs.swipe.swipe.prev();
    },

    next(){
        this.refs.swipe.swipe.next();
    },

    getPos(){
        return this.refs.swipe.swipe.getPos();
    }
});

const ImageItem=React.createClass({
    render(){
        return (
            <div className="swipe-wrap-div">
                <img  className="product-pic-image" src={this.props.data}></img>
            </div>
        )
    }

});


module.exports = Pics;