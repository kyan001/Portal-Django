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
    $('.page-header').click(function(){
        var ele = $(this).find('span.glyphicon');
        var whenOpen = 'glyphicon-chevron-up';
        var whenClose = 'glyphicon-chevron-down';
        if(ele.hasClass(whenOpen)){
            ele.removeClass(whenOpen)
            ele.addClass(whenClose)
        } else if(ele.hasClass(whenClose)) {
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
