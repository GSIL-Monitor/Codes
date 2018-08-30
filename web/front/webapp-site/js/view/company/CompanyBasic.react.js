var React = require('react');
var $ = require('jquery');

const CompanyBasic = React.createClass({
    render(){
        var company = this.props.data;

        return(
            <div className="section">
                <span className="section-header">
                    公司信息
                </span>

                <section className="section-body">
                    <div className="section-left">
                        <div className="section-left-name name2">
                            简介
                        </div>
                    </div>
                    <div className="section-right">
                        {company.description}
                    </div>
                </section>


                <section className="section-body">
                    <div className="section-left">
                        <div className="section-left-name name4">
                            基本<br/>信息
                        </div>
                    </div>
                    <div className="section-right">
                        <div className="section-right-part">
                            <div className="section-right-name">公司名称：</div>
                            <div className="section-right-content">{company.fullName}</div>
                        </div>

                        <div className="section-right-part">
                            <div className="section-right-name">行业：</div>
                            <div className="section-right-content">Sass</div>
                        </div>

                        <div className="section-right-part">
                            <div className="section-right-name">标签：</div>
                            <div className="section-right-content">企业服务</div>
                        </div>
                    </div>
                </section>



            </div>

        )
    }

});


const DevelopList = React.createClass({
    render(){
        return(
            <div className="section-right-part">
                <div className="section-right-name">{this.props.date}</div>
                <div className="section-right-content">{this.props.desc}</div>
            </div>
        )
    }
});

module.exports = CompanyBasic;