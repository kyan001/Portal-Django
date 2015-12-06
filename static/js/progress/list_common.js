$(function(){
    $('.progress-card .panel').mouseover(function(){
        $(this).find('.progress').addClass('active').addClass('progress-striped');
    });
    $('.progress-card .panel').mouseout(function(){
        $(this).find('.progress').removeClass('active').removeClass('progress-striped');
    });
    $('.progress-card .panel').click(function(){
        var progressid = $(this).parent('.progress-card').attr('progressid');
        window.location.href="/progress/detail?id=" + progressid;
    });
    $('.page-header').mouseover(function(){
        $(this).find('h1>span').css('color','red');
    });
    $('.page-header').mouseout(function(){
        $(this).find('h1>span').css('color','silver');
    });
    $('.page-header').click(function(){
        var ele = $(this).find('h1>span');
        var whenOpen = 'glyphicon-chevron-up';
        var whenClose = 'glyphicon-chevron-down';
        if(ele.hasClass(whenOpen)){
            ele.removeClass(whenOpen)
            ele.addClass(whenClose)
        } else {
            ele.removeClass(whenClose)
            ele.addClass(whenOpen)
        }
    });
    $('.progress-card').each(function(){
        var ele = $(this)
        $.getImageColor("", ele.attr('progressname'), function(result){
            if( result.color ){
                ele.find('.panel').css('border-left', '5px solid' + result.color);
            }
        });
    });
});
