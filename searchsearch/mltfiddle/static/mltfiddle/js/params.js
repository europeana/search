$(document).ready(function(){

    var init = function(){




    }

    var start_with_new_init_item = function(){

        return retrieve_init_item();

    }

    var retrieve_init_item = function(){

        request = {};
        request['searchterms'] = get_search_term();
        $.getJSON('inititem', request, display_init_item);
        return false;

    };

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
        params['europeana_id'] = $.trim($("#init-item-id").text());
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
        $(".boost-field").each(function(){
            var raw_num = $(this).attr('id');
            var tidy_num = $.trim(raw_num.substring(raw_num.lastIndexOf('_') + 1));
            if($.trim($(this).val()) != "") params['boostfield_' + String(tidy_num)] = $.trim($(this).val());
        });
        $(".boost-factor").each(function(){

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
        var header = $("<div class=\"results-header\"><div id=\"summary\" class=\"result-info\">Top <span id=\"items-returned\"\
        >" + items_returned + "</span> items from <span id='items-found'>" + items_found + "</span> found.</div></div>");
        var wrapper = $("#query_results");
        wrapper.children().remove();    // clear previous results
     //   if(response['duplicate']){ show_duplicate_key_warning(); return false; }
        if(!items_found){ warn_no_results(); return false; }
        wrapper.append(header);
        if(items_returned < 1) return false;
        var items_wrapper = $("<ul class=\"result-items\"></ul>");
        wrapper.append(items_wrapper);
        for(var i = 0; i < items_returned; i++){
              var item = response['items'][i];
              var title = item['title'];
              var lang = item['language'] == undefined ? "None provided" : item['language'];
              var data_provider = item['dataProvider'];
              var country = item['country'] == undefined ? "None provided" : item['country'][0];
              var desc = item['dcDescription'] == undefined ? "None provided" : item['dcDescription'];
              var thumb = item['edmPreview'];
              var item_url = item['edmIsShownAt'];
              var europeana_id = item['id'];
              europeana_page = item['guid'];
              var all_concepts = item['edmConceptTerm'];
              var object_type = item['type'];
              var hidden = "#id_result_id_" + i;
              $(hidden).val(europeana_id);
              var record = "<li><article class=\"search-list-item cf\"><div class=\"item-preview\">\
              <div class=\"item-image\"><a href=\"" + europeana_page  + "\"><img src=\"" + thumb + "\">\
              </a></div></div><div class=\"item-info\"><h1><a href=\"" + europeana_page + "\">" + title + "</a>\
              </h1>" + get_stars(i, europeana_id) + "<p class=\"excerpt\"><b>Description</b>: " + desc + "</p><div class=\"item-origin\">\
              <a class=\"external\" href=\"" + item_url + "\">View at " + data_provider + "</a>\
              </div>" + build_object_type_html(object_type)  + "</article></li>";
              var record_as_jq = $(record);
              $(items_wrapper).append(record_as_jq);


        }
        // if(query_is_new()){  reset_prev_query();}


    }

    var display_init_item = function(data){

        title = data['title'];
        desc = data['description'];
        europeana_id = data['europeana_id'];
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
        $("#init-item-id").text(europeana_id);

    }

    var reflow_result_columns = function(){

        column_count = 0;
        if($("#query-results-weighted ul.result-items li").length > 0) column_count++;
        if($("#query-results-unweighted ul.result-items li").length > 0) column_count++;
        if($("#query-results-bm25f ul.result-items li").length > 0) column_count++;
        $("ul.result-items li").closest(".results-list").css("display", "block");
        if(column_count < 2) return;
        display_width = 66; // TODO: set this dynamically
        column_width = display_width / column_count;
        column_width = column_width.toString() + '%';
        $(".results-list").css("width", column_width);
        $("div.results-list").css("border-right", "thin solid black");
        longest_list_count = Math.max($("#query-results-weighted ul.result-items li").length, $("#query-results-unweighted ul.result-items li").length, $("#query-results-bm25f ul.result-items li").length);
        for(var i = 0; i < longest_list_count; i++){
            var highest = Math.max($("#query-results-weighted ul.result-items li:eq(" + i + ")").innerHeight(), $("#query-results-unweighted ul.result-items li:eq(" + i + ")").innerHeight(), $("#query-results-bm25f ul.result-items li:eq(" + i + ")").innerHeight());
            var prev_total;
            $("ul.result-items").each(function(){

                nth_li = $(this).children("li")[i];
                $(nth_li).children(".search-list-item").innerHeight(highest);
                if(prev_total != undefined && i >= prev_total)$(nth_li).css("border-left", "thin solid black");
                prev_total = $(this).children("li").length;
            });
        }
    }

    var deactivate_query_freetext = function(){

        $(this).attr('disabled', false);
        $("#query-freetext").val('');

    }

    var deactivate_query_selector = function(){

        $(this).attr('disabled', false);
        $("#query-selector").val('');

    }

    var make_field_boosts_first = function(){

        var last_add = $("p:has('#query-selector')");
        var field_type;
        $("p:has('.boost-field')").each(function(){

            if($(this).children('.phrase-boost-field').length > 0){ field_type = "phrase"; }
            else if($(this).children('.bigram-boost-field').length > 0){ field_type = "bigram"; }
            else if($(this).children('.trigram-boost-field').length > 0){ field_type = "trigram"; }
            else{ field_type = "standard"; }
            var factor = $(this).next("p");
            var wrapper = $("<div class=\"boost " + field_type + "\"></div>");
            wrapper.append($(this).remove());
            wrapper.append(factor.remove());
            wrapper.insertAfter(last_add);
            last_add = wrapper;

        });

    }

    var hide_extra_field_boosts = function(){

        $("div.standard").each(function(){
            if($(this).prevAll("div.standard").length > 7){
                $(this).css({ "display" : "none" });
                $(this).addClass("extra-field");
            }
        });

        $("div.phrase").each(function(){
            if($(this).prevAll("div.phrase").length > 4){
                $(this).css({ "display" : "none" });
                $(this).addClass("extra-field");
            }
        });

        $("div.bigram").each(function(){
            if($(this).prevAll("div.bigram").length > 0){
                $(this).css({ "display" : "none" });
                $(this).addClass("extra-field");
            }
        });

        $("div.trigram").each(function(){
            if($(this).prevAll("div.trigram").length > 0){
                $(this).css({ "display" : "none" });
                $(this).addClass("extra-field");
            }
        });

    }

    var add_field = function(){

        var field_type = $(this).attr("id").replace(/-field-adder/, '');
        selector = "div." + field_type + ".extra-field:first";
        $(selector).css({"display":"block"});
        $(selector).removeClass("extra-field");

    }

    var add_field_adders = function(){

        // first, we clear any previously-added buttons
        $("div#standard-field-adder").remove();
        $("div#phrase-field-adder").remove();
        $("div#bigram-field-adder").remove();
        $("div#trigram-field-adder").remove();

        var standard_adder = $("<div id=\"standard-field-adder\" class=\"field-adder\">Add boost field</div>");
        standard_adder.insertAfter($("div.standard:last"));
        $("div#standard-field-adder").click(add_field);

        var phrase_adder = $("<div id=\"phrase-field-adder\" class=\"field-adder\">Add phrase-boost field</div>");
        phrase_adder.insertAfter($("div.phrase.boost:last"));
        $("div#phrase-field-adder").click(add_field);

        var bigram_adder = $("<div id=\"bigram-field-adder\" class=\"field-adder\">Add bigram-boost field</div>");
        bigram_adder.insertAfter($("div.bigram:last"));
        $("div#bigram-field-adder").click(add_field);

        var trigram_adder = $("<div id=\"trigram-field-adder\" class=\"field-adder\">Add trigram-boost field</div>");
        trigram_adder.insertAfter($("div.trigram:last"));
        $("div#trigram-field-adder").click(add_field);

    }

    var line_up_slops = function(){

        $("p:has('.slop')").each(function(){ $(this).addClass("para-slop"); });

    }

    var check_query_exists = function(){

        var freetext = $.trim($("#query-freetext").val())
        var dropdown = $.trim($("#query-selector").val())
        submitted_query = dropdown == '' ? freetext : dropdown;
        if(submitted_query == ''){

            alert('Please enter or select a query term!');
            return false;

        }

        return true;

    }

    var query_for_new_view = function(){

        var freetext = $.trim($("#query-freetext").val())
        var dropdown = $.trim($("#query-selector").val())
        submitted_query = dropdown == '' ? freetext : dropdown;
        if(submitted_query != ''){

            $("#launch-query").click();

        }
    }

    init();
/*    $("#query-freetext").focus(deactivate_query_selector);
    $("#query-selector").focus(deactivate_query_freetext);
    $("input[name='weight_views']").click(query_for_new_view);
    $("#launch-query").click(check_query_exists);


*/

    $("#launch-init-query").click(start_with_new_init_item);
    $("#launch-query").click(retrieve_related_items)

})