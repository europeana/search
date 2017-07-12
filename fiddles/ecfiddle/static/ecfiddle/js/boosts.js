$(document).ready(function(){

    var init = function(){

        columnate();
        init_autocomplete();
        init_disabled();

    }

    var init_autocomplete = function(){

        var options = {

            url: function(frag) {
            return "http://test-entity.europeana.eu/entity/suggest?wskey=apidemo&rows=10&text=" + frag;
            },
            list: { match: { enabled: true },
                    onChooseEvent: function() {
                        global_search = $("#id_picked_entity").getSelectedItemData()
                        querify_global_search();
                        var value = trim_autocomplete_msg(concatenate_autocomplete_msg(global_search));
                        $("#id_picked_entity").val(value);
                        populate_query(global_search);
            }},
            listLocation: "contains",
            getValue: concatenate_autocomplete_msg

        }

        $("#id_picked_entity").easyAutocomplete(options);

    }

    var init_disabled = function(){

        $("input[name=clause_0_operator]").prop("disabled", true);
        $("#id_clause_0_activator").prop("disabled", true);
        $(".operator-wrapper .clause_0_group.column_1 * label").css({ "visibility" : "hidden" });
        $(".operator-wrapper .clause_0_group.column_1 label").css({ "visibility" : "hidden" });
        $("input.activator").each(function(){

            check_clause_state.call(this);

        });
        disable_clause($("#id_subclause_0_0_activator").parent("p"));

    }

    var populate_query = function(entity){

        $("input.search-terms:enabled").each(function(){

            var display_value = $.trim($(this).parents("div.mode-wrapper").find("input:checked").val()) == "URL" ? entity.id : entity.as_query; 
            $(this).val(display_value);
            enable_clause($(this).parents("div.mode-wrapper").next("p.activator-wrapper"));
            if($(this).is(".clause")){

                enable_clause($(this).parents("div.mode-wrapper").nextAll("p.activator-wrapper.clause").first());   

            }

        });

    }

    var querify_global_search = function(){

        var raw_hidden_label = global_search.hiddenLabel;
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

        $(".activator").parent("p").addClass("activator-wrapper");
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

    var check_clause_state = function(){

        if($(this).is(":checked")){

            $(this).parent("p").nextUntil("p.activator-wrapper").each(function(){

                enable_clause(this);

            });

        }
        else{

            $(this).parent("p").nextAll().each(function(){

                disable_clause(this);

            });
            var prev_clause_field = $(this).parent("p").next(".operator-wrapper").find("select").val();
            if(prev_clause_field){

                var next_clause_activator_p = $(this).parent("p").nextAll("p.clause.activator-wrapper");
                $(next_clause_activator_p).removeClass("disabled-panel");
                $(next_clause_activator_p).find("input").first().prop("disabled", false);
            
            }
        }
       
    }

    var enable_clause = function(el){

        $(el).find("input").prop("disabled", false);
        $(el).find("select").prop("disabled", false);
        $(el).removeClass("disabled-panel");
        $(el).removeClass("disabled-panel");
        repopulate_query.call($(el).find("input[type=text]"));

    }

    var disable_clause = function(el){

        $(el).find("input").prop("disabled", true);
        $(el).find("input.search-terms").val("");
        $(el).find("select").prop("disabled", true);
        $(el).find("select").val("");
        $(el).addClass("disabled-panel");
        $(el).addClass("disabled-panel");
    }

    var retrieve_items = function(){

        var query = build_all_clauses();
        alert(query);

    }

    var build_all_clauses = function(){

        var clause = ""; 
        $("p.clause.activator-wrapper").has("input:checked").each(function(){

            var clause_bits = get_clause_elements(this);
            all_subclause_elements = [];
            $(this).nextUntil("p.clause.activator-wrapper").each(function(){

                if($(this).is("p.subclause.activator-wrapper") && $(this).children("input.activator").first().is(":checked")){
                    var subclause_elements = get_clause_elements($(this));
                    all_subclause_elements.push.apply(all_subclause_elements, subclause_elements);

                }


            });

            var operator = clause_bits[0];
            if(typeof operator === undefined){ 

                operator = "";

            }
            else{

                operator = " " + operator + " ";

            }
            start_delimiter = "(";
            end_delimiter = ")";
            var current_clause = operator + start_delimiter + clause_bits[1] + " " + all_subclause_elements.join(" ") + end_delimiter;
            clause += current_clause;

        });
        // get rid of initial AND as superfluous
        clause = clause.replace(/^ AND /, "");
        return clause;
    }

    var get_clause_elements = function(first_element){

        var operator_element = $(first_element).next("div.operator-wrapper");
        var mode_element = $(operator_element).next("div.mode-wrapper");
        var operator = $(operator_element).find("input:checked").first().val();
        var fieldname = $(operator_element).find("select").val();
        var mode_value = $.trim($(mode_element).find("input.search-terms").val());
        if(mode_value.charAt(0) != "\"" && mode_value.charAt(0) != "("){ 

            mode_value = "\"" + mode_value + "\"";

        }
        var clause_value = fieldname + ":" + mode_value;
        return [operator, clause_value];

    }

    var check_next_activator_status = function(){

        var next_activator_p = get_next_activator(this);
        var next_clause_activator_p = get_next_clause_activator(this);
        var next_activator = $(next_activator_p).find("input").first();
        var next_clause_activator = $(next_clause_activator_p).find("input").first();
        var inactive = $(this).val() == "";
        if(inactive){

            $(next_activator_p).addClass("disabled-panel");
            $(next_clause_activator_p).addClass("disabled-panel");

        }
        else{

            $(next_activator_p).removeClass("disabled-panel");
            $(next_clause_activator_p).removeClass("disabled-panel");

        }

        $(next_activator).prop("disabled", inactive);
        $(next_clause_activator).prop("disabled", inactive);

    }

    var get_next_activator = function(el){

        var next_activator = $(el).parents(".operator-wrapper").nextAll(".activator-wrapper").first();
        return next_activator;

    }

    var get_next_clause_activator = function(el){

        var next_clause_activator = $(el).parents(".operator-wrapper").nextAll("p.clause.activator-wrapper").first();
        return next_clause_activator;

    }

    $("#launch-query").click(retrieve_items);
    $("input[type=checkbox]").change(check_clause_state);
    $("input.mode-value").change(repopulate_query);
    $("select").change(check_next_activator_status);
    init();

})