/**
 * Created by mushoujin on 2016/12/15.
 */
//顶部齿轮悬停出现
// $("#drop").hover(function() {
//     if ($(this).parent().is(".open")) {
//         return
//     }
//     else
//         $(this).dropdown("toggle")
// });


$('li.gl').mouseover(function() {
    $(this).addClass('open');
}).mouseout(function() {
    $(this).removeClass('open');
});

//获取左侧高度
$('.left-nav').height($(window).height() -116);
$(".right-box iframe").height($(window).height() -134);
/*$(".right-box").height($(window).height() -134);*/
var rightheight=$(window).height() -116;
$(".xz-list").height(rightheight -60);
$(window).resize(function () {
    $(".left-nav").height($(window).height() -116);
    $(".right-box iframe").height($(window).height() -134);
    /*$(".right-box").height($(window).height() -134);*/
    var rightheight=$(window).height() -116;
    $(".xz-list").height(rightheight -60);
});

//左侧菜单
$(function () {
    $('#menu').metisMenu();
});
$(function () {
    $('#menu1').metisMenu();
});
$(function(){
    $("#srcoll").panel({iWheelStep:32});
    $("#srcoll1").panel({iWheelStep:32});
});

