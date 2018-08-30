var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyInfoActions = require('../action/CompanyInfoActions');
var CompanyInfoStore = require('../store/CompanyInfoStore');
var Functions = require('../util/Functions');

var Fundings = require('./Fundings.react');
var Footprints = require('./Footprints.react');

var SpinnerCircle = require('../basic/SpinnerCircle.react');

const CompanyInfo = React.createClass({

    mixins: [Reflux.connect(CompanyInfoStore, 'data')],

    componentWillMount() {
        CompanyInfoActions.init(this.props.code);
    },

    render(){
        if(Functions.isEmptyObject(this.state)){
            return null;
        }

        var data = this.state.data;
        var code = this.props.code;
        var className = this.props.className;
        var link = "/#/company/"+code+"/overview";
        if(Functions.browserVersion() == 'mobile'){
            link = '.'+link;
            return(
                <a className={className}
                   href={link} >
                    {this.props.name}
                </a>
            );
        }

        var info;

        if(this.state != null){
            if(this.state.show){
                //className += ' item-padding';
                info = <Info data={data} onMouseEnter={this.onMouseDetailEnter} onMouseLeave = {this.onMouseLeave}/>
            }
        }
        return(
            <div className={className}>
                <a href={link}
                   target="_blank"
                   onMouseEnter={this.onMouseEnter}
                   onMouseLeave = {this.onMouseLeave} >
                    {this.props.name}
                </a>
                {info}
            </div>
        )
    },

    onMouseEnter(){
        CompanyInfoActions.getCompany(this.props.code);
        this.setState({show: true})
    },

    onMouseDetailEnter(){
        this.setState({show: true})
    },

    onMouseLeave(){
        this.setState({show: false})
    }
});


const Info = React.createClass({
    render(){
        var data = this.props.data;
        if(Functions.isNull(data)) return null;
        var company = data.company;
        if(company == null){
            return(
                <div className="company-popover" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                    <div className="company-popover-body">
                        <SpinnerCircle />
                    </div>
                </div>
            )
        }
        //console.log(data)

        var logo;
        if(company.logo != null){
            logo = "/file/"+company.logo+"/product.png";
        }else{
            logo = "/resources/image/company_logo.png";
        }
        var establishDate = company.establishDate;
        if(establishDate != null){
            establishDate = establishDate.substring(0,7)
        }

        var location = company.location;
        if(location != null){
            location = "@"+location;
        }

        var desc = company.description;
        if(!Functions.isNull(desc)){
            if(desc.length > 300){
                desc = desc.substring(0, 300)+'...';
            }
            desc = <pre>{desc}</pre>
        }

        return(
            <div className="company-popover" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                <div className="company-popover-body">
                    <div className="company-header">
                        <img className="company-logo" src={logo} />
                        <div className="company-basic company-popover-basic">
                            <p className="company-popover-name">{company.name}</p>
                            <p className="company-brief"> {company.brief} </p>
                            <p>{establishDate} {location}</p>
                        </div>
                    </div>

                    {desc}

                    <div>
                        <Fundings  data={data.fundings}/>
                        <Footprints  data={data.footprints}/>

                    </div>
                </div>
            </div>
        )
    },

    onMouseEnter(){
        this.props.onMouseEnter();
    },

    onMouseLeave(){
        this.props.onMouseLeave();
    }
});


module.exports = CompanyInfo;