$(document).ready(function(){


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

        // TODO: align these with relevant page section
        $("p:has('.phrase')").each(function(){ $(this).addClass("para-phrase")});
        $("p:has('.slop')").each(function(){ $(this).addClass("para-slop"); });

    }

    make_field_boosts_first();
    hide_extra_field_boosts();
    add_field_adders();
  //  line_up_slops();

  // TODO: MoreLikeThis fiddle


})