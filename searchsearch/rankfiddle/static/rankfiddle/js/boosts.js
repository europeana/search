$(document).ready(function(){


    var make_field_boosts_first = function(){

        var last_add = $("p:has('#query-selector')");

        $("p:has('.boost-field')").each(function(){

            var factor = $(this).next("p");
            var wrapper = $("<div class=\"boost\"></div>");
            wrapper.append($(this).remove());
            wrapper.append(factor.remove());
            wrapper.insertAfter(last_add);
            last_add = wrapper;

        });

    }

    var hide_extra_field_boosts = function(){

        $("div.boost").each(function(){

            if($(this).prevAll("div.boost").length > 7){

                $(this).css({ "display" : "none" });
                $(this).addClass("extra-field");

            }

        });

    }

    var add_field = function(){

        $("div.extra-field:first").css({"display":"block"});
        $("div.extra-field:first").removeClass("extra-field");

    }

    var add_field_adder = function(){

        $("div#field-adder").remove();
        var adder = $("<div id=\"field-adder\">Add boost field</div>");
        adder.insertAfter($("div.boost:last"));
        $("div#field-adder").click(add_field);

    }

    var line_up_slops = function(){

        $("p:has('.phrase')").each(function(){ $(this).addClass("para-phrase")});
        $("p:has('.slop')").each(function(){ $(this).addClass("para-slop"); });

    }

    make_field_boosts_first();
    hide_extra_field_boosts();
    add_field_adder();
    line_up_slops();


})