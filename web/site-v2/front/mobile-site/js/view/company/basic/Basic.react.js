var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyUtil = require('../../../../../webapp-site/js/util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
//var Document = require('./Document.react');

var FundingStatus = require('./FundingStatus.react');
var Fundings = require('../develop/Fundings.react');
var Footprints = require('../develop/Footprints.react');

const CompanyBasic = React.createClass({

    render(){

        var data = this.props.data;
        var company = data.company;
        var tags = data.tags;
        var documents = data.documents;

        //<Document data={documents} />
        return(
            <div className="section first-section">
                <span className="section-header">
                    公司信息
                </span>

                <Description data={company.description} />

                <Basic company={company}
                       parentSector = {data.parentSector}
                       subSector = {data.subSector}
                       tags = {tags} />

                <FundingStatus company={company}/>

                <Fundings data={data} />
                <Footprints data={data} />


            </div>

        )
    }

});

const Description = React.createClass({
    render(){
        var data ;
        if(Functions.isNull(this.props.data)){
            data = <span className="text-soft">未收录</span>
        }else{
            data = this.props.data
        }

        return(
            <section className="section-body">
                <div className="section-round">
                    <div className="section-name name2">
                        简介
                    </div>
                </div>
                <div className="section-content">
                    <pre className="pre-desc">
                    {data}
                    </pre>
                </div>
            </section>
        )
    }
});


const Basic = React.createClass({
    render(){
        var company = this.props.company;
        var fullName = company.fullName;
        if(Functions.isNull(fullName))
            fullName = 'N/A';

        var headCountMin = company.headCountMin;
        var headCountMax = company.headCountMax;

        var headCount = 'N/A';
        if(!Functions.isNull(headCountMin) && !Functions.isNull(headCountMax)){
            headCount = headCountMin + '-' + headCountMax;
        }

        var sector = this.props.parentSector;
        var subSector = this.props.subSector;

        if(!Functions.isEmptyObject(sector)){
            sector = sector.sectorName;
        }else{
            sector = null;
        }
        var arrow = <strong className="sector-arrow"> {'>'} </strong>
        if(!Functions.isEmptyObject(subSector) && subSector != undefined) {
            subSector = <span>
                            {arrow}
                {subSector.sectorName}
                        </span>;
        }else{
            subSector = null;
        }

        if(sector == null && subSector == null){
            sector = 'N/A'
        }

        return(
            <section className="section-body">
                <div className="section-round">
                    <div className="section-name name4">
                        基本<br/>信息
                    </div>
                </div>
                <div className="section-content">
                    <div className="section-sub-item">
                        <div className="section-sub-item-name">公司名称：</div>
                        <div className="section-sub-item-content">{fullName}</div>
                    </div>

                    <div className="section-sub-item">
                        <div className="section-sub-item-name">团队规模：</div>
                        <div className="section-sub-item-content">{headCount}</div>
                    </div>

                    <div className="section-sub-item">
                        <div className="section-sub-item-name">行业：</div>
                        <div className="section-sub-item-content">
                            {sector} {subSector}
                        </div>
                    </div>

                    <Tag data={this.props.tags}/>

                </div>
            </section>

        )
    }

});

const Tag = React.createClass({
    render(){
        var data = this.props.data;
        if(data == null) return null;
        if(data.length == 0) return null;

        if(data.length > 8){
            data = data.splice(8)
        }

        return(
            <div className="section-sub-item">
                <div className="section-sub-item-name">标签：</div>
                <div className="section-sub-item-content">
                    {data.map(function (result, index) {
                        return <TagItem key={index} data={result}/>;
                    })}
                </div>
            </div>
        )
    }

});

const TagItem = React.createClass({

    render(){
        return(
            <span className="label tag" >
               {this.props.data.name}
            </span>
        )
    }


});





module.exports = CompanyBasic;