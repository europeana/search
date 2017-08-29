$(document).ready(function(){


	var init_new_query = function(){

        $.ajax({
            type: "GET",
            url: "init",
            cache: false,
            dataType: "xml",
            success: function(xml) {

            		build_control_tree($(xml), $("#clause-controllers"));
 
                }
            });

	}

	var build_control_tree = function(xml, parent_element){

		$(xml).children().each(function(){

			tag_type = $(this).prop("tagName");
			if(tag_type == "clause-group"){

				clause_group_controls = render_clause_group($(this));
				$(parent_element).append(clause_group_controls);
			}
			else if(tag_type == "clause"){

				clause_controls = render_clause($(this));
				$(parent_element).append(clause_controls);

			}
			else if(typeof tag_type != 'undefined'){

				var new_root = $(this);
				build_control_tree(new_root, parent_element);

			}


		});

	}

	var render_clause_group = function(xml){

		var node_id = $(xml).attr("node-id");
		var is_negated = $(xml).attr("negated");
		var is_deprecated = $(xml).attr("deprecated");
		var operator = $(xml).attr("operator");
		var cg_wrapper = $("<div class=\"clause-group\" id=\"" + node_id + "\"></div>");
		var lbl = $("<h3>Clause Group</h3>");
		var ops_wrapper = $("<div class=\"ops-wrapper\"></div>");
		var neg_control = create_negated_control(is_negated);
		var op_control = create_op_control(operator);
		var button_set = create_group_button_set();
		$(ops_wrapper).append(op_control);
		$(ops_wrapper).append(neg_control);
		$(cg_wrapper).append(lbl);
		$(cg_wrapper).append(ops_wrapper);
		$(cg_wrapper).append(button_set);
		build_control_tree(xml, $(cg_wrapper));
		return $(cg_wrapper);

	}

	var render_clause = function(xml){
		// note that clauses are leaf nodes by definition
		// no need for recursion here
		var node_id = $(xml).attr("node-id");
		var is_negated = $(xml).attr("negated");
		var is_deprecated = $(xml).attr("deprecated");
		var operator = $(xml).attr("operator");
		var all_fields = $(xml).find("all-fields").text();
		var ops_wrapper = $("<div class=\"ops-wrapper\"></div>");
		var op_control = create_op_control(operator);
		var neg_control = create_negated_control(is_negated);
		var button_set = create_clause_button_set();
		var inputs = create_clause_inputs(all_fields);
		var cl_wrapper = $("<div class=\"clause\" id=\"" + node_id + "\"><h3>Clause</h3></div>");
		$(ops_wrapper).append(op_control);
		$(ops_wrapper).append(neg_control);
		$(cl_wrapper).append(ops_wrapper);
		$(cl_wrapper).append(button_set);
		$(cl_wrapper).append(inputs);
		return $(cl_wrapper);

	}

	var create_op_control = function(operator){

		var controls = $("<div class=\"operator-radio-set\"></div>");
		var and_control = $("<input type=\"radio\" class=\"operator-radio\" name=\"operator\" value=\"AND\">AND</input>");
		var or_control = $("<input type=\"radio\" class=\"operator-radio\" name=\"operator\" value=\"OR\">OR</input>");
		$(controls).append(and_control);
		$(controls).append(or_control);
		if(operator == "AND"){

			$(and_control).attr("checked", "checked");

		}
		else if(operator == "OR"){

			$(or_control).attr("checked", "checked");

		}

		return controls;

	}

	var create_negated_control = function(is_negated){

		var controls = $("<div class=\"negated-wrapper\">Negated (NOT): </div>");
		var neg = $("<input type=\"checkbox\" class=\"negcheck\" value=\"negated\"></input>");
		$(controls).append(neg)
		if(is_negated == true){

			$(neg).attr("checked", "checked");

		}

		return controls;

	}

	var create_group_button_set = function(){

		var wrapper = $("<div class=\"button-set\"><div>");
		var add_cg = $("<div class=\"button-control add-cg\">Add Clause Group</div>");
		var add_cl = $("<div class=\"button-control add-cl\">Add Clause</div>");
		var con = $("<div class=\"button-control convert-to-cl\">Convert to Clause</div>");
		var dep = $("<div class=\"button-control deprecate\">Deprecate</div>");
		var del = $("<div class=\"button-control delete\">Delete</div>");
		$(wrapper).append(add_cg);
		$(wrapper).append(add_cl);
		$(wrapper).append(con);
		$(wrapper).append(dep);
		$(wrapper).append(del);
		return $(wrapper);

	}

	var create_clause_button_set = function(){

		var wrapper = $("<div class=\"button-set\"><div>");
		var con = $("<div class=\"button-control convert-to-cg\">Convert to Clause Group</div>");
		var dep = $("<div class=\"button-control deprecate\">Deprecate</div>");
		var del = $("<div class=\"button-control delete\">Delete</div>");
		var exp = $("<div class=\"button-control expand\">Expand</div>");
		$(wrapper).append(con);
		$(wrapper).append(dep);
		$(wrapper).append(del);
		$(wrapper).append(exp);
		return $(wrapper);

	}

	var create_clause_inputs = function(field_list){

		var select_list = $("<select class=\"all-field-listing\"></select>");
		field_list = field_list.split(",");
		for(var i = 0; i < field_list.length; i++){

			var option = $("<option>" + field_list[i] + "</option>")
			$(select_list).append(option)

		}
		var input_wrapper = $("<div class=\"clause-input\"></div>");
		var field_name = $("<input class=\"field-name\"></input>");
		var value = $("<input class=\"field-value\"></input>");
		var selector_wrapper = $("<div class=\"dropdowns\"></div>");
		$(selector_wrapper).append(select_list);
		$(input_wrapper).append(field_name);
		$(input_wrapper).append(value);
		$(input_wrapper).append(selector_wrapper);
		return $(input_wrapper);

	}

	var add_clause = function(){

		var node_id = $(this).parents(".clause-group").first().attr("id");
		$.ajax({
            type: "GET",
            url: "new-clause",
            cache: false,
            dataType: "xml",
            data: { "node_id" : node_id },
            success: function(xml) {

            		build_control_tree($(xml), $("#" + node_id));
 
                }
            });

	}

	var add_clause_group = function(){

		var node_id = $(this).parents(".clause-group").first().attr("id");
		$.ajax({
            type: "GET",
            url: "new-clause-group",
            cache: false,
            dataType: "xml",
            data: { "node_id" : node_id },
            success: function(xml) {

            		build_control_tree($(xml), $("#" + node_id));
 
                }
            });

	}	

	var delete_clausular_element = function(){

		var node_to_remove = $(this).parents(".button-set").parent()
		var node_id_to_remove = $(node_to_remove).attr("id");
		var reflow_from_root = $(node_to_remove).parents(".clause-group").length == 0
		var node_id_for_reflow = 0
		if(!reflow_from_root){

			node_id_for_reflow = $(node_to_remove).parents(".clause-group").first().attr("id");

		}
		$.ajax({
            type: "GET",
            url: "delete-cl-element",
            cache: false,
            dataType: "xml",
            data: { "node_to_remove" : node_id_to_remove, "node_to_reflow" : node_id_for_reflow },
            success: function(xml) {

            		var selector = "";
            		if(node_id_for_reflow == 0){

            			selector = "#clause-controllers";
            			$("#clause-controllers").children().remove();

            		}
            		else{

            			selector = "#" + node_id_for_reflow;
            			$(selector).children(".clause").remove();
            			$(selector).children(".clause-group").remove();

            			$(xml).children().each(function(){

            				build_control_tree($(this), $(selector))

            			})

            		}
 
                }
            });		

	}	

	var populate_clause_inputs = function(){

		var new_field = $(this).val();
		$(this).parents(".clause-input").children(".field-name").first().val(new_field);
		var that = $(this)
		$.ajax({
            type: "GET",
            url: "facet-values",
            cache: false,
            dataType: "json",
            data: { "passedfield" : new_field },
            success: function(json) {

            		vals = json["values"];
            		var value_selector = $("<select class=\"facet-selector\"></select>");
            		for(var i = 0; i < vals.length; i++){

            			var option = $("<option value=\"" + vals[i] + "\">" + vals[i] + "</option>");
            			$(value_selector).append(option);
            		}
            		console.log("finished");
            		$(that).parents(".clause-input").children(".dropdowns").first().append(value_selector);

                }
            });

	}

	var populate_clause_value = function(){

		var val = $(this).val();
		$(this).parents(".clause-input").children(".field-value").first().val(val);
	}

	var expand_languages = function(){

		var original_term = $(this).parents(".clause").first().children(".clause-input").first().children("input.field-value").first().val();
		$.ajax({
            type: "GET",
            url: "translate",
            cache: false,
            dataType: "json",
            data: { "term" : original_term },
            success: function(json) {

            		alert("hi");
                }
            });
	}

	init_new_query();
	$(document).on("click", ".add-cl", add_clause);
	$(document).on("click", ".add-cg", add_clause_group);
	$(document).on("click", ".delete", delete_clausular_element);
	$(document).on("change", "select.all-field-listing", populate_clause_inputs);
	$(document).on("change", "select.facet-selector", populate_clause_value);
	$(document).on("click", ".expand", expand_languages)
});