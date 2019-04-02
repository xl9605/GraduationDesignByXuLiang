/**
* 换肤
**/


$(function(){
	$('.color a').click(function(){
		$("#"+this.id).addClass("color-on").siblings().removeClass("color-on");
		$('#skinCss').attr("href","extras/css/"+(this.id)+".css");
	});
})