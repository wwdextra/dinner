// index.js
// ~~~~~~~~~
// Micheal Fan, 2014-05-15

;
// 配置Vue变量标签
Vue.config(
    { delimiters: ["[", "]"] }
);
url = 'http://127.0.0.1:8000/users/';
var pdata = '';
var data = {
    message: ''
};

$.ajax({
    url: url,
    type: 'post',
    dataType: 'json',
    data: pdata,
    success: function(response) {
        data.message = response.detail;
    }
});
//{
//    message: 'Hello Vue.js!'
//};
var demo = new Vue({
    el: '#demo',
    data: data
});

