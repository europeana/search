$(document).ready(function(){

    var display_items = function(response){

        $("#loading").remove();
        if(response['duplicate']){ show_duplicate_key_warning(); return false; }
        var items_found = response['totalResults'];
        if(!items_found){ warn_no_results() }
        var items_returned = response['itemsCount'];
        var header = $("<div class=\"results-header\"><div id=\"summary\" class=\"result-info\">Top <span id=\"items-returned\"\
        >" + items_returned + "</span> items from <span id='items-found'>" + items_found + "</span> found.</div></div>");
        if($("#rating-warning").length){

            var rating_warning = $("#rating-warning").remove();
            $(header).append(rating_warning);
        }
        var wrapper = $("#query_results");
        wrapper.children().remove();    // clear previous results
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
              $(".star-stub").addClass("star").rating();    // need to trigger the plugin

        }

        indicate_star_state();
        display_rating_errors();
    }

    var launch_query = function(){

        var entered_text = $.trim($(this).val());
        var prev_text = $.trim($("#prev-query").val());
        if(prev_text != entered_text){
            clear_previous_ratings();
            clear_no_result_warning();
            clear_duplicate_key_warning();
        }
        if(entered_text != ""){
            $("#prev-query").val(entered_text);
            var request = {};
            request['query'] = entered_text;
            if(prev_text != entered_text) add_loader();
            $.ajax({url:'loc', data:request, dataType:"json"}).done(function(data){ display_items(data);  });
        }
    }

    var build_object_type_html = function(object_type){

        var pretty_type = " " + object_type.toUpperCase().substring(0, 1) + object_type.toLowerCase().substring(1);
        var start = "<footer><div class=\"item-metadata\"><span class=\"highlight item-type\">\
        <svg class=\"icon icon-image\">";
        var end = "</svg>" + pretty_type + "</span></div></footer>";
        type_to_icon_map = {"TEXT" : "book", "VIDEO" : "tv", "SOUND" : "music"}
        var icon_type = type_to_icon_map[object_type] ? type_to_icon_map[object_type] : "image";
        var icon = "<use xlink:href=\"#icon-" + icon_type + "\"></use>";
        return start + icon + end;

    }

    var add_loader = function(){

            var loading = $("<span id=\"loading\"></span>");
            var input_width = $("#id_test_query").width();
            var input_height = $("#id_test_query").height();
            var p = $("#id_test_query").parent("p");
            p.css({ "position" : "relative" })
            loading.css({ "left" : (input_width) + "px", "top" : (input_height + 22) + "px" });
            p.append(loading);

    }

    var get_stars = function(item_list_position, item_id){

        var ilp = $.trim(item_list_position);
        var iid = $.trim(item_id);
        var stars = "<div id=\"rater-" + ilp + "\" class=\"relevance-rater\">\
             <span class=\"star-label\">Relevance rating:</span>\
             <input name='star" + ilp + "' type='radio' class='star-stub'/>\
             <input name='star" + ilp + "' type='radio' class='star-stub'/>\
             <input name='star" + ilp + "' type='radio' class='star-stub'/>\
             <input name='star" + ilp + "' type='radio' class='star-stub'/>\
             <input name='star" + ilp + "' type='radio' class='star-stub'/><br/></div>";
        return stars;

    }

    var indicate_star_state = function(){

        $(".rating-cancel").append("or ");
        var not_relevant_button = $("<span class=\"not-relevant\">Not relevant</span>");
        $(".rating-cancel").append(not_relevant_button);
        var num_raters = $(".relevance-rater").length;
        for(var i = 0; i < num_raters; i++){

            var rater_selector = "div#rater-" + i;
            var star_selector = rater_selector + " input.star";
            var rating_selector = "#id_result_rating_" + i;
            var rating = $(rating_selector).val();
            if(rating == ""){

                return false;

            }
            else if(rating > 0){

               rating -= 1;
               var checked = $(star_selector).get(rating);
               $(checked).click();
            }
            else if(rating == 0){

                var cancel_selector = rater_selector + " .not-relevant";
                $(cancel_selector).click();

            }
        }

    }

    var mark_not_relevant = function(){

        var pos = $(this).parents("li").prevAll("li").length;
        var hidden_field = "#id_result_rating_" + pos;
        $(hidden_field).val(0);
        $(this).addClass("rating-cancelled");

    }

    var set_relevance = function(){

       var pos = $(this).parents("li").prevAll("li").length;
       var hidden_field = "#id_result_rating_" + pos;
       var val = $(this).prevAll(".star").length + 1;
       $(hidden_field).val(val);
       $(this).parents(".relevance-rater").find(".rating-cancelled").removeClass("rating-cancelled");
    }

    var set_unused_relevance = function(){

        var allowed_no_hits = $(".euro-id:not(#id_result_id_0)").filter(function(){ return $(this).val() == ""; });
        allowed_no_hits.val("no-item-found");
        allowed_no_hits.next(".rel-rating").val(0);

    }

    var clear_previous_ratings = function(){

        var result_ids = $(".euro-id");
        var result_ratings = result_ids.next(".rel-rating");
        $(result_ids).val("");
        $(result_ratings).val("");

    }

    var clear_no_result_warning = function(){

        var no_results = $("#no-results-warning").remove();
        $("#warnings").append(no_results);
        $(no_results).css({"display" : "none"});

    }

    var clear_empty_field_warning = function(){

        $(this).siblings(".error-text").remove();
        $(this).removeClass("field-error");

    }

    var sense_keystroke = function(keyboard){

        if($("form p #no-results-warning").length){

            clear_no_result_warning();

        }
        if($("form p #duplicate-key-warning").length){

            clear_duplicate_key_warning();

        }
        if($(this).hasClass("field-error")){

            clear_empty_field_warning.apply(this);

        }
        if($("ul.errorlist.nonfield li:contains('result_')").length){

            $("ul.errorlist.nonfield li:contains('result_')").remove();

        }
        if(keyboard.which == 13){

            $("#lang-selector").focus();
            return false;

        }

    }

    var enable_submit = function(){

        $("#continue").prop("disabled", false)

    }

    var warn_no_results = function(){

        var warning = $("#no-results-warning").remove();
        $(warning).insertAfter("#id_test_query");
        $(warning).css({ "display" : "block" });

    }

    var display_standard_errors = function(){

        $("ul.errorlist:not(.nonfield)").each(function(){

            var msg = $(this).text();
            var field = $(this).next("p");
            var control = $(field).children("input, select");
            $(control).addClass("field-error");
            var wrapper = $("<div class=\"error-text\">" + msg + "</div>");
            wrapper.insertAfter(control);

        });

    }

    var display_rating_errors = function(){

       if($("ul.errorlist.nonfield li:contains('result_rating_')").length){

            var rating_warning = $("#rating-warning").remove();
            rating_warning.insertAfter("#summary");
            $(rating_warning).css({ "display" : "block" });
            // TODO: red CSS on items without a rating
            $("ul.errorlist.nonfield li:contains('result_rating_')").each(function(){

                var raw_text = $(this).text();
                var num_snippet = raw_text.substring(raw_text.indexOf("result_rating_") + "result_rating_".length, raw_text.lastIndexOf(")"));
                var item = $(".search-list-item").get(num_snippet);
                $(item).find(".relevance-rater").addClass("rating-missing");

            });


       }

    }

    var clear_duplicate_key_warning = function(){

        var warning = $("#duplicate-key-warning").remove();
        $("#warnings").append(warning);
        $("#warnings").css({ "display" : "none" });

    }

    var show_duplicate_key_warning = function(){

         var warning = $("#duplicate-key-warning").remove();
         $(warning).insertAfter("#id_test_query");
         $(warning).css({ "display" : "block" });

    }

    var show_thank_you = function(){

        var thanks = $("<p id=\"thank-you\">Thank you for your query submission - and for trying another!</p>");
        $("#query_results").append(thanks);
        $("#id_test_query").focus();

    }

    var check_logout = function(){

            var msg = "This form is still missing data! If you leave the page now, your query will not be submitted. Are you sure you want to leave?";
            if(confirm(msg)){
                window.location = "/accounts/logout";
                return false;
            }
            else{
                $("ul.errorlist.nonfield li:contains('logout')").remove();
                launch_query.apply($("#id_test_query"));
                return false;
            }
    }

    var start_state = function(){

        if($("ul.errorlist.nonfield li:contains('logout')").length){

            check_logout();

        }
        else if($("#duplicate-key").val() == "T"){

            show_duplicate_key_warning();

        }
        else if($("#duplicate-key").val() == "F" && $("#id_test_query").val() == ""){

            show_thank_you();

        }
        else if($("#id_test_query").val() != ""){

            launch_query.apply($("#id_test_query"));

        }

        display_standard_errors();

    }

    start_state();

    $("#query_results").on('click', '.not-relevant', mark_not_relevant);
    $("#query_results").on('click', '.star-stub', set_relevance)
    $("#id_test_query").blur(launch_query);
    $("#id_test_query").mouseout(launch_query);
    $("#id_test_query").keydown(sense_keystroke);
    $("#continue, #quit").click(set_unused_relevance);
    $("#lang-selector").click(clear_empty_field_warning);

});

