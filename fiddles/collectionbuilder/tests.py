from django.test import SimpleTestCase
from collectionbuilder.xmlutil import XMLQueryEditor
from collectionbuilder.xmlutil.InconsistentOperatorException import InconsistentOperatorException
from collectionbuilder.xmlutil.ZeroResultsException import ZeroResultsException
import xml.etree.ElementTree as ET
from datetime import datetime

class XMLQueryEditorTestCase(SimpleTestCase):

	namespaces = { 'xml', 'http://www.w3.org/XML/1998/namespace'} 
	def test_xml_loaded(self):
		# XML is correctly loaded and parsed
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		root_node_name = xqe.get_tree().getroot().tag
		self.assertEquals(root_node_name, 'query')

	def test_generate_id(self):
		# to ensure uniqueness, node ids are generated
		# from timestamps
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		test_time = datetime(2017, 8, 28, 10, 00, 00, 000) 
		expected = "c02dd831a0333ce9e8b2c7259cd0d3f6"
		actual = xqe.convert_timestamp_to_identifier(test_time)
		self.assertEquals(expected, actual)

	def test_retrieve_clause_by_id(self):
		# given the id of a clause, we retrieve it correctly
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		test_node = xqe.retrieve_node_by_id("1")
		op_suppressed = test_node.attrib["operator-suppressed"]
		field = test_node.find("field").text 
		value = test_node.find("value").text
		self.assertEquals(op_suppressed, "true")
		self.assertEquals(field, "title")
		self.assertEquals(value, "test title")

	def test_retrieve_clause_group_by_id(self):
		# given the id of a clause group, we retrieve it correctly
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		test_node = xqe.retrieve_node_by_id("2")
		op = test_node.attrib["operator"]
		clause_count = len(test_node.find("clause"))
		self.assertEquals(op, "AND")
		self.assertEquals(clause_count, 2)		

	def test_remove_clause_by_id(self):
		# the specified clause is removed from the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		xqe.remove_node_by_id("1")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		self.assertEquals(prev_number_of_clauses, new_number_of_clauses + 1)
		self.assertIsNone(xqe.retrieve_node_by_id("1"))

	def test_remove_clause_group_by_id(self):
		# the specified clause group is removed from the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		xqe.remove_node_by_id("5")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		self.assertEquals(prev_number_of_clauses, new_number_of_clauses + 1)
		self.assertIsNone(xqe.retrieve_node_by_id("5"))

	def test_generate_clause(self):
		# given an operator, a field, and a value, the correct
		# XML clause is generated
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		self.assertEquals(clause.attrib["operator"], "OR")
		self.assertEquals(clause.attrib["xml:lang"], "de")
		self.assertEquals(clause.attrib["deprecated"], "false")
		self.assertEquals(clause.attrib["negated"], "false")
		self.assertEquals(clause.find("field").text, "subject")
		self.assertEquals(clause.find("value").text, "Quellenforschung")

	def test_generate_clause_group(self):
		# given the material for two clauses and an operator,
		# appropriately generates a new clause group
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		clause_group = xqe.generate_clause_group()
		self.assertEquals(clause_group.attrib["operator"], "AND")
		self.assertEquals(clause_group.attrib["deprecated"], "false")
		self.assertEquals(clause_group.attrib["negated"], "false")

	def test_add_clause_at_root(self):
		# a given clause is added to the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clausular_element=clause)
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		self.assertEquals(prev_number_of_clauses + 1, new_number_of_clauses)
		last_child = xqe.get_tree().getroot().findall(".//clause")[-1]
		self.assertEquals(last_child.find("value").text, "Quellenforschung")

	def test_add_clause(self):
		# a given clause is added to the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clausular_element=clause, to_el_id="2")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		self.assertEquals(prev_number_of_clauses + 1, new_number_of_clauses)
		last_root_child = xqe.get_tree().getroot().findall("./clause-group/clause")[-1]
		self.assertNotEquals(last_root_child.find("value").text, "Quellenforschung")
		augmented_clause_group = xqe.retrieve_node_by_id("2")
		last_child = augmented_clause_group.findall("clause")[-1]
		self.assertEquals(last_child.find("value").text, "Quellenforschung")

	def test_add_clause_group(self):
		# a given clause group is added to the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		clause_group = xqe.generate_clause_group(operator="AND")
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		xqe.add_clausular_element(clausular_element=clause_group, to_el_id="5")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		added_group_children = len(xqe.retrieve_node_by_id("5").findall("clause-group")[-1].findall(".//*"))
		self.assertEquals(prev_number_of_clauses + 1, new_number_of_clauses)
		self.assertEquals(added_group_children, 0)

	def test_change_clause_field(self):
		# changing the field of a clause
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		node_to_change = xqe.retrieve_node_by_id("1")
		prev_field = node_to_change.find("field").text
		xqe.set_field("proxy_dc_subject", "1")
		changed_node = xqe.retrieve_node_by_id("1")
		now_field = changed_node.find("field").text
		self.assertNotEquals(prev_field, now_field)

	def test_change_clause_value(self):
		# changing the value associated with a field in a clause
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		node_to_change = xqe.retrieve_node_by_id("1")
		prev_field = node_to_change.find("value").text
		xqe.set_value("new testing title", "1")
		changed_node = xqe.retrieve_node_by_id("1")
		now_field = changed_node.find("value").text
		self.assertNotEquals(prev_field, now_field)

	def test_deprecate_clause(self):
		# the deprecation flag is correctly set and unset on clauses
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("1")
		el_is_deprecated = xqe.retrieve_node_by_id("1").attrib["deprecated"]
		self.assertEquals(el_is_deprecated, "true")		

	def test_undeprecate_clause(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.undeprecate_by_id("6")
		el_is_deprecated = xqe.retrieve_node_by_id("6").attrib["deprecated"]
		self.assertEquals(el_is_deprecated, "false")

	def test_negate_clause(self):
		# the negation (NOT) flag is correctly set and unset on clauses
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.negate_by_id("1")
		el_is_negated = xqe.retrieve_node_by_id("1").attrib["negated"]
		self.assertEquals(el_is_negated, "true")	

	def test_unnegate_clause(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.unnegate_by_id("3")
		el_is_negated = xqe.retrieve_node_by_id("3").attrib["negated"]
		self.assertEquals(el_is_negated, "false")	

	def test_subsequent_nodes_inherit_not(self):
		# any clause added to a group with a "not" clause
		# already defined also has its flag set to "not"
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		self.assertEquals(clause.attrib["negated"], "true")

	# we need to ensure that the boolean operators (AND|OR) are 
	# correctly handled when nodes are removed or added

	def test_first_node_operator_is_suppressed(self):
		# the first node in a group of siblings has its operator suppressed
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.remove_node_by_id("3")
		xqe.remove_node_by_id("4")
		xqe.remove_node_by_id("5")
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		self.assertEquals(clause.attrib["operator-suppressed"], "true")		

	def test_subsequent_nodes_inherit_and(self):
		# any clause added to a group with an "AND" clause
		# already defined also has the "AND" operator
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		clause = xqe.generate_clause(field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "5")
		self.assertEquals(clause.attrib["operator"], "AND")

	def test_subsequent_nodes_inherit_or(self):
		# any clause added to a group containing an "OR" clause
		# also has the "OR" operator
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		clause = xqe.generate_clause(field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		self.assertEquals(clause.attrib["operator"], "OR")

	def test_remove_first_clause_changes_operator_on_second(self):
		# when the second node becomes the first, its operator 
		# should be suppressed
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		unaltered_node = xqe.retrieve_node_by_id("2")
		self.assertEquals(unaltered_node.attrib["operator-suppressed"], "false")
		xqe.remove_node_by_id("1")
		new_first_node = xqe.retrieve_node_by_id("2")
		self.assertEquals(new_first_node.attrib["operator-suppressed"], "true")

	def test_remove_first_clause_has_no_operator_effect_on_third(self):
		# need to ensure that this effect does not spread too far
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.remove_node_by_id("3")
		new_first_node = xqe.retrieve_node_by_id("5")
		self.assertEquals(new_first_node.attrib["operator"], "OR")

	def test_serialisation_to_query(self):
		# the XML needs to be converted appropriately to query form
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		serialised_query = xqe.serialise_to_solr_query()
		expected = "title:\"test title\" AND (-proxy_dc_subject:\"test\" OR proxy_dc_subject:\"l'examen\" OR (CREATOR:\"Leonardo da Vinci\"))"
		self.assertEquals(serialised_query, expected)

	# operators appearing first in either the query or in individual clauses
	# break the query. Deprecating earlier clauses accordingly means these
	# clauses have to be suppressed.
	def test_deprecating_first_clause_at_top_level_removes_subsequent_operator(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("1")
		self.assertEquals(xqe.retrieve_node_by_id("2").attrib["operator-suppressed"], "true")

	def test_deprecating_first_clause_in_group_removes_subsequent_operator(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("3")
		self.assertEquals(xqe.retrieve_node_by_id("4").attrib["operator-suppressed"], "true")

	# undeprecation needs to reverse these changes
	def test_undoing_operator_suppression_at_top_level(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("1")	
		self.assertEquals(xqe.retrieve_node_by_id("2").attrib["operator-suppressed"], "true")
		xqe.undeprecate_by_id("1")
		self.assertEquals(xqe.retrieve_node_by_id("2").attrib["operator-suppressed"], "false")

	def test_undoing_operator_suppression_at_group_level(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("3")
		self.assertEquals(xqe.retrieve_node_by_id("4").attrib["operator-suppressed"], "true")
		xqe.undeprecate_by_id("3")		
		self.assertEquals(xqe.retrieve_node_by_id("4").attrib["operator-suppressed"], "false")

	# operator deprecation also needs to apply to clause groups in cases
	# where the clause-group itself is not deprecated, but all
	# of its children are

	def test_no_operator_for_clause_group_when_all_clauses_deprecated(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("6")
		xqe.deprecate_by_id("7")
		self.assertEquals(xqe.retrieve_node_by_id("5").attrib["operator-suppressed"], "true")

	# and we need to make sure that re-activating one of the clauses restores the 
	# clause-group operator

	def test_reactivating_clause_reactivates_parent_group(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.deprecate_by_id("6")
		xqe.deprecate_by_id("7")
		self.assertEquals(xqe.retrieve_node_by_id("5").attrib["operator-suppressed"], "true")
		xqe.undeprecate_by_id("6")
		self.assertEquals(xqe.retrieve_node_by_id("5").attrib["operator-suppressed"], "false")

	# changing the operator on just one clause unit when others
	# have a different operator should flag a warning

	def test_inconsistent_operator_warning(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		self.assertRaises(InconsistentOperatorException, xqe.set_operator("4", "AND"))
		xqe.set_operator("4", "OR")
		self.assertEquals(xqe.retrieve_node_by_id("4").attrib["operator"], "OR")

	def test_convert_to_clause_group(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		start_node = xqe.retrieve_node_by_id("4")
		start_op = start_node.attrib["operator"]
		start_neg = start_node.attrib["negated"]
		start_lang = start_node.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
		xqe.convert_to_clause_group("4")
		# we now test that the clause has a new position ...
		found_node = xqe._tree.getroot().find("./clause-group/clause-group/clause-group/clause[@node-id=\"4\"]")
		self.assertIsNotNone(found_node)
		# ... but is otherwise unchanged
		end_op = found_node.attrib["operator"]
		end_neg = found_node.attrib["negated"]
		# TODO: why do I need to namespace here, but not in earlier tests?
		end_lang = found_node.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
		self.assertEquals(start_op, end_op)
		self.assertEquals(start_neg, end_neg)
		self.assertEquals(start_lang, end_lang)

	def test_clause_group_conversion_leaves_tree_position_unchanged(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		start_node = xqe.retrieve_node_by_id("4")
		xqe.convert_to_clause_group("4")
		new_group_node = xqe._tree.getroot().find("./clause-group/clause-group/clause-group[1]/clause[@node-id=\"4\"]")
		self.assertIsNotNone(new_group_node)

	def test_convert_to_clause(self):
		# elements should be in the same positions and with the same contents
		# as they had prior to the clause-group being removed
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.ungroup_clause_group("2")
		first_freed_clause = xqe.get_tree().getroot().find("./clause-group/clause[2]")
		second_freed_clause = xqe.get_tree().find("./clause-group/clause[3]")
		self.assertEquals(first_freed_clause.get("node-id"), "3")
		self.assertEquals(second_freed_clause.get("node-id"), "4")

	def test_clause_conversion_triggers_inconsistency_error_as_needed(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		self.assertRaises(InconsistentOperatorException, xqe.ungroup_clause_group, "5")

	def test_force_operator_conversion_raises_error_if_no_results(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		self.assertRaises(ZeroResultsException, xqe.set_all_operators, "OR", "5")

	def test_force_operator_conversion_raises_no_error_if_results(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.set_operator("OR", "2")
		xqe.set_all_operators("OR", "5")
		self.assertEquals(xqe.retrieve_node_by_id("3").get("operator"), "OR")
		self.assertEquals(xqe.retrieve_node_by_id("4").get("operator"), "OR")
		self.assertEquals(xqe.retrieve_node_by_id("5").get("operator"), "OR")

	def test_facet_query_excludes_on_OR(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		facet_query = xqe.get_facet_query_for_clause("4")
		self.assertEquals(facet_query, "title:\"test title\"")

	def test_facet_query_does_not_exclude_on_AND(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		facet_query = xqe.get_facet_query_for_clause("1")
		self.assertEquals("(-proxy_dc_subject:\"test\" OR proxy_dc_subject:\"l'examen\" OR (CREATOR:\"Leonardo da Vinci\"))", facet_query)		

	def test_zero_results_from_operator_raises_exception(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.remove_node_by_id("5")
		xqe.set_field("TYPE", "3")
		xqe.set_field("TYPE", "4")
		xqe.set_value("IMAGE", "3")
		xqe.set_value("TEXT", "4")
		xqe.unnegate_by_id("3")
		self.assertRaises(ZeroResultsException, xqe.set_operator, "AND", "4")

	def test_gt_zero_results_from_operator_no_exception(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.remove_node_by_id("5")
		xqe.set_field("TYPE", "3")
		xqe.set_field("TYPE", "4")
		xqe.set_value("IMAGE", "3")
		xqe.set_value("TEXT", "4")
		xqe.set_operator("OR", "4")

	def test_saves_with_fidelity(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		xqe.remove_node_by_id("5")
		test_tree = ET.tostring(xqe.get_tree().getroot(), encoding="utf8", method="text")
		new_name = "test2"
		xqe.save_query_file(new_name)
		xqe2 = XMLQueryEditor.XMLQueryEditor(new_name)
		comparison_tree = ET.tostring(xqe2.get_tree().getroot(), encoding="utf8", method="text")
		self.assertEquals(test_tree, comparison_tree)

	def test_reading_directory(self):
		xqe = XMLQueryEditor.XMLQueryEditor("test")
		query_list = xqe.read_query_directory()
		self.assertGreater(len(query_list), 1)
		self.assertIn("test", query_list)

	
