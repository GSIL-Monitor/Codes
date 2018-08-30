var React = require('react');

const SelectedList = React.createClass({

    render(){
        id = this.props.id;
        var list = this.props.selectedIds;
        var flag;
        if (list.length > 0) {
            for (var i in list) {
                if (id == list[i].id) {
                    if (list[i].selected)
                        flag = true;
                }
            }
        }
        var className = 'product-select ';
        if (flag) className += 'product-selected';
        return (
            <div className="new-org-item">
                <div className="org-item-info">
                    <div className={className} onClick={this.click}></div>
                </div>

            </div>
        )
    },

    click(){
        this.props.select(this.props.id);
    }
});

module.exports = SelectedList;
