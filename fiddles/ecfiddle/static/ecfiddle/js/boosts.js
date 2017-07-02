$(document).ready(function(){

    var init = function(){

        columnate();
        init_autocomplete();
        $("input[name=clause_0_operator]").prop("disabled", true);
        $(".operator-wrapper .clause_0_group.column_1 * label").css({ "color" : "#aaa", "font-style" : "italic" });
        $(".operator-wrapper .clause_0_group.column_1 label").css({ "color" : "#aaa", "font-style" : "italic" });

    }

    var init_autocomplete = function(){

        var options = {

            url: function(frag) {
            return "http://test-entity.europeana.eu/entity/suggest?wskey=apidemo&rows=10&text=" + frag;
            },
            list: { match: { enabled: true },
                    onChooseEvent: function() {
                        global_search = $("#id_picked_entity").getSelectedItemData()
                        var value = trim_autocomplete_msg(concatenate_autocomplete_msg(global_search));
                        $("#id_picked_entity").val(value);
            }},
            listLocation: "contains",
            getValue: concatenate_autocomplete_msg

        }

        $("#id_picked_entity").easyAutocomplete(options);

    }

    var concatenate_autocomplete_msg = function(element){

        var label = element.prefLabel;
        var expansion_label = element.hiddenLabel.join("; ");
        var uri = element.id;
        var cat = element.type;
        var msg = label;
        if(expansion_label != label){ msg += "<br>Expansion Labels: " + expansion_label; }
        msg += "<br>type: " + cat;
        msg += "<br>(" + uri + ")";
        return msg;                  

    }

    var trim_autocomplete_msg = function(current_msg){

        var msg = current_msg.replace(/<br>/g, ", ");
        return msg;

    }

    var columnate = function(){

      $("p:empty").each(function(){

            $(this).remove();

        });

        $("#user_form").children("form").first().children().each(function(){

            if($(this).attr("type") == "hidden"){

                return true;

            }
            else if($(this).attr("id") == "launch-query"){

                return true;

            }
            else if($(this).children("label").first().attr("for") == "id_picked_entity"){

                return true;

            }
            else{

                var identifier = get_current_identifier($(this));
                var clause_type = get_current_clause_type($(this));
                var clause_group = get_clause_group(identifier, clause_type);
                var clause_number = get_clause_number(clause_group);
                var control_function = get_control_function(identifier);
                $(this).addClass(clause_group);
                $(this).addClass(clause_type);
                $(this).addClass(control_function + "_" + clause_number);
                $(this).addClass(get_column($(this)));
            }

        });

        for(var i = 0; i < 4; i++){

            $(".operator_" + i.toString()).wrapAll("<div class=\"operator-wrapper\"></div>");
            $(".mode_" + i.toString()).wrapAll("<div class=\"mode-wrapper\"></div>");

            for(var j = 0; j < 4; j++){

                new_id = i.toString() + "_" + j.toString();
                $(".operator_" + new_id).wrapAll("<div class=\"operator-wrapper\"></div>");
                $(".mode_" + new_id).wrapAll("<div class=\"mode-wrapper\"></div>");


            }

        }

        $(".operator-wrapper").each(function(){

            $(this).children(".column_1").wrapAll("<div class=\"column-1-wrapper\">");
            $(this).children(".column_2").wrapAll("<div class=\"column-2-wrapper\">");


        });

        $(".mode-wrapper").each(function(){

            $(this).children(".column_1").wrapAll("<div class=\"column-1-wrapper\">");
            $(this).children(".column_2").wrapAll("<div class=\"column-2-wrapper\">");


        });

        $(".activator").prev().addClass("activator-label");




    }

    var get_column = function(current_element){

        if($(current_element).find(".clause-field").length > 0){

            return "column_2";

        }
        else if($(current_element).children("input.clause-value").length > 0){

            return "column_2";

        }
        else if($(current_element).find(".subclause-field").length > 0){

            return "column_2";

        }
        else if($(current_element).children("input.subclause-value").length > 0){

            return "column_2";

        }
        else{


            return "column_1";

        }


    }

    var get_clause_group = function(identifier, clause_type){

        cid = identifier;
        cty = clause_type;
        idno = /[a-z_]+([\d])/.exec(cid)
        idid = ""
        if(cty == "clause"){

            idid = idno[1].toString();

        }
        else if(cty == "subclause"){

            idid = idno[1].toString() + "_" + /[a-z_]+[\d]_([\d])/.exec(cid)[1];

        }
        group = cty + "_" + idid + "_group";
        if(idid == ""){ group = ""; }
        return group;

    }

    var get_clause_number = function(clause_group){

        nogroup = clause_group.replace(/_group/, "");
        noclause = nogroup.replace(/(sub)?clause_/, "");
        return noclause;

    }

    var get_control_function = function(current_identifier){

        if(current_identifier.includes("mode")){

            return "mode";

        }
        else if(current_identifier.includes("field")){

            return "operator";

        }
        else if(current_identifier.includes("operator")){

            return "operator";

        }
        else if(current_identifier.includes("value")){


            return "mode";

        }
        else{

            return "";

        }

    }

    var get_current_identifier = function(current_element){

        var current_identifier;
        if(typeof $(current_element).attr("id") != "undefined"){

            current_identifier = $(current_element).attr("id");

        }
        else{

            current_identifier = $(current_element).children("label").first().attr("for");

        }

        return current_identifier;

    }

    var get_current_clause_type = function(current_element){

        var cid = get_current_identifier(current_element);
        if(cid.includes("subclause")){ 

            return "subclause";

        }
        else{

            return "clause";

        }

    }



  
    init();

})