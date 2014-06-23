// index.js
// ~~~~~~~~~
// Micheal Fan, 2014-05-15

;
// 配置Vue变量标签
Vue.config(
  { delimiters: ["[", "]"] }
);

Vue.directive('disable', function (value) {
    this.el.disabled = !!value
});

url = 'http://127.0.0.1:8000/users/';
var pdata = '';
var data = {
  message: ''
};
/*
$.ajax({
  url: url,
  type: 'post',
  dataType: 'json',
  data: pdata,
  success: function(response) {
    data.message = response.detail;
  }
});
*/
//{
//    message: 'Hello Vue.js!'
//};
// var demo = new Vue({
//   el: '#demo',
//   data: data
// });

var test = new Vue({
  el: '#test0',
  data: {
    abled: false
  },
  methods: {
        onClick: function (e) {
            // console.log(e.target.tagName) // "A"
            // console.log(e.targetVM === this) // true
            console.log('foo');
            // e是原生的DOM事件对象
            // this 指向该ViewModel实例
            this.abled = !this.abled
        }
    }
});

