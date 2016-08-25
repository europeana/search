$(document).ready(function(){

    var init = function(){

        $("p:has(.boost-field)").addClass("boost-field");
        $("p:has(.boost-factor)").addClass("boost-factor");
        $("p:has(.boost-field)").addClass("boost-inner");
        $("p:has(.boost-factor)").addClass("boost-inner");

        var boosts = $(".boost-inner")
        for(var i = 0; i < boosts.length; i+=2){

            boosts.slice(i, i + 2).wrapAll("<div class=\"boost-unit\"></div>");

        }

        $("p:has(input):not(.boost-inner)").addClass("param-pair");
        $("p:has(#id_searchterm)").removeClass("param-pair");
        $("p:has(#id_field_10)").css({"margin-bottom" : "35px"});

    }

    var start_with_new_init_item = function(){

        return retrieve_init_item();

    }

    var retrieve_init_item = function(){

        $("#query_results").children().remove();
        request = {};
        request['searchterms'] = get_search_term();
        $.getJSON('inititem', request, display_init_item);
        return false;

    };

    var warn_no_init_result = function(bad_query){

        $("#init-item-display").css({ "visibility" : "hidden" });
        var warning = $("<div class=\"results-list\" id=\"init-item-warning-wrapper\"><p id=\"no-init-item-warning\">Unfortunately the search term <b>" + bad_query + "</b> returned no hits.</p></div>");
        $("#user_form").after(warning);


    }

    var warn_no_results = function(bad_query){

        $("#query_results").css({ "visibility" : "visible"});
        $("#query_results").children().remove();
        var warning = $("<p id=\"no-hits-warning\">Unfortunately, your search returned no results. Please try another query. <br/> Your query was " + bad_query + "</p>");
        $("#query_results").append(warning);

    }

    var get_search_term = function(){

        return $.trim($("#id_searchterm").val());

    }


    var retrieve_related_items = function(){

        request = get_sim_params();
        $.getJSON('relateditems', request, display_related_items);
        return false;

    }

    var get_sim_params = function(){

        params = {}
        params['europeana_id'] = $.trim($("#europeana-id").val());
        params['mintf'] = $.trim($('#mintf').val());
        params['mintf'] = $.trim($('#mintf').val());
        params['mindf'] = $.trim($('#mindf').val());
        params['maxdf'] = $.trim($('#maxdf').val());
        params['minwl'] = $.trim($('#minwl').val());
        params['maxwl'] = $.trim($('#maxwl').val());
        params['maxqt'] = $.trim($('#maxqt').val());
        params['maxntp'] = $.trim($('#maxntp').val());
        params['boost'] = $.trim($('#boost').val());
        params['searchterms'] = get_search_term();
        $(".mlt-field").each(function(){
            var raw_num = $(this).attr('id');
            var tidy_num = $.trim(raw_num.substring(raw_num.lastIndexOf('_') + 1));
            if($.trim($(this).val()) != "") params['simfield_' + String(tidy_num)] = $.trim($(this).val());
        });
        $("select.boost-field").each(function(){
            var raw_num = $(this).attr('id');
            var tidy_num = $.trim(raw_num.substring(raw_num.lastIndexOf('_') + 1));
            if($.trim($(this).val()) != "") params['boostfield_' + String(tidy_num)] = $.trim($(this).val());
        });
        $("input.boost-factor").each(function(){

            var raw_num = $(this).attr('id');
            var tidy_num = $.trim(raw_num.substring(raw_num.lastIndexOf('_') + 1));
            var corr_field = "#id_field_" + String(tidy_num)
            // we only include boosts for defined fields
            if($.trim($(corr_field).val()) != "") params['boostfactor_' + String(tidy_num)] = $.trim($(this).val());
        });

        return params;

    }

    var display_related_items = function(data){


        var items_found = data['response']['docs'].length;
        var interesting_terms = data['interestingTerms']
        var header = $("<div id=\"interesting-terms\"><h2>Interesting Terms</h2></div>");
        var term_wrapper = $("<div id=\"term-wrapper\"></div>");
        $(header).append(term_wrapper)
        for(var i = 0; i < interesting_terms.length; i += 2){

            raw_term = interesting_terms[i];
            breakdown = raw_term.split(":");
            field = breakdown[0];
            term = breakdown[1];
            weight = interesting_terms[i + 1];
            $(term_wrapper).append("<span class=\"interest-info\"><span class=\"interest-field\">" + field + "</span>: <span class=\"interest-term\">" + term + "</span> - \
            <span class=\"interest-weight\">" + weight + "</span></span>");
            if((i + 1) < (interesting_terms.length - 1) ){ $(term_wrapper).append(", ");}

        }
        var wrapper = $("#query_results");
        var results_header = $("<h3>Related Items</h3>");
        wrapper.children().remove();    // clear previous results
        if(!items_found){ warn_no_results(data['query']); return false; }
        wrapper.append(header);
        wrapper.append(results_header);
        if(items_found < 1) return false;
        var items_wrapper = $("<ul class=\"result-items\"></ul>");
        wrapper.append(items_wrapper);
        for(var i = 0; i < 10; i++){
              var item = data['response']['docs'][i];
              var title = item['proxy_dc_title'] == undefined ? "Untitled" : item['proxy_dc_title'][0];
              var data_provider = item['DATA_PROVIDER'];
              var desc = item['proxy_dc_description'] == undefined ? "None provided" : item['proxy_dc_description'][0];
              var thumb = item['provider_aggregation_edm_object'];
              var item_url = item['provider_aggregation_edm_isShownAt'] == undefined ? "None provided" : item['provider_aggregation_edm_isShownAt'][0];
              var europeana_id = item['europeana_id'];
              europeana_page = item['europeana_aggregation_edm_landingPage'];
              var object_type = item['proxy_edm_type'][0];
              var hidden = "#id_result_id_" + i;
              $(hidden).val(europeana_id);
              var record = "<li><article class=\"search-list-item cf\"><div class=\"item-preview\">\
              <div class=\"item-image\"><a href=\"" + europeana_page  + "\"><img src=\"" + thumb + "\">\
              </a></div></div><div class=\"item-info\"><h1><a href=\"" + europeana_page + "\">" + title + "</a>\
              </h1><p class=\"excerpt\"><b>Description</b>: " + desc + "</p><div class=\"item-origin\">\
              <a class=\"external\" href=\"" + item_url + "\">View at " + data_provider + "</a>\
              </div>" + build_object_type_html(object_type)  + "</article></li>";
              var record_as_jq = $(record);
              $(items_wrapper).append(record_as_jq);

        }

        // - debugging info $("#query_results").append("<p>" + data['query'] + "</p>");

    }

    var build_object_type_html = function(object_type){

        var pretty_type = " " + object_type.toUpperCase();
        var start = "<footer><div class=\"item-metadata\"><span class=\"highlight\">\
        <svg class=\"icon icon-image\">";
        var end = "</svg><span id=\"init-item-type\" style=\"margin-left:0px;\">" + pretty_type + "</span></span></div></footer>";
        type_to_icon_map = {"TEXT" : "book", "VIDEO" : "tv", "SOUND" : "music"}
        var icon_type = type_to_icon_map[object_type] ? type_to_icon_map[object_type] : "image";
        var icon = "<use xlink:href=\"#icon-" + icon_type + "\"></use>";
        return start + icon + end;

    }

    var size_results_column = function(){

        total_width = $(window).width();
        form_width = $("#user_form").width();
        results_width = total_width - form_width - 65;
        $(".results-list").width(results_width);


    }

    var display_init_item = function(data){

        europeana_id = data['europeana_id'];
        $("#init-item-warning-wrapper").remove();
        if(europeana_id == 'no-item-found'){

            warn_no_init_result($("#id_searchterm").val());
            return false;

        }
        size_results_column();
        $("#init-item-display").css({ "visibility" : "visible" });
        title = typeof data['title'] !== 'undefined' ? data['title'] : "No title given";
        desc = typeof data['description'] !== 'undefined' ? data['description'] : "No description given";
        url = data['url'];
        thumb = data['thumbnail'];
        type = data['resource_type'];
        data_provider = data['data_provider'];
        original_page = data['original_page'];
        $("#init-item-inner-landing-page").text(title);
        $("#init-item-desc").text(desc);
        $("#init-item-landing-page").attr("href", url);
        $("#init-item-thumbnail").attr("src", thumb);
        $("#init-item-type").text(type);
        $("#init-item-ext-link").attr("href", original_page);
        $("#init-item-data-provider").text(data_provider);
        $("#europeana-id").val(europeana_id);

    }

    init();
    $("#launch-init-query").click(start_with_new_init_item);
    $("#launch-query").click(retrieve_related_items);
    init();

})