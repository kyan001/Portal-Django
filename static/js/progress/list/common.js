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
