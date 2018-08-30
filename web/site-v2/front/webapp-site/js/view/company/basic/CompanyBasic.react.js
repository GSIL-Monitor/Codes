var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var Sectors = require('./Sectors.react');
var Tags = require('./Tags.react');
var Documents = require('./Documents.react');
var MoreDesc = require('./MoreDesc.react');
var FundingStatus = require('./FundingStatus.react');
var Fundings = require('../develop/Fundings.react.js');
var Footprints = require('../develop/Footprints.react.js');
var UpdateCompany = require('../update/UpdateCompany.react');
var UpdateFundings  = require('../update/UpdateFundings.react');
var Gongshang  = require('../gongshang/Gongshang.react');

const CompanyBasic = React.createClass({

    render(){
        var data = this.props.data;
        if(data.update){
            return(
                <div>
                    <UpdateCompany data={data}/>
                    <UpdateFundings data={data.updateFundings} fundingAll={data.fundingAll} />
                    <Footprints data={data.footprints} footprintAll={data.footprintAll} />
                </div>
            )
        }else{
            var company = data.company;

            return(
                <div className="section first-section">
                    <span className="section-header">
                        公司信息
                    </span>

                    <Description data={company.description} companyDesc={data.companyDesc}/>

                    <BasicInfo data={data} />

                    <FundingStatus company={company}/>

                    <Fundings data={data} />
                    <Footprints data={data} />

                    <Documents data={data.documents} />


                </div>

            )
        }
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

        var companyDesc = this.props.companyDesc;

        var moreDescBtn, moreDesc;
        if(!Functions.isNull(companyDesc)){

            if( !Functions.isNull(companyDesc.productDesc) ||
                !Functions.isNull(companyDesc.modelDesc) ||
                !Functions.isNull(companyDesc.operationDesc) ||
                !Functions.isNull(companyDesc.teamDesc) ||
                !Functions.isNull(companyDesc.marketDesc) ||
                !Functions.isNull(companyDesc.compititorDesc) ||
                !Functions.isNull(companyDesc.advantageDesc) ||
                !Functions.isNull(companyDesc.planDesc)
                ){
                moreDescBtn = <a className="more-desc" onClick={this.moreDesc}>
                                更多介绍
                                <i className="fa fa-angle-double-right fa-lg m-l-5"></i>
                            </a>

                moreDesc = <MoreDesc data={companyDesc}/>
            }
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
                    {moreDescBtn}
                    </pre>
                    {moreDesc}
                </div>
            </section>
        )
    },

    moreDesc(){
        $('.float-more-desc').hide();
        $('#more-desc').show();
        //$('.user-mark').hide();
        //$('.header').css('z-index', '-1');
    }
});


const BasicInfo = React.createClass({

    render(){
        var data = this.props.data;
        var company = data.company;
        var tags = data.tags;

        var fullName = company.fullName;
        if(Functions.isNull(fullName))
            fullName = 'N/A';

        var headCountMin = company.headCountMin;
        var headCountMax = company.headCountMax;

        var headCount = 'N/A';
        if(!Functions.isNull(headCountMin) && !Functions.isNull(headCountMax)){
            headCount = headCountMin + '-' + headCountMax;
        }

        var gsBtn, gsDiv;
        var gongshangList = data.gongshangList;
        if(gongshangList != null){
            if(gongshangList.length > 0){
                gsBtn = <a className="gongshang-btn" onClick={this.gongshang}>工商信息
                            <i className="fa fa-angle-double-right fa-lg m-l-5"></i>
                        </a>;
                gsDiv = <Gongshang data={gongshangList}/>;
            }
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
                        <div className="section-sub-item-content">
                            {fullName}
                            {gsBtn}
                            {gsDiv}
                        </div>
                    </div>

                    <div className="section-sub-item">
                        <div className="section-sub-item-name">团队规模：</div>
                        <div className="section-sub-item-content">{headCount}</div>
                    </div>

                    <Sectors data={data} />

                    <Tags data={tags}/>

                </div>
            </section>

        )
    },

    gongshang(){
        $('.float-more-desc').hide();
        $('#gongshang').show();
    }

});


module.exports = CompanyBasic;