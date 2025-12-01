(function($){
    if(cookieExists('nv-news-unibrow')){
        $('#announcement-banner').remove();
    }
    else{
        $('#announcement-banner').css('display', 'block');
    }
    adjust_page_margin();
    $('#announcement-banner .btn-toggle-additional-text').click(function(){
        $('#announcement-banner').toggleClass('show-additional-text')
        adjust_page_margin();
    })

    $('#btn-close-announcement-banner').click(function(){
        $('#announcement-banner').fadeOut('slow', function() {
            $(this).remove();
            adjust_page_margin();
        });
        set_anouncement_banner_cookie();
    })

    function adjust_page_margin(){
        var height_global_nav = $('.navigation .global-nav').height();
        $('#page-content').css('margin-top',  height_global_nav+"px")
    }

    
    function set_anouncement_banner_cookie() {
        const cookieName = 'nv-news-unibrow';
        const cookieValue = 'nv-news-unibrow';
        const hoursToExpire = 24;

        var date = new Date();
        date.setTime(date.getTime() + (hoursToExpire * 60 * 60 * 1000));
        var expires = "expires=" + date.toUTCString();
        document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
    }
    function cookieExists(cookieName) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Check if this cookie is the one we're looking for
            if (cookie.indexOf(cookieName + '=') === 0) {
                return true;
            }
        }
        return false;
    }
    
})(jQuery)