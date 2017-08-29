from django.test import SimpleTestCase
from collectionbuilder.xmlutil import XMLQueryEditor
import xml.etree.ElementTree as ET
from datetime import datetime

class XMLQueryEditorTestCase(SimpleTestCase):


	def test_xml_loaded(self):
		# XML is correctly loaded and parsed
		xqe = XMLQueryEditor.XMLQueryEditor()
		root_node_name = xqe.get_tree().getroot().tag
		self.assertEquals(root_node_name, 'query')

	def test_generate_id(self):
		# to ensure uniqueness, node ids are generated
		# from timestamps
		xqe = XMLQueryEditor.XMLQueryEditor()
		test_time = datetime(2017, 8, 28, 10, 00, 00, 000) 
		expected = "c02dd831a0333ce9e8b2c7259cd0d3f6"
		actual = xqe.convert_timestamp_to_identifier(test_time)
		self.assertEquals(expected, actual)

	def test_retrieve_clause_by_id(self):
		# given the id of a clause, we retrieve it correctly
		xqe = XMLQueryEditor.XMLQueryEditor()
		test_node = xqe.retrieve_node_by_id("1")
		op = test_node.attrib["operator"]
		field = test_node.find("field").text 
		value = test_node.find("value").text
		self.assertEquals(op, "FIRST")
		self.assertEquals(field, "title")
		self.assertEquals(value, "test title")

	def test_retrieve_clause_group_by_id(self):
		# given the id of a clause group, we retrieve it correctly
		xqe = XMLQueryEditor.XMLQueryEditor()
		test_node = xqe.retrieve_node_by_id("2")
		op = test_node.attrib["operator"]
		clause_count = len(test_node.find("clause"))
		self.assertEquals(op, "AND")
		self.assertEquals(clause_count, 2)		

	def test_remove_clause_by_id(self):
		# the specified clause is removed from the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor()
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		xqe.remove_node_by_id("1")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		self.assertEquals(prev_number_of_clauses, new_number_of_clauses + 1)
		self.assertIsNone(xqe.retrieve_node_by_id("1"))

	def test_remove_clause_group_by_id(self):
		# the specified clause group is removed from the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor()
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		xqe.remove_node_by_id("5")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		self.assertEquals(prev_number_of_clauses, new_number_of_clauses + 1)
		self.assertIsNone(xqe.retrieve_node_by_id("5"))

	def test_generate_clause(self):
		# given an operator, a field, and a value, the correct
		# XML clause is generated
		xqe = XMLQueryEditor.XMLQueryEditor()
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
		xqe = XMLQueryEditor.XMLQueryEditor()
		clause_group = xqe.generate_clause_group(operator="FIRST")
		self.assertEquals(clause_group.attrib["operator"], "FIRST")
		self.assertEquals(clause_group.attrib["deprecated"], "false")
		self.assertEquals(clause_group.attrib["negated"], "false")

	def test_add_clause_at_root(self):
		# a given clause is added to the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor()
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clausular_element=clause)
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		self.assertEquals(prev_number_of_clauses + 1, new_number_of_clauses)
		last_child = xqe.get_tree().getroot().findall(".//clause")[-1]
		self.assertEquals(last_child.find("value").text, "Quellenforschung")

	def test_add_clause(self):
		# a given clause is added to the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor()
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clausular_element=clause, to_el_id="2")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause"))
		self.assertEquals(prev_number_of_clauses + 1, new_number_of_clauses)
		last_root_child = xqe.get_tree().getroot().findall("clause")[-1]
		self.assertNotEquals(last_root_child.find("value").text, "Quellenforschung")
		augmented_clause_group = xqe.retrieve_node_by_id("2")
		last_child = augmented_clause_group.findall("clause")[-1]
		self.assertEquals(last_child.find("value").text, "Quellenforschung")

	def test_add_clause_group(self):
		# a given clause group is added to the XML tree
		xqe = XMLQueryEditor.XMLQueryEditor()
		clause_group = xqe.generate_clause_group(operator="AND")
		prev_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		xqe.add_clausular_element(clausular_element=clause_group, to_el_id="5")
		new_number_of_clauses = len(xqe.get_tree().getroot().findall(".//clause-group"))
		added_group_children = len(xqe.retrieve_node_by_id("5").findall("clause-group")[-1].findall(".//*"))
		self.assertEquals(prev_number_of_clauses + 1, new_number_of_clauses)
		self.assertEquals(added_group_children, 0)

	def test_change_clause_field(self):
		# changing the field of a clause
		xqe = XMLQueryEditor.XMLQueryEditor()
		node_to_change = xqe.retrieve_node_by_id("1")
		prev_field = node_to_change.find("field").text
		xqe.set_field("proxy_dc_subject", "1")
		changed_node = xqe.retrieve_node_by_id("1")
		now_field = changed_node.find("field").text
		self.assertNotEquals(prev_field, now_field)

	def test_change_clause_value(self):
		# changing the value associated with a field in a clause
		xqe = XMLQueryEditor.XMLQueryEditor()
		node_to_change = xqe.retrieve_node_by_id("1")
		prev_field = node_to_change.find("value").text
		xqe.set_value("new testing title", "1")
		changed_node = xqe.retrieve_node_by_id("1")
		now_field = changed_node.find("value").text
		self.assertNotEquals(prev_field, now_field)

	def test_deprecate_clause(self):
		# the deprecation flag is correctly set and unset on clauses
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.deprecate_by_id("1")
		el_is_deprecated = xqe.retrieve_node_by_id("1").attrib["deprecated"]
		self.assertEquals(el_is_deprecated, "true")		

	def test_undeprecate_clause(self):
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.undeprecate_by_id("6")
		el_is_deprecated = xqe.retrieve_node_by_id("6").attrib["deprecated"]
		self.assertEquals(el_is_deprecated, "false")

	def test_negate_clause(self):
		# the negation (NOT) flag is correctly set and unset on clauses
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.negate_by_id("1")
		el_is_negated = xqe.retrieve_node_by_id("1").attrib["negated"]
		self.assertEquals(el_is_negated, "true")	

	def test_unnegate_clause(self):
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.unnegate_by_id("3")
		el_is_negated = xqe.retrieve_node_by_id("3").attrib["negated"]
		self.assertEquals(el_is_negated, "false")	

	def test_subsequent_nodes_inherit_not(self):
		# any clause added to a group with a "not" clause
		# already defined also has its flag set to "not"
		xqe = XMLQueryEditor.XMLQueryEditor()
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		self.assertEquals(clause.attrib["negated"], "true")

	# we need to ensure that the boolean operators (AND|OR) are 
	# correctly handled when nodes are removed or added

	def test_first_node_operator_is_first(self):
		# the first node in a group of siblings is
		# without an operator and is labelled "FIRST"
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.remove_node_by_id("3")
		xqe.remove_node_by_id("4")
		xqe.remove_node_by_id("5")
		clause = xqe.generate_clause(operator="OR", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		self.assertEquals(clause.attrib["operator"], "FIRST")		

	def test_second_node_with_operator_unassigned_when_added(self):
		# any node added immediately after the first nodes
		# should be explicitly flagged as needing an operator
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.remove_node_by_id("4")
		xqe.remove_node_by_id("5")
		clause = xqe.generate_clause(operator="UNASSIGNED", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		# while we're at it, let's make sure this is being added to the
		# right point in the tree
		parent = xqe.retrieve_node_by_id("2")
		pos = xqe.get_position(parent, clause)
		self.assertEquals(pos, 2)
		self.assertEquals(clause.attrib["operator"], "UNASSIGNED")

	def test_subsequent_nodes_inherit_and(self):
		# any clause added to a group with an "AND" clause
		# already defined also has the "AND" operator
		xqe = XMLQueryEditor.XMLQueryEditor()
		clause = xqe.generate_clause(operator="UNASSIGNED", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "5")
		self.assertEquals(clause.attrib["operator"], "AND")

	def test_subsequent_nodes_inherit_or(self):
		# any clause added to a group containing an "OR" clause
		# also has the "OR" operator
		xqe = XMLQueryEditor.XMLQueryEditor()
		clause = xqe.generate_clause(operator="UNASSIGNED", field="subject", value="Quellenforschung", lang="de")
		xqe.add_clausular_element(clause, "2")
		self.assertEquals(clause.attrib["operator"], "OR")

	def test_remove_first_clause_changes_operator_on_second(self):
		# when the second node becomes the first, its operator 
		# should be "FIRST"
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.remove_node_by_id("1")
		new_first_node = xqe.retrieve_node_by_id("2")
		self.assertEquals(new_first_node.attrib["operator"], "FIRST")

	def test_remove_first_clause_has_no_operator_effect_on_third(self):
		# need to ensure that this effect does not spread too far
		xqe = XMLQueryEditor.XMLQueryEditor()
		xqe.remove_node_by_id("3")
		new_first_node = xqe.retrieve_node_by_id("5")
		self.assertEquals(new_first_node.attrib["operator"], "OR")

	def test_serialisation_to_query(self):
		# the XML needs to be converted appropriately to query form
		xqe = XMLQueryEditor.XMLQueryEditor()
		serialised_query = xqe.serialise_to_solr_query()
		expected = "title:\"test title\" AND (-proxy_dc_subject:\"test\" OR proxy_dc_subject:\"l'examen\" OR (CREATOR:\"Leonardo da Vinci\"))"
		self.assertEquals(serialised_query, expected)









