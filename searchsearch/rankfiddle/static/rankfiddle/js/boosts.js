$(document).ready(function(){

    var init = function(){

        make_field_boosts_first();
        hide_extra_field_boosts();
        add_field_adders();
        line_up_slops();
        $("#weightview-selector").prev("p").css("display", "inline");
        $("#weightview-selector").prev("p").css("float", "left");
        $("#weightview-selector").prev("p").css("min-height", "10px");
        reflow_result_columns();

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
        $("ul.result-items li").closest("div.results-list").css("border-right", "thin solid black");
        longest_list_count = Math.max($("#query-results-weighted ul.result-items li").length, $("#query-results-unweighted ul.result-items li").length, $("#query-results-bm25f ul.result-items li").length);
        for(var i = 0; i < longest_list_count; i++){
            var highest = Math.max($("#query-results-weighted ul.result-items li:eq(" + i + ")").innerHeight(), $("#query-results-unweighted ul.result-items li:eq(" + i + ")").innerHeight(), $("#query-results-bm25f ul.result-items li:eq(" + i + ")").innerHeight());
            var prev_total;
            $("ul.result-items").each(function(){

                nth_li = $(this).children("li")[i];
                $(nth_li).children(".search-list-item").innerHeight(highest);
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
    $("#query-freetext").focus(deactivate_query_selector);
    $("#query-selector").focus(deactivate_query_freetext);
    $("input[name='weight_views']").click(query_for_new_view);
    $("#launch-query").click(check_query_exists);

  // TODO: MoreLikeThis fiddle


})