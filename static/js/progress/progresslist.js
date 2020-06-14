$(function () {
    $('.progress-card .panel').mouseover(function(){
        $(this).find('.progress').addClass('active progress-striped');
    });
    $('.progress-card .panel').mouseout(function(){
        $(this).find('.progress').removeClass('active progress-striped');
    });
    $('.collapse').on('hide.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right')
    })
    $('.collapse').on('show.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down')
    })
    // insert search input box
    let searchInputHtml = `
        <div id="progress-search-div" hidden>
            <div class="row">
                <div class="col-xs-12">
                    <form id="search-form" action="/progress/search" method="get">
                        <div class="input-group input-group-sm">
                            <input id="search-input" type="text" class="form-control" name="keyword" placeholder="…" autocomplete="off" oninput="instantProgressSearch(this.value)">
                            <input id="search-submit" type="submit" hidden>
                            <div class="input-group-btn">
                                <a class="btn btn-default" role="button" onclick="$('#search-submit').click()">
                                    <span class="glyphicon glyphicon-search"></span>
                                </a>
                            </div>
                        </div>
                    </form>
                </div><!--.col-->
            </div><!--.row-->
            <br>
        </div><!--#progress-search-div-->
    `
    $('.container').prepend(searchInputHtml)
})

function toggleFollowProgresses (btn) {
    $(btn).toggleClass("active").children().toggleClass("text-warning")
    $(btn).find(".glyphicon").toggleClass("glyphicon-unchecked").toggleClass("glyphicon-check")
    $("#follow-row").toggleClass("hidden")
    $("#inprogress-and-follow-row").toggleClass("hidden")
}

let prevScrollTop = 0
function scrollTopToggle () {
    $("html, body").animate({ scrollTop: prevScrollTop }, 200)
    if (prevScrollTop === 0) {
        prevScrollTop = document.documentElement.scrollTop
    } else {
        prevScrollTop = 0
    }
}

function toggleSearchRow (btn) {
    scrollTopToggle()
    $("#progress-search-div").slideToggle('fast')
    $(btn).toggleClass("active")
    if ($(btn).hasClass("active")) {
        $("#search-input").focus()
    }
}

function isTextHit(text, keyword) {
    return (text.trim().toLowerCase().indexOf(keyword.trim().toLowerCase()) > -1)
}

function instantProgressSearch (keyword) {
    keyword = keyword.trim()
    if (keyword) {
        $('.progress-card').each(function () {
            if (isTextHit($(this).find('.prg-name').text(), keyword) || isTextHit($(this).find('.comment').text(), keyword)) {
                $(this).show()
            } else {
                $(this).hide()
            }
        })
    } else {
        $('.progress-card').show()
    }
}
