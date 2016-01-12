(function($) {

    $(document).ready(function() {
      console.log('page loaded');

      function updatePage() {
        // ajax call to fetch the data from the server.
        $.getJSON('/stats/update', function(data) {
          console.log(data);
          // update the DOM with the new data.
          $('.workers').text(data.workers);
          $('.clients').text(data.clients);
        });
      }

      // start up a timer that loads in the data every three seconds and updates the page.
      var updaterId = setInterval(updatePage, 3000);
    })

})(jQuery);
