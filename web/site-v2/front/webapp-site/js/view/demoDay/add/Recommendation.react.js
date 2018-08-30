var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../../store/demoday/DemoDayStore');

const Recommendation = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'demoday')],

    render(){
        var className= 'textarea-update-full ';

        return(
            <section className="section-body">
                <div className="section-round">
                    <div className="section-name name4">
                        推荐<br/>理由
                    </div>
                </div>
                <div className="section-content">
                    <textarea  className={className}
                               name="description"
                               value={this.props.data}
                               onChange={this.change}
                               onMouseOver={this.onMouseOver}
                               onMouseOut={this.onMouseOut}
                               placeholder="项目亮点/存在问题"
                        />
                </div>
            </section>
        )
    },

    change(e){
        DemoDayActions.changeRecommendation(e.target.value);
    }
});


module.exports = Recommendation;
