var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var InitActions = require('../../../action/InitActions');
var InitStore = require('../../../store/InitStore');
var Functions = require('../../../../../react-kit/util/Functions');
var DemoDayNav = require('../DemoDayNav.react');
var Overview = require('../../company/Overview.react');
var ScoreCtrl = require('./ScoreCtrl.react');


const CompanyScore = React.createClass({

    mixins: [Reflux.connect(InitStore, 'data')],

    componentWillMount() {
        InitActions.initDemoDayScore(this.props.id, this.props.code, this.props.type);
    },

    componentWillReceiveProps(nextProps) {
        InitActions.initDemoDayScore(nextProps.id, nextProps.code, nextProps.type);
    },

    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var code = data.code;
        var type = data.scoreType;
        var id = data.demodayId;

        return(
            <div className="main-body">
                <DemoDayNav scoreType={type}
                            code={code}
                            selected="company"
                            id={id}/>

                <div className="column three-fourths left-block">
                    <Overview code={code} from={type} id={id} />
                </div>

                <div className="column one-fourth user-part">
                    <ScoreCtrl id={id} code={code} type={type} />
                </div>

            </div>
        )
    },

    scroll(){
        if(Functions.browserVersion() != 'mobile'){
            var scrollTop = $(window).scrollTop();
            var sectionOffSet = $('.first-section').offset();
            if(sectionOffSet != undefined &&  sectionOffSet != null){
                if(scrollTop > sectionOffSet.top){
                    $('.user-operate').css('top', '30px');
                }else{
                    $('.user-operate').css('top', '130px');
                }
            }
        }
    }

});





module.exports = CompanyScore;

