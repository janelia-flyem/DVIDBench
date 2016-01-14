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
          for (var stat in data.stats[data.stats.length - 1]) {
            $('.'+ stat).text(data.stats[data.stats.length -1][stat])
          }
        });
      }

      // start up a timer that loads in the data every three seconds and updates the page.
      var updaterId = setInterval(updatePage, 3000);
    })

})(jQuery);




(function($) {

  var loadInterval = 3000;
  var totalPoints = 100;
  var timingData = {};
  var plotData = [];
  var ymax = 10;

  var chartOptions = {
    series: { shadowSize: 1 }, // drawing is faster without shadows
    yaxis: { min: 0, max: ymax },
    xaxis: { show: false },
    legend: {
      position: 'nw'
    },
    grid: {
      borderWidth: 1,
      borderColor: '#ccc'
    }
  };

  // convert timing data into something the flot code can understand.
  var setPlotData = function() {
    var setnum = 0;
    for (var dataset in timingData) {
      var yscale = 1;
      var datasetLabel = dataset;
      plotData[setnum] = {
        label: datasetLabel,
        data: []
      };
      var filler = totalPoints - timingData[dataset].length;
      for (var x = 0; x < totalPoints; ++x) {
        if (filler > x) {
          plotData[setnum].data.push([x,0]);
        } else {
          var i = x - filler;
          if (i < 0 || i > timingData[dataset].length) {
            console.log("Bad i:", i, x, filler, timingData[dataset].length);
          }
          var y = timingData[dataset][i] / yscale;

          if (y < 0) {
            y = 0;
          }
          if (y > ymax) {
            y = ymax;
          }

          plotData[setnum].data.push([x, y]);
        }
      }
      ++setnum;
    }
  }

  // fetch the stats and update the data store.

  var getTimingData = function () {
    $.getJSON('/stats/timings', function(response) {
      for (var entry in response) {
        if (!timingData.hasOwnProperty(entry) || Object.prototype.toString.call(timingData[entry]) !== '[object Array]') {
          timingData[entry] = [];
        }
        if (timingData[entry].length >= totalPoints) {
          timingData[entry] = timingData[entry].slice(1);
        }
        timingData[entry].push(response[entry]);
      }
    });

    setPlotData();

    statsTimeout = setTimeout(getTimingData, loadInterval);
  }

  getTimingData();


  // update the graph
  var updateStats = function() {
    $.plot($('.response_time_graph'), plotData, chartOptions).draw();
    updateTimeout = setTimeout(updateStats, loadInterval);
  }
  updateStats();


})(jQuery);
