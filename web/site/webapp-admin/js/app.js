var ReactDOM = require('react-dom');
var React = require('react');
var RouterConf = require('./router/RouterConf.react');


/*********** router *******/

ReactDOM.render(
    <RouterConf />,
    document.getElementById('router')
);



/*********   basic  **********/
var Header = require('./view/basic/Header.react');
var Sidebar = require('./view/basic/Sidebar.react');
var Footer = require('./view/basic/Footer.react');
var Mask = require('./view/modal/Mask.react.js');
var View = require('./util/view');

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













