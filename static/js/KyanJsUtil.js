$.extend({
    getBookImg: function(name, size, callback) {
        size = size?size:'m';  // s,m,l
        if(!name){
            return ''
        }
        var book_search_api = 'https://api.douban.com/v2/book/search';
        $.ajax({
            type: 'GET',
            url: book_search_api,
            data: {
                'count':'1',
                'q':name
            },
            async: false,
            dataType: 'jsonp',
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Ajax Error, XMLHttpRequest:");
                console.log("status: "+XMLHttpRequest.status);
                console.log("readyState: "+XMLHttpRequest.readyState);
                console.log("textStatus: "+textStatus);
            },
            success: function(data){
                var imgurl = "";
                if( checkHas(name, data.books[0]) ){
                    switch(size){
                        case 's':
                            imgurl = data.books[0].images.small;
                            break;
                        case 'm':
                            imgurl = data.books[0].images.medium;
                            break;
                        case 'l':
                            imgurl = data.books[0].images.large;
                            break;
                        default:
                            imgurl = data.books[0].images.medium;
                    }
                }
                callback(imgurl);
            }
        });
    },
    getBookInfo: function(name, callback){
        var book_search_api = 'https://api.douban.com/v2/book/search';
        if(name != ''){
            $.get(book_search_api, {'count':'1','q':name}, function(data){
                var info = {}
                info.title = '';
                info.rating = '';
                info.pages = '';
                info.url = '';
                info.tags = new Array()
                if( checkHas(name, data.books[0]) ){
                    info.title = data.books[0].title
                    if(data.books[0].tags[0]){
                        info.tags.push(data.books[0].tags[0].name)
                    }
                    if(data.books[0].tags[1]){
                        info.tags.push(data.books[0].tags[1].name)
                    }
                    if(data.books[0].tags[2]){
                        info.tags.push(data.books[0].tags[2].name)
                    }
                    info.rating = data.books[0].rating.average
                    info.pages = data.books[0].pages
                    info.url = data.books[0].alt
                }
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
                info.title = '';
                info.rating = '';
                info.url = '';
                info.tags = new Array()
                if( checkHas(name, data.subjects[0]) ){
                    info.title = data.subjects[0].title
                    info.tags = data.subjects[0].genres
                    info.rating = data.subjects[0].rating.average
                    info.url = data.subjects[0].alt
                }
                callback(info);
            }, 'jsonp');
        }
    },
});

function checkHas(keyword, bookOrMovie){
    if(!bookOrMovie){
        return false;
    }
    if(keyword){
        keyword = keyword.toLowerCase()
    } else {
        return false;
    }
    if(bookOrMovie.title){
        if(bookOrMovie.title.toLowerCase().indexOf(keyword) >= 0){
            return true
        }
    }
    if(bookOrMovie.original_title){
        if(bookOrMovie.original_title.toLowerCase().indexOf(keyword) >= 0){
            return true
        }
    }
    return false
}
