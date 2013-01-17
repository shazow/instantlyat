(function($) { 
    $.fn.poll = function(options){ 
        var $this = $(this); 
        // extend our default options with those provided 
        var opts = $.extend({}, $.fn.poll.defaults, options); 
        $.fn.poll.yoyo = setInterval(update, opts.interval);

        // method used to update element html
        function update(){
            var data = opts.data
            if(typeof(opts.data) == "function")
              data = opts.data.call(this);
            
            $.ajax({
                type: opts.type,
                data: data,
                url: opts.url,
                success: opts.success
            });
        };
    };

    // method used to stop polling
    $.fn.stopPoll = function(){
        clearInterval($.fn.poll.yoyo);
    };

    // default options
    $.fn.poll.defaults = {
        type: "POST",
        url: ".",
        success: '',
        interval: 2000
    };
})(jQuery);