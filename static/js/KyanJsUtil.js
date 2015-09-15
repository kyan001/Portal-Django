$.extend({
    getBookImg: function(name, size, callback) {
        size = size?size:'m';  // s,m,l
        if(!name){
            return ''
        }
        var douban_api_search = 'https://api.douban.com/v2/book/search';
        $.ajax({
            type: 'GET',
            url: douban_api_search,
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
                console.log("get book image success");
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
                callback(imgurl);
            }
        });
    },
    getBookPages: function(name, callback){
        var douban_api_search = 'https://api.douban.com/v2/book/search';
        if(name != ''){
            $.get(douban_api_search, {'count':'1','q':name}, function(data){
                callback(data.books[0].pages);
            }, 'jsonp');
        }
    },
    getBookTags: function(name, callback){
        var douban_api_search = 'https://api.douban.com/v2/book/search';
        if(name != ''){
            $.get(douban_api_search, {'count':'1','q':name}, function(data){
                tags = new Array()
                if(data.books[0].tags){
                    tags.push(data.books[0].tags[0].name)
                    tags.push(data.books[0].tags[1].name)
                    tags.push(data.books[0].tags[2].name)
                }
                callback(tags);
            }, 'jsonp');
        }
    },
});
