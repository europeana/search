$(document).ready(function(){

    var display_relations = function(el, data){

        level_indent = 25;
        var sublevel_indent = parseInt($(el).children("td").first().next("td").css("padding-left").replace("px", "")) + level_indent;
        var arr_prev_classes = $(el).attr("class").split(" ");
        prev_classes = "";
        $.each(arr_prev_classes, function(i, v){
            if(v.match(/Q[0-9]+/) && prev_classes.indexOf(v) == -1) prev_classes += v + " ";
        });
        prev_classes = prev_classes.replace("toplevel", "").replace("sublevel", "");
        $.each(data, function(){
            act_url = this[0]
            act_label = this[1];
            rel_label = get_friendly_rel_label(this[2]);
            pas_label = this[3];
            pas_url = this[4];
            image_url = this[5];
            subsclass = "subagent-label"
            if(image_url == "None"){

                subsclass += " unknown-image"

            }
            if(image_url == "None"){

                image_url = "/static/remfriends/images/unknown.jpg"

            }
            act_id = act_url.split("/").splice(-1)[0];
            pas_id = pas_url.split("/").splice(-1)[0];
            pas_url = "Agent/" + pas_id;
            info = $("<tr class=\"sublevel " + prev_classes + act_id + "\"><td class=\"" + subsclass + "\"></td><td class=\"" + act_id + "\" style=\"padding-left:" + sublevel_indent + "px;\"><img height=\"60px\" width=\"60px\" src=\"" + image_url + "\"/><div class=\"subagent-label\" style=\"text-align:right;\">...</div></td><td>" + rel_label + "</td><td class=\"" + pas_id + "\">" + pas_label + "</td><td></td></tr>");
            $(info).insertAfter(el);

        });
        assign_rel_state(el);
    }

    var get_friendly_rel_label = function(unfriendly_label){

        var enemy2friend = {

            "employer" : "employed by",
            "child" : "has child",
            "father" : "father is",
            "mother" : "mother is",
            "spouse" : "married to",
            "student" : "has as student",
            "sister" : "sister is",
            "brother" : "brother is",
            "relative" : "relative of",
            "partner" : "partner of"

        }

        if(unfriendly_label in enemy2friend){ return enemy2friend[unfriendly_label]; }
        else{ return unfriendly_label; }

    }

    var assign_rel_state = function(el){

        var top = $(el).hasClass("toplevel") ? el : $(el).prevAll(".toplevel").first();
        now_open = [];
        $(top).nextUntil("tr.toplevel", "tr.sublevel").each(function(){
           now_open.push($(this).children("td").first().next("td").attr("class"));
        });
        $(top).nextUntil("tr.toplevel", "tr.sublevel").each(function(){

            var vis_rel = $(this).children("td").last();
            $(vis_rel).removeClass("no-relations");
            if($(this).children("td.hide-relations").length == 0){

                var patient = $(this).children("td")[3];
                var vis_rel = $(this).children("td").last();
                var patient_id = $(patient).attr("class");
                var patient_name = $(patient).text();
                var lnk = "Agent/" + patient_id;
                var a = $("<a href=\"" + lnk + "\" target=\"_blank\">" + patient_name + "</a>");
                $(patient).html(a);
                if(now_open.indexOf(patient_id) == -1){

                    $(vis_rel).addClass("show-relations");
                    $(vis_rel).html("Show " + patient_name + " Relations");

                }
                else{

                    $(vis_rel).addClass("no-relations");
                    $(vis_rel).html("<span class=\"ibid\">" + patient_name +" relations already expanded.</span>");
                }
            }
        });

    }

    var hide_relations = function(){

        var rel_cell = $(this).parent("tr").hasClass("toplevel") ? 1 : 3;
        var arr_classes = $($(this).parent("tr").children("td")[rel_cell]).attr("class").split(" ");
        patient_id = "";
        $.each(arr_classes, function(i, v){

            if(v.match(/Q[0-9]+/)) patient_id += v + " ";

        });
        var patient_id = patient_id.trim();
        $(this).parent("tr").nextAll("tr." + patient_id).remove();
        $(this).removeClass("hide-relations");
        $(this).addClass("show-relations");
        ($(this).text($(this).text().replace("Hide", "Show")));
        assign_rel_state($(this).parent("tr"));

    }

    var retrieve_relations = function(){

        var agid = $(this).parent("tr").find("td a").last().attr("href").split("/").slice(-1)[0];
        var that = $(this).parent("tr");
        $(this).removeClass("show-relations");
        $(this).addClass("hide-relations");
        ($(this).text($(this).text().replace("Show", "Hide")));
        $.ajax({url:'Network/' + agid, dataType:"json"}).done(function(data){ display_relations(that,data)  });

    }

    var launch_reorder = function(){


        $("#submit-roles").click()

    }



    $("table").on("click", "td.show-relations", retrieve_relations);
    $("table").on("click", "td.hide-relations", hide_relations);
    $("#id_order_select").change(launch_reorder);



});