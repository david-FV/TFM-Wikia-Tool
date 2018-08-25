function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
};
    $(function() {
    $('#calculate').bind('click', function() {
        var $form = $("#form_data");
var data = getFormData($form);
console.log(data)
      $.getJSON('/_get_graph', data, function(data) {
        $("#nodos").text(data.num_nodos);
        $("#aristas").text(data.num_aristas);
        var cy = window.cy = cytoscape({
                container: document.getElementById('cy'),

                boxSelectionEnabled: false,
                autounselectify: true,

                layout: {
                  name: data.layout,
                  avoidOverlap: true,
                  nodeDimensionsIncludeLabels: false,
                  fit: true
                },

                style: [
                  {
                    selector: 'node',
                    style: {
                      'height': data.map,
                      'width': data.map,
                      'background-color': '#ad1a66',
                      'label' : 'data(label)',
                      'font-size' : '4'
                    }
                  },

                  {
                    selector: 'edge',
                    style: {
                      'curve-style': 'haystack',
                      'haystack-radius': 0,
                      "width": "mapData(weight, 1, 100, 1, 2)",
                      'opacity': "mapData(weight, 1, 100, 0.2, 1)",
                      'line-color': "blue",
                    }
                  }
                ],

                elements: data.result
            });
      });
      return false;
    });
  });
