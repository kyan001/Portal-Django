$(function(){
    $(".innerlink").click(function(){
        // 在 <a> 中的 <span>，点击和 <a> 效果一致
        var href = $(this).attr("href")
        var target = $(this).attr("target")
        if(target == "_blank"){
            window.open(href)
        } else {
            window.location.href=href;
        }
        return false
    })
})

var OpusInfoGetter = {
    /**
     * get book info from douban by isbn number
     * @param  {String}     isbn        [isbn number]
     * @param  {Function}   callback    [call this function after got the data]
     * @param  {Function}   callback404 [call this function if has a error ]
     */
    "getIsbnInfo": function(isbn, callback, callback404){
        var isbn_search_api = "https://api.douban.com/v2/book/isbn/" + isbn
        if(isbn !== ""){
            $.ajax({
                type: "GET",
                url: isbn_search_api,
                data: {},
                dataType: "jsonp",
                error: function(){
                    callback404()
                },
                success: function(result){
                    callback(result)
                }
            })
        }
    },
    /**
     * get book info from douban by the name
     * @param  {String}     name     [book's name, full or partial]
     * @param  {Function}   callback [call this function after got the data]
     */
    'getBookInfo': function(name, callback){
        var book_search_api = "/opus/searchopusinfo"
        var book_search_api_douban = "https://api.douban.com/v2/book/search"
        if(name !== ""){
            $.get(book_search_api, {'count':'1', 'q':name, 'type':'book'}, function(data){
                var info = {}
                info.exist = data.books[0] ? true : false
                info.type = 'book'
                info.api = book_search_api_douban + '?count=1&q=' + name
                if(info.exist){
                    info.title = data.books[0].title;
                    info.origin_title = data.books[0].origin_title  // book only, optional
                    info.numrater = data.books[0].rating.numRaters  // book only
                    info.rating = data.books[0].rating.average;
                    info.pages = data.books[0].pages
                    info.url = data.books[0].alt
                    info.tags = new Array()
                    info.summary = data.books[0].summary
                    if(data.books[0].tags[0]){
                        info.tags.push(data.books[0].tags[0].name)
                    }
                    if(data.books[0].tags[1]){
                        info.tags.push(data.books[0].tags[1].name)
                    }
                    if(data.books[0].tags[2]){
                        info.tags.push(data.books[0].tags[2].name)
                    }
                    info.images = {}
                    if(data.books[0].images){
                        info.images.small = data.books[0].images.small
                        info.images.medium = data.books[0].images.medium
                        info.images.large = data.books[0].images.large
                    }
                    info.image = data.books[0].image
                }
                info.match = OpusInfoGetter.checkHas(name, data.books[0])
                callback(info)
            }, 'json');
        }
    },
    /**
     * get movie info from douban by the name
     * @param  {String}     name     [movie's name, full or partial]
     * @param  {Function}   callback [call this function after got the data]
     */
    'getMovieInfo': function(name, callback){
        var movie_search_api = '/opus/searchopusinfo'
        var movie_search_api_douban = 'https://api.douban.com/v2/movie/search'
        var movie_info_api = 'https://api.douban.com/v2/movie/subject/'
        if(name != ""){
            $.get(movie_search_api, {"count": "1","q": name, "type": "movie"}, function(data){
                var info = {}
                if( data.subjects[0] ){
                    info.title = data.subjects[0].title;
                    info.rating = data.subjects[0].rating.average;
                    info.original_title = data.subjects[0].original_title  // movie only, optional
                    info.stars = data.subjects[0].rating.stars  // movie only
                    info.subtype = data.subjects[0].subtype  // movie only
                    info.url = data.subjects[0].alt;
                    info.tags = new Array(data.subjects[0].genres);
                    info.summary = data.subjects[0].summary
                    if(data.subjects[0].images){
                        info.images = {};
                        info.images.small = data.subjects[0].images.small
                        info.images.medium = data.subjects[0].images.medium
                        info.images.large = data.subjects[0].images.large
                        info.image = data.subjects[0].images.medium
                    }
                }
                info.api = movie_search_api_douban + "?count=1&q=" + name
                info.type = "movie"
                info.match = OpusInfoGetter.checkHas(name, data.subjects[0])
                info.exist = data.subjects[0] ? true : false
                callback(info)
            }, "json");
        }
    },
    /**
     * get image's primary color
     * @param  {String}     url      [image url, if url=="", only read cache]
     * @param  {String}     name     [the opus's title which contains the image]
     * @param  {Function}   callback [call this function after got the data]
     */
    "getImageColor": function(url, opusid, callback){
        var request_data = {}
        if(url==""){
            request_data = {
                "opusid": opusid,
            };
        } else {
            request_data = {
                "url": url,
                "opusid": opusid,
            };
        }
        $.ajax({
            type: "GET",
            url: "/progress/imagecolor",
            data: request_data,
            async: true,
            dataType: "json",
            success: function(result) {
                callback(result)
            }
        });
    },
    /**
     * check if the keyword is appeared in the original name or title of a  book/movie
     * @param  {String}     keyword     [words, mostly is short]
     * @param  {opusinfo}   bookOrMovie [the opus's info, should include a title or original_title]
     * @return {Boolean}                   [if the keyword is in the opus names]
     */
    "checkHas": function(keyword, bookOrMovie){
        if(!keyword || !bookOrMovie){
            return false;
        }
        var kw = keyword.toLowerCase().split(" ")
        var isInOriginalTitle = true;
        var isInTitle = true;
        if(bookOrMovie.original_title){  // 有英文名
            for(var i in kw){
                if(bookOrMovie.original_title.toLowerCase().indexOf(kw[i]) < 0){
                    isInOriginalTitle = false  // 只要有一个词不在title内，则判定失败
                    break
                }
            }
        } else {  // 无英文名
            isInOriginalTitle = false
        }
        if(bookOrMovie.title){  // 如果有title
            for(var i in kw){
                if(bookOrMovie.title.toLowerCase().indexOf(kw[i]) < 0){
                    isInTitle = false  // 只要有一个词不在title内，则判定失败
                    break
                }
            }
        } else {  // 没有title
            isInTitle = false
        }
        return isInOriginalTitle || isInTitle
    },
}

function disableAllBtn(){
    // submit() 前应禁用所有按钮。
    $(".btn").attr("disabled", "disabled")
    $(".btn").click(function(){
        return false;
    })
}

function markread(ele){
    chatid = $(ele).attr("chatid")
    if(chatid<0){
        return;
    }
    if(!$(ele).hasClass("unread")){
        return;
    }
    $.ajax({
        type: "GET",
        url: "/chat/markread",
        data: {"chatid": chatid},
        async: true,
        dataType: "json",
        success: function(result) {
            if(result.error){
                alert(result.error)
            } else {
                $("div[chatid="+chatid+"]").removeClass("unread")
            }
            updateUnreadCount()
        }
    });
}

function square_this(ele){
    var width = $(ele).width()
    $(ele).height(width)
}

function isMobile(){
    // 判断是否有 mobile 于 user-agent
    if(navigator.userAgent.toLowerCase().match(/mobile/i) == "mobile"){
        return true
    } else {
        return false
    }
}
