$(document).ready(function(){

    var init = function(){

        do_form_layout();
        init_global_search();
        init_autocomplete();

    }

    var init_global_search = function(){
        global_search = {}
        if($("#search-as-url").val() != ""){

            global_search.id = $("#search-as-uri").val();
            $("#uri-body").text(global_search.id);

        }
        if($("#search-as-query").val() != ""){

            global_search.as_query = $("#search-as-label").val();
            $("#labels-body").text(global_search.as_query);
        }

    }

    var init_autocomplete = function(){

        var options = {

            url: function(frag) {
            return "http://entity-acceptance.europeana.eu//entity/suggest?wskey=apidemo&rows=10&text=" + frag;
            },
            list: { match: { enabled: true },
                    maxNumberOfElements: 10,
                    onChooseEvent: function() {
                        global_search = $("#id_picked_entity").getSelectedItemData()
                        querify_global_search();
                        var value = trim_autocomplete_msg(concatenate_autocomplete_msg(global_search));
                        $("#id_picked_entity").val(value);
                        echo_info();
                    },

            },
            listLocation: "contains",
            requestDelay: 500,
            getValue: concatenate_autocomplete_msg

        }

        $("#id_picked_entity").easyAutocomplete(options);

    }

    var echo_info = function(){

        $("#uri-body").text(global_search.id);
        $("#labels-body").text(global_search.as_query);
        $("#search-as-uri").val(global_search.id);
        $("#search-as-label").val(global_search.as_query);
    }


    var querify_global_search = function(){

        global_search.id = "\"" + global_search.id + "\"";
        var all_names = [];
        for (var slot in global_search.hiddenLabel){

          all_names.push("\"" + global_search.hiddenLabel[slot] + "\"");

        }

        global_search.as_query = "(" + all_names.join(" OR ") + ")";

    }

    var repopulate_query = function(){

        if(typeof global_search !== "undefined"){ 
        
            var new_value = $.trim($(this).parents(".mode-wrapper").find("input:checked").val()) == "URL" ? global_search.id : global_search.as_query;
            $(this).parents(".mode-wrapper").find("input[type=text]").val(new_value);
        }

    }

    var concatenate_autocomplete_msg = function(element){

        var label = element.prefLabel;
        var uri = element.id;
        var cat = element.type;
        msg = label + " (" + cat + ")"
        return msg;                  

    }

    var trim_autocomplete_msg = function(current_msg){

        var msg = current_msg.replace(/<br>/g, ", ");
        return msg;

    }

    var do_form_layout = function(){
      $("p:empty").each(function(){

            $(this).remove();

        });
      $("form p:has(#id_solr_query)").after($("#meta-buttons"));
      $("form p").css({ "width" : "350px"});

    }

    var retrieve_items = function(){
        var tidied_query = tidy_query();

        $("#id_solr_query").val(tidied_query);
        reset_pagination(tidied_query);
        return true;

    }

    var tidy_query = function(){

        var raw_query = $.trim($("#id_solr_query").val());
        all_terms = raw_query.split();
        var new_terms = [];
        for(var i = 0; i < all_terms.length; i++){

            var term = $.trim(all_terms[i]);
            if(term.startsWith("http:")){
                term = "\"" + term + "\"";

            }
            new_terms.push(term);

        }
        var tidied_query = new_terms.join(" ");
        return tidied_query;

    }

    var reset_pagination = function(query){

        if(query != $.trim($("#query-body").text())){

            $("#page_no").val("1");

        }

    }


    var reset_form = function(){

        $("#do-reset").val("T");
        $("#launch-query").click();

    }

    var jump_to_page = function(){

        var new_page = $.trim($(this).text());
        change_page(new_page);

    }

    var advance_page = function(){

        var new_page = parseInt($.trim($("#page_no").val())) + 1;
        change_page(new_page);
    
    }

    var retreat_page = function(){

        var new_page = parseInt($.trim($("#page_no").val())) - 1;
        change_page(new_page);

    }

    var change_page = function(new_page_no){

        $("#page_no").val(new_page_no);
        $("#launch-query").click();

    }

    $("#launch-query").click(retrieve_items);
    $("#clear-query").click(reset_form);
    $(".pagination-item").click(jump_to_page);
    $("#arrow-back").click(retreat_page);
    $("#arrow-forward").click(advance_page);
    init();

})