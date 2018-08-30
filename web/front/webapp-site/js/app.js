var ReactDOM = require('react-dom');
var React = require('react');
var RouterConf = require('./router/RouterConf.react');


/*********** router *******/

ReactDOM.render(
    <RouterConf />,
    document.getElementById('router')
);



/*********   basic  **********/
var Header = require('../../react-kit/basic/Header.react');
var Sidebar = require('../../react-kit/basic/Sidebar.react');
var Mask = require('../../react-kit/modal/Mask.react');

var view = require('../../react-kit/util/view');

ReactDOM.render(
    <Header />,
    document.getElementById('header')
);

ReactDOM.render(
    <Sidebar />,
    document.getElementById('sidebar')
);


ReactDOM.render(
    <Mask />,
    document.getElementById('mask')
);













