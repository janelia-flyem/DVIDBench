(function($) {

    $(document).ready(function() {

      // reset stats.
      $('.reset').on('click', function(){
        $.get('/stats/reset', function(data) {
          // do nothing
        });
      });

      $('.add_workers').on('click', function(e) {
        e.preventDefault();

        $.post('/start',$('form').serialize(), function(data) {
          //do nothing for now.
        });
      });

      $('.stop').on('click', function() {
        $.get('/stop', function() {});
      })

      function updatePage() {
        // ajax call to fetch the data from the server.
        $.getJSON('/stats/update', function(data) {
          // update the DOM with the new data.
          $('.workers').text(data.workers);
          $('.clients').text(data.clients);
          for (var stat in data.stats[1]) {
            $('.'+ stat).text(data.stats[1][stat])
          }
        });
      }

      // start up a timer that loads in the data every three seconds and updates the page.
      var updaterId = setInterval(updatePage, 3000);
    })

})(jQuery);
