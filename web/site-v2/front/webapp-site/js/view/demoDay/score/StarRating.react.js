var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions =  require('../../../action/demoday/DemoDayActions');
var DemoDayStore =  require('../../../store/demoday/DemoDayStore');
var Functions = require('../../../../../react-kit/util/Functions');

const StarRating = React.createClass({

    render(){

        var rating;

        if(this.state != null){
            rating = this.state.rating;
            if(rating > 0){
                rating = this.state.rating;
            }else{
                rating = this.props.rating;
                if(rating == 0)
                    rating = this.props.rated;
            }
        }else{
            if(rating > 0){
                rating = this.props.rating;
            }else{
                rating = this.props.rated;
            }
        }

        var stars =[];
        for(var i =1 ; i<6; i++){
            var starClass = "fa fa-star-o";
            var star = {};
            if(i <= rating){
                starClass = "fa fa-star";
            }

            star.className = starClass;
            star.score = i;
            star.type = this.props.type;
            star.disable = this.props.disable;

            stars.push(star);
        }


        return(
            <div className="star-rating">
                <label className="star-rating-label">{this.props.name}</label>
                {stars.map(function(result, index){
                    return <Star key={index}
                                 data={result}
                                 onMouseOver={this.onMouseOver}
                                 onMouseOut={this.onMouseOut}
                            />;
                }.bind(this))}
            </div>
        )
    },

    onMouseOver(score){
        this.setState({rating: score})
    },

    onMouseOut(){
        this.setState({rating: 0})
    }

});

const Star =  React.createClass({

    render(){
        return(
            <i className={this.props.data.className}
               rank={this.props.data.score}
               onMouseOver={this.onMouseOver}
               onMouseOut={this.onMouseOut}
               onTouchMove = {this.onMouseOver}
               onTouchEnd = {this.onMouseOut}
               onClick={this.onClick} >
            </i>
        )
    },

    onMouseOver(){
        if(!this.props.data.disable)
            this.props.onMouseOver(this.props.data.score);
    },

    onMouseOut(){
        if(!this.props.data.disable)
            this.props.onMouseOut();
    },

    onClick(){
        if(!this.props.data.disable)
            DemoDayActions.rating(this.props.data.score, this.props.data.type);
    }
});

module.exports = StarRating;

