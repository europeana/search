$(document).ready(function(){

	var init_new_query = function(){

        $.ajax({
            type: "GET",
            url: "init",
            cache: false,
            dataType: "xml",
            success: function(xml) {

            		update_query_controls($(xml), $("#clause-controllers"));
 
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
				update_query_controls(new_root, parent_element);

			}

		});

	}

	var build_query_struct = function(xml, parent){
		$("#query-container").children().remove();
		$(xml).children().each(function(){

			var tag = $(this).prop("tagName");
			var is_deprecated = $(this).attr("deprecated");
			if(!clause_is_populated($(this))){  }
			else if(tag == "clause"){
				var clause = serialise_clause_to_query(xml, $(this));
				$(parent).append(clause);

			}
			else if(tag == "query"){

				build_query_struct($(this), parent);

			}
			else if(is_deprecated == "false"){
				var operator = construct_query_operator($(this));
				var negator = construct_query_negator($(this));
				var node_id = "q_" + $(this).attr("node-id");
				var step_parent = $("<span id=\"" + node_id + "\" class=\"stepparent\"></span>");
				build_query_struct($(this), step_parent);
				$(step_parent).prepend($("<span class=\"open-bracket\">(</span>"));
				$(step_parent).append($("<span class=\"close-bracket\">)</span>"));
				if(negator != ""){

					$(step_parent).prepend($("<span class=\"group-negator\">" + negator + "</span>"));
				}
				if(operator != ""){

					$(step_parent).prepend($("<span class=\"group-operator\"> " + operator + " </span>"));

				}
				$(parent).append(step_parent);

			}

		});

	}

	var clause_is_populated = function(xml){

		if($(xml).find("field").length == 0){ return false;  }
		if($(xml).find("value").length == 0){ return false; }
		if($(xml).find("field").first().text().trim() == ""){ return false; }
		if($(xml).find("value").first().text().trim() == ""){ return false; }
		return true;

	}

	var construct_query_operator = function(child){

		op = $(child).attr("operator")
		if($(child).attr("operator-suppressed") == "true"){
			return "";
		}
		if(op == "AND"){
			return "AND";
		}
		if(op == "OR"){
			return "OR";
		}
		return "";

	}

	var construct_query_negator = function(child){
		var neg = $(child).attr("negated");
		var sup = $(child).attr("operator-suppressed");
		if(neg == "true" && sup == "true"){
			return "-";
		}
		else{
			return "";
		}

	}

	var serialise_clause_to_query = function(xml, clause){

		var operator = construct_query_operator(clause);
		var negator = construct_query_negator($(clause));
		var deprecated = $(clause).attr("deprecated") == "true" ? "class=\"deprecated-clause\"" : "";
		var node_id = "q_" + $(clause).attr("node-id");		
		var field = $(clause).find("field").text();
		var value = $(clause).find("value").text();
		if(value != "*"){ value = "\"" + value + "\""; }
		var wrapper = $("<span " + deprecated + " id=\"" + node_id + "\"></span>");
		var qs = " " + operator + " " + negator + field + ":" + value;
		$(wrapper).text(qs)
		return $(wrapper);

	}

	var update_query_controls = function(xml, selector){

		build_control_tree($(xml), selector);
		$.ajax({
        	type: "GET",
        	url: "getfullquery",
        	cache: false,
        	dataType: "xml",
        	success: function(xml) {

        		build_solr_query($(xml));

            }
        });
		
	}

	var build_solr_query = function(xml){

		var bqw = $("<div id=\"big-query-wrapper\"></div>");
		if($(xml).find("field").length == 1 && $(xml).find("field").text() == ""){
			
			bqw.text("*:*");

		}
		else{

			build_query_struct(xml, bqw);

		}
		$("#query-container").text("");
		$("#query-container").children().remove();
		$("#query-container").append(bqw);

	}

	var update_query_text = function(query_text){

		$("#query-container").text(query_text);

	}

	var render_clause_group = function(xml){

		var node_id = $(xml).attr("node-id");
		var is_negated = $(xml).attr("negated");
		var is_deprecated = $(xml).attr("deprecated");
		var operator = $(xml).attr("operator");
		var is_suppressed = $(xml).attr("operator-suppressed");
		var cg_wrapper = $("<div class=\"clause-group\" id=\"" + node_id + "\"></div>");
		var lbl = $("<h3>Clause Group</h3>");
		var neg_control = create_negated_control(is_negated);
		var button_set = create_group_button_set();
		var ops_wrapper = $("<div class=\"ops-wrapper\"></div>");
		if(is_suppressed == "false"){
			var op_control = create_op_control(node_id, operator);
			$(ops_wrapper).append(op_control);
		}
		$(ops_wrapper).append(neg_control);
		$(cg_wrapper).append(lbl);
		$(cg_wrapper).append(ops_wrapper);
		$(cg_wrapper).append(button_set);
		update_query_controls(xml, $(cg_wrapper));
		return $(cg_wrapper);

	}

	var render_clause = function(xml){
		// note that clauses are leaf nodes by definition
		// no need for recursion here
		var node_id = $(xml).attr("node-id");
		var is_negated = $(xml).attr("negated");
		var is_deprecated = $(xml).attr("deprecated");
		var operator = $(xml).attr("operator");
		var is_suppressed = $(xml).attr("operator-suppressed");
		var all_fields = $(xml).find("all-fields").text();
		var neg_control = create_negated_control(is_negated);
		var button_set = create_clause_button_set();
		var inputs = create_clause_inputs(xml, all_fields);
		var cl_wrapper = $("<div class=\"clause\" id=\"" + node_id + "\"><h3>Clause</h3></div>");
		var ops_wrapper = $("<div class=\"ops-wrapper\"></div>");
		if(is_suppressed == "false"){
			var op_control = create_op_control(node_id, operator);		
			$(ops_wrapper).append(op_control);
		}
		$(ops_wrapper).append(neg_control);
		$(cl_wrapper).append(ops_wrapper);
		$(cl_wrapper).append(button_set);
		$(cl_wrapper).append(inputs);
		return $(cl_wrapper);

	}

	var create_op_control = function(node_id, operator){

		var name = "operator-radio-" + node_id;
		var controls = $("<div class=\"operator-radio-set\"></div>");
		var and_control = $("<input type=\"radio\" class=\"operator-radio\" value=\"AND\" name=\"" + name + "\">AND</input>");
		var or_control = $("<input type=\"radio\" class=\"operator-radio\" value=\"OR\" name=\"" + name + "\">OR</input>");
		$(controls).append(and_control);
		$(controls).append(or_control);
		if(operator == "OR"){

			$(or_control).attr("checked", "checked");

		}
		else{

			$(and_control).attr("checked", "checked");

		}
		return controls;

	}

	var create_negated_control = function(is_negated){

		var controls = $("<div class=\"negated-wrapper\">Negated (NOT): </div>");
		var neg = $("<input type=\"checkbox\" class=\"negcheck\" value=\"negated\"></input>");
		$(controls).append(neg)
		if(is_negated == "true"){

			$(neg).attr("checked", "checked");

		}

		return controls;

	}

	var create_group_button_set = function(){

		var wrapper = $("<div class=\"button-set\"><div>");
		var add_cg = $("<div class=\"button-control add-cg\">Add Clause Group</div>");
		var add_cl = $("<div class=\"button-control add-cl\">Add Clause</div>");
		var con = $("<div class=\"button-control convert-to-cl\">Ungroup</div>");
		var dep = $("<div class=\"button-control deprecate\">Deactivate</div>");
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
		var con = $("<div class=\"button-control convert-to-cg\">Group</div>");
		var dep = $("<div class=\"button-control deprecate\">Deactivate</div>");
		var del = $("<div class=\"button-control delete\">Delete</div>");
		var exp = $("<div class=\"button-control expand\">Expand Labels</div>");
		$(wrapper).append(con);
		$(wrapper).append(dep);
		$(wrapper).append(del);
		$(wrapper).append(exp);
		return $(wrapper);

	}

	var create_clause_inputs = function(xml, field_list){

		var field = $(xml).find("field").text();
		var val = $(xml).find("value").text();
		var select_list = $("<select class=\"all-field-listing\"></select>");
		field_list = field_list.split(",");
		for(var i = 0; i < field_list.length; i++){

			var option = $("<option value=\"" + field_list[i] + "\">" + field_list[i] + "</option>")
			$(select_list).append(option)

		}
		$(select_list).val(field);
		var input_wrapper = $("<div class=\"clause-input\"></div>");
		var field_name = $("<input class=\"field-name\" value=\"" + field + "\"></input>");
		var value = $("<input class=\"field-value\" value=\"" + val + "\"></input>");
		var selector_wrapper = $("<div class=\"dropdowns\"></div>");
		$(selector_wrapper).append(select_list);
		$(input_wrapper).append(field_name);
		$(input_wrapper).append(value);
		$(input_wrapper).append(selector_wrapper);
		if(val != ""){

			build_facet_value_selector(field, $(select_list), val);

		}
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

            		update_query_controls($(xml), $("#" + node_id));
 
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

            		update_query_controls($(xml), $("#" + node_id));
 
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

            				update_query_controls($(this), $(selector));

            			})

            		}
 
                }
            });		

	}	

	var populate_clause_inputs = function(){

		var new_field = $(this).val();
		$(this).parents(".clause-input").children(".field-name").first().val(new_field);
		$(this).parents(".clause-input").find("select.facet-selector").remove();
		build_facet_value_selector(new_field, $(this), "");


	}

	var build_facet_value_selector = function(field, form_control, current_value){

		$.ajax({
            type: "GET",
            url: "facet-values",
            cache: false,
            dataType: "json",
            data: { "passedfield" : field },
            success: function(json) {

            		vals = json["values"];
            		var value_selector = $("<select class=\"facet-selector\"></select>");
            		for(var i = 0; i < vals.length; i++){

            			var option = $("<option value=\"" + vals[i] + "\">" + vals[i] + "</option>");
            			$(value_selector).append(option);
            		}
            		$(form_control).parents(".clause-input").children(".dropdowns").first().append(value_selector);

                }
            });
	}

	var populate_clause_value = function(){

		var val = $(this).val();
		$(this).parents(".clause-input").children(".field-value").first().val(val);
	
	}

	var expand_languages = function(){

		var clause_box = $(this).parents(".clause").first();
		var original_term = $(this).parents(".clause").first().children(".clause-input").first().children("input.field-value").first().val();
		$.ajax({
            type: "GET",
            url: "translate",
            cache: false,
            dataType: "json",
            data: { "term" : original_term },
            success: function(json) {

            		render_term_expansions(json, clause_box);

                }
            });
	}

	var render_term_expansions = function(json, clause_box){

		// first we need to order the json contents
		langs = []
		$.each(json, function(k, v){ langs.push(k);});
		langs = langs.sort()
		var exp_wrapper = $("<div class=\"expansions\"></div>");
		for(var i = 0; i < langs.length; i++){

			lang_code = langs[i];
			lang_trans = json[lang_code];
			var trans_wrapper = $("<div class\"trans-wrapper\"></div>");
			var check = $("<input type=\"checkbox\"></input>");
			var info_wrapper = $("<span class=\"trans-label-wrapper\"></span>");
			var lang_code_display = $("<span class=\"lang-code\">" + lang_code + "</span>");
			var lang_val_display = $("<span class=\"lang-val\">" + lang_trans + "</span>");
			$(info_wrapper).append(lang_code_display);
			$(info_wrapper).append(lang_val_display);
			$(trans_wrapper).append(check);
			$(trans_wrapper).append(info_wrapper);
			$(exp_wrapper).append(trans_wrapper);

		}

		var dismiss_button = $("<div class=\"button-control finished-expanding\">Done</div>")
		$(exp_wrapper).append(dismiss_button);
		$(clause_box).append(exp_wrapper);

	}

	var dismiss_expansions = function(){

		var translations = [];
		var that = this;
		$(this).parents(".expansions").first().find("input:checked").next(".trans-label-wrapper").find(".lang-val").each(function(){

			var trans = $(this).text();
			translations.push(trans);

		});

		var field = $(this).parents(".clause").first().find(".field-name").val();
		translations.push($(this).parents(".clause").first().find(".field-value").val());
		var parent_id = $(this).parents("div.clause-group").first().attr("id");
		add_expansion_clauses(parent_id, field, translations);
		var this_id = $(this).parents(".clause").first().attr("id");
		var delenda = $(this).parents(".expansions").first().prevAll(".button-set").first().find(".delete").first();
		delete_clausular_element.apply(delenda);

	}

	var add_expansion_clauses = function(parent_id, field_name, translations){

		$.ajax({
            type: "GET",
            url: "new-expansion-group",
            cache: false,
            dataType: "xml",
            data: { "node_id" : parent_id, "fieldname" : field_name, "translations" : translations.join(",")  },
            success: function(xml) {

            		update_query_controls($(xml), $("#" + parent_id));

            }
        });
	}

	var update_clause = function(){

		var common_parent = $(this).parents(".clause").first();
		var node_id = $(common_parent).attr("id");
		var node_id_selector = "#" + node_id;
		var field = $(common_parent).find(".field-name").first().val().trim();
		var value = $(common_parent).find(".field-value").first().val().trim();
		if(field != "" && value != ""){

		$.ajax({
            type: "GET",
            url: "updatevalues",
            cache: false,
            dataType: "xml",
            data: { "node_id" : node_id, "field_name" : field, "field_value" : value },
            success: function(xml) {

            		build_solr_query(xml);

                }
            });	

		}

	}

	var view_results = function(){

		qry = serialise_query($("#big-query-wrapper"), false);
		var results_page = "http://www.europeana.eu/portal/en/search?q=" + qry;
		window.open(results_page, "_blank");

	}

	var serialise_query = function(root_qry, deprecation_flag){
		qry_str = "";
		$(root_qry).children().each(function(){

			var is_deprecated = $(this).hasClass("deprecated-clause");
			if(is_deprecated){ deprecation_flag = true; }
			else{

				if($(this).children().length == 0){

					var raw_text = $(this).text();
					qry_str += raw_text;
					if(deprecation_flag){

						qry_str = qry_str.replace(/AND /, "");
						qry_str = qry_str.replace(/OR /, "");
						deprecation_flag = false;	

					}


				}
				else{

					qry_str += serialise_query($(this), deprecation_flag);

				}

			}

		});

		return qry_str;

	}

	var update_operator = function(node_id){

		opval = $(this).val();
		$.ajax({
            type: "GET",
            url: "update-operator",
            cache: false,
            dataType: "xml",
            data: { "operator" : opval, "node_id" : node_id },
            success: function(xml) {
            		if($(xml).text() == "Inconsistent Operators"){
            			display_inconsistent_operator_warning(opval, node_id);
            		}
            		else{
            			build_solr_query(xml);
            		}

                }
            });

	}

	var display_inconsistent_operator_warning = function(operator, node_id){

		$("#inconsistent-operator-warning").css({ "visibility" : "visible"});
		$("#new-operator").text(operator);
		// info for if we want to revert the operator later
		var operator_control_selector = "operator-radio-" + node_id;
		var reverted_operator = operator == "AND" ? "OR" : "AND";
		$("#previous-operator").text(reverted_operator);
		$("#previous-node").text(node_id);

	}

	var update_operator_indirectly = function(){

		var node_id = get_parent_node_id($(this));
		update_operator.apply(this, [node_id]);

	}

	var get_parent_node_id = function(el){

		var has_clause_parent = ($(el).parents(".clause").length > 0);
		if(has_clause_parent){

			return $(el).parents(".clause").first().attr("id");

		}
		else{

			return $(el).parents(".clause-group").first().attr("id");

		}

	}

	var update_negated_status = function(node_id){

		negval = $(this).prop("checked") ? "negated" : "affirmed";
		$.ajax({
            type: "GET",
            url: "update-negated-status",
            cache: false,
            dataType: "xml",
            data: { "negstatus" : negval, "node_id" : node_id },
            success: function(xml) {

            		build_solr_query(xml);

                }
            });

	}

	var deprecate_clausular_element = function(){

		var node_id = get_parent_node_id($(this));
		var operation = $(this).text() == "Deactivate" ? "deprecate" : "undeprecate";
		if(operation == "deprecate"){

			$(this).text("Activate");

		}
		else{

			$(this).text("Deactivate");

		}
		$.ajax({
            type: "GET",
            url: "deprecate",
            cache: false,
            dataType: "xml",
            data: { "depstatus" : operation, "node_id" : node_id },
            success: function(xml) {

            		build_solr_query(xml);

                }
            });

	}

	var update_negated_status_indirectly = function(){

		var node_id = get_parent_node_id($(this));
		update_negated_status.apply(this, [node_id]);

	}

	var toggle_save_box = function(){

		var save_box = $("#to-save");
		var is_visible = $(save_box).css("visibility") != "hidden";
		if(is_visible){

			$(save_box).css({ "visibility" : "hidden"});

		}
		else{

			$(save_box).css({ "visibility" : "visible"});

		}

	}

	var cancel_io_warning = function(){

		$("#inconsistent-operator-warning").css({ "visibility" : "hidden"});
		revert_to_previous_operator();

	}

	var revert_to_previous_operator = function(){

		var previous_operator = $("#previous-operator").text();
		var previous_node = $("#previous-node").text();
		var operator_selector = "operator-radio-" + previous_node;
		$("input[name=\"" + operator_selector + "\"][value=\"" + previous_operator + "\"]").click();

	}

	var convert_to_clause_group = function(){
		// flow is tricky here. this is the clause being converted ...
		var node_id = get_parent_node_id($(this));
		// and this is that clause's parent ...
		var parent_node_id = get_parent_node_id($("#" + node_id));
		$.ajax({
            type: "GET",
            url: "convert-to-cg",
            cache: false,
            dataType: "xml",
            data: { "node_id" : node_id },
            success: function(xml) {
            		// the xml being returned is of the element parent
            		// (that is to say, the parent of the newly-created clause group)
            		// so we need to reflow from the element one level above
            		// *that* - so to speak the grandparent
            		reflow_from_parent(xml, parent_node_id)

                }
            });

	}

	var reflow_from_parent = function(xml, parent_id){

		var grandparent_id = get_parent_node_id($("#" + parent_id));
		$("#" + parent_id).remove();
		if(!grandparent_id){

			update_query_controls(xml, "#clause-controllers");

		}
		else{

			build_control_tree(xml, $("#" + grandparent_id));

		}

	}

	var convert_to_clause = function(){

		var node_id = get_parent_node_id($(this));
		var parent_node_id = get_parent_node_id($("#" + node_id));
		$.ajax({
	        type: "GET",
	        url: "convert-to-cl",
	        cache: false,
	        dataType: "xml",
	        data: { "node_id" : node_id },
	        success: function(xml) {

            		if($(xml).text() == "Inconsistent Operators"){

            			display_ungroup_warning(opval, node_id);

            		}
            		else{
	        			
	        			reflow_from_parent(xml, parent_node_id);
	        		}

	            }
	        });

	}

	var display_ungroup_warning = function(){

		$("#ungrouping-inconsistency-warning").css({"visibility" : "visible"});


	}

	var dismiss_ungrouping_warning = function(){

		$("#ungrouping-inconsistency-warning").css({ "visibility" : "hidden"});

	}

	var solve_inconsistency_by_conversion = function(){
		
		var rel_node = $("#previous-node").text();
		$("#" + rel_node).find(".convert-to-cg").click();
		cancel_io_warning();

	}

	var change_all_operators = function(){

		//TODO: Implement this
		cancel_io_warning();

	}

	init_new_query();
	$(document).on("click", ".add-cl", add_clause);
	$(document).on("click", ".add-cg", add_clause_group);
	$(document).on("click", ".delete", delete_clausular_element);
	$(document).on("click", ".deprecate", deprecate_clausular_element);
	$(document).on("change", "select.all-field-listing", populate_clause_inputs);
	$(document).on("change", "select.all-field-listing", update_clause)
	$(document).on("change", "select.facet-selector", populate_clause_value);
	$(document).on("change", "select.facet-selector", update_clause);
	$(document).on("click", ".expand", expand_languages);
	$(document).on("click", ".finished-expanding", dismiss_expansions);
	$(document).on("change", ".field-value", update_clause);
	$(document).on("change", ".operator-radio", update_operator_indirectly);
	$(document).on("change", ".negcheck", update_negated_status_indirectly);
	$(document).on("click", ".convert-to-cg", convert_to_clause_group);
	$(document).on("click", ".convert-to-cl", convert_to_clause);
	$(document).on("click", "#iow-convert-to-group", solve_inconsistency_by_conversion)
	$("#iow-cancel").click(cancel_io_warning);
	$("#iow-change-all").click(change_all_operators);
	$("#view-results").click(view_results);
	$("#save-to-file").click(toggle_save_box);
	$("#ungrouping-iow-cancel").click(dismiss_ungrouping_warning);
});