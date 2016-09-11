$.extend({
    getBookInfo: function(name, callback){
        var book_search_api = 'https://api.douban.com/v2/book/search';
        if(name !== ''){
            $.get(book_search_api, {'count':'1','q':name}, function(data){
                var info = {}
                if(data.books[0]){
                    info.title = data.books[0].title;
                    info.rating = data.books[0].rating.average;
                    info.pages = data.books[0].pages;
                    info.url = data.books[0].alt;
                    info.tags = new Array();
                    if(data.books[0].tags[0]){
                        info.tags.push(data.books[0].tags[0].name)
                    }
                    if(data.books[0].tags[1]){
                        info.tags.push(data.books[0].tags[1].name)
                    }
                    if(data.books[0].tags[2]){
                        info.tags.push(data.books[0].tags[2].name)
                    }
                    info.images = {};
                    if(data.books[0].images){
                        info.images.small = data.books[0].images.small
                        info.images.medium = data.books[0].images.medium
                        info.images.large = data.books[0].images.large
                    }
                    info.image = data.books[0].image
                }
                info.api = book_search_api + '?count=1&q=' + name
                info.type = 'book'
                info.match = checkHas(name, data.books[0])
                info.exist = data.books[0]?true:false
                callback(info)
            }, 'jsonp');
        }
    },
    getMovieInfo: function(name, callback){
        var movie_search_api = 'https://api.douban.com/v2/movie/search';
        var movie_info_api = 'https://api.douban.com/v2/movie/subject/';
        if(name != ''){
            $.get(movie_search_api, {'count':'1','q':name}, function(data){
                var info = {}
                if( data.subjects[0] ){
                    info.title = data.subjects[0].title;
                    info.rating = data.subjects[0].rating.average;
                    info.url = data.subjects[0].alt;
                    info.tags = new Array(data.subjects[0].genres);
                    info.subtype = data.subjects[0].subtype
                    if(data.subjects[0].images){
                        info.images = {};
                        info.images.small = data.subjects[0].images.small
                        info.images.medium = data.subjects[0].images.medium
                        info.images.large = data.subjects[0].images.large
                        info.image = data.subjects[0].images.medium
                    }
                }
                info.api = movie_search_api + '?count=1&q=' + name
                info.type = 'movie'
                info.match = checkHas(name, data.subjects[0])
                info.exist = data.subjects[0]?true:false
                callback(info);
            }, 'jsonp');
        }
    },
    /**
     * get image's primary color
     * @param  {[string]}   url      [image url, if url=="", only read cache]
     * @param  {[string]}   name     [the opus's title which contains the image]
     * @param  {Function}   callback [call this function after got the data]
     */
    getImageColor: function(url, opusid, callback){
        var request_data = {}
        if(url==""){
            request_data = {
                'opusid': opusid,
            };
        } else {
            request_data = {
                'url': url,
                'opusid': opusid,
            };
        }
        $.ajax({
            type: "GET",
            url: "/progress/imagecolor",
            data: request_data,
            async: true,
            dataType: 'json',
            success: function(result) {
                callback(result)
            }
        });
    },
});

function checkHas(keywords, bookOrMovie){
    if(!bookOrMovie){
        return false;
    }
    if(!keywords){
        return false;
    }
    kw = keywords.toLowerCase().split(' ')
    var isInOriginalTitle = true;
    var isInTitle = true;
    if(bookOrMovie.original_title){//有英文名
        for(var i in kw){
            if(bookOrMovie.original_title.toLowerCase().indexOf(kw[i]) < 0){
                isInOriginalTitle = false //只要有一个词不在title内，则判定失败
                break
            }
        }
    } else {//无英文名
        isInOriginalTitle = false;
    }
    if(bookOrMovie.title){ //如果有title
        for(var i in kw){
            if(bookOrMovie.title.toLowerCase().indexOf(kw[i]) < 0){
                isInTitle = false //只要有一个词不在title内，则判定失败
                break
            }
        }
    } else { //没有title
        isInTitle = false
    }
    return isInOriginalTitle || isInTitle
}

function disableAllBtn(){
    // submit() 前应禁用所有按钮。
    $('.btn').attr('disabled','disabled')
    $('.btn').click(function(){
        return false;
    })
}

function markread(ele){
    chatid = $(ele).attr('chatid')
    if(chatid<0){
        return;
    }
    if(!$(ele).hasClass("unread")){
        return;
    }
    $.ajax({
        type: "GET",
        url: "/chat/markread",
        data: {'chatid': chatid},
        async: true,
        dataType: 'json',
        success: function(result) {
            if(result.error){
                alert(result.error)
            } else {
                $("div[chatid="+chatid+"]").removeClass('unread')
            }
            updateUnreadCount()
        }
    });
}
