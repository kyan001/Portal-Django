$(function(){
    $('.progress-card .panel').mouseover(function(){
        $(this).find('.progress').addClass('active progress-striped');
    });
    $('.progress-card .panel').mouseout(function(){
        $(this).find('.progress').removeClass('active progress-striped');
    });
    $('.progress-card .panel .weblink').click(function(){
        var href = $(this).attr('href')
        //window.location.href=href;
        window.open(href)
        return false
    });
    $('.collapse').on('hide.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down')
    })
    $('.collapse').on('show.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up')
    })
    // $('.progress-card').each(function(){
    //     var ele = $(this)
    //     $.getImageColor("", ele.attr('progressname'), function(result){
    //         if( result.color ){
    //             ele.find('.panel').css('border-left', '5px solid' + result.color);
    //         }
    //     });
    // });
});
