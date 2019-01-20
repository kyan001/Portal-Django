$(function(){
    $('.progress-card .panel').mouseover(function(){
        $(this).find('.progress').addClass('active progress-striped');
    });
    $('.progress-card .panel').mouseout(function(){
        $(this).find('.progress').removeClass('active progress-striped');
    });
    $('.collapse').on('hide.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down')
    })
    $('.collapse').on('show.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up')
    })
});
function toggleFollowProgresses(btn){
    $(btn).toggleClass("active").toggleClass("btn-default").toggleClass("btn-warning")
    $(btn).find(".glyphicon").toggleClass("glyphicon-unchecked").toggleClass("glyphicon-check")
    $("#follow-row").toggleClass("hidden")
    $("#inprogress-and-follow-row").toggleClass("hidden")
}
function toggleSearchRow(btn){
    if (typeof prev_scrollTop == "undefined"){
        var target_scrollTop = 0
        prev_scrollTop = document.documentElement.scrollTop
    } else {
        var target_scrollTop = document.documentElement.scrollTop || prev_scrollTop
        delete prev_scrollTop
    }
    $("html, body").animate({ scrollTop: target_scrollTop }, 200)
    $("#search-row").fadeToggle()
    $(btn).toggleClass("active")
}
