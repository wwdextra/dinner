// dinner.js
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
var domain = 'http://localhost:8000';
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

var test = new Vue({
  el: '#test0',
  data: {
    selected: false
  },
  methods: {
        onClick: function (e) {
            // console.log(e.target.tagName) // "A"
            // console.log(e.targetVM === this) // true
            // e是原生的DOM事件对象
            // this 指向该ViewModel实例
            this.selected = !this.selected;
            var url = domain + '/dinner/book';
            var pdata = {
              selected: Number(this.selected),
              cal_id: 333
            };
            $.post(url, pdata, function(response) {
            }, 'json');
        }
    }
});

