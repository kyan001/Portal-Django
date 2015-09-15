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
                var title = '';
                var rating = '';
                var pages = '';
                var tags = new Array()
                if( checkHas(name, data.books[0]) ){
                    title = data.books[0].title
                    if(data.books[0].tags[0]){
                        tags.push(data.books[0].tags[0].name)
                    }
                    if(data.books[0].tags[1]){
                        tags.push(data.books[0].tags[1].name)
                    }
                    if(data.books[0].tags[2]){
                        tags.push(data.books[0].tags[2].name)
                    }
                    rating = data.books[0].rating.average
                    pages = data.books[0].pages
                }
                callback(title, tags, rating, pages)
            }, 'jsonp');
        }
    },
    getMovieInfo: function(name, callback){
        var movie_search_api = 'https://api.douban.com/v2/movie/search';
        if(name != ''){
            $.get(movie_search_api, {'count':'1','q':name}, function(data){
                var title = '';
                var rating = '';
                var tags = new Array()
                if( checkHas(name, data.subjects[0]) ){
                    title = data.subjects[0].title
                    tags = data.subjects[0].genres
                    rating = data.subjects[0].rating.average
                }
                callback(title, tags, rating);
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
