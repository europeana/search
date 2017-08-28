from django.test import SimpleTestCase
from collectionbuilder.xmlutil import XMLQueryEditor

class XMLQueryEditorTestCase(SimpleTestCase):

	def setUp(self):
		self.XQE = XMLQueryEditor.XMLQueryEditor()

	def test_xml_loaded(self):
		# XML is correctly loaded and parsed
		root_node_name = False
		self.assertEquals(root_node_name, 'query')

	def test_generate_id(self):
		# to ensure uniqueness, node ids are generated
		# from timestamps
		test_id = 0
		timestamp = 1000
		self.assertEquals(test_id, timestamp)

	def test_retrieve_clause_by_id(self):
		# given the id of a clause, we retrieve it correctly
		value = False
		self.assertEquals(value, 'l\'examen')

	def test_retrieve_clause_group_by_id(self):
		# given the id of a clause group, we retrieve it correctly
		clause_count = 0
		self.assertEquals(clause_count, 2)

	def test_remove_clause_by_id(self):
		# the specified clause is removed from the XML tree
		clause = False
		self.assertIsNone(clause)

	def test_remove_clause_group_by_id(self):
		# the specified clause group is removed from the XML tree
		clause = False
		self.assertIsNone(clause)

	def test_generate_clause(self):
		# given an operator, a field, and a value, the correct
		# XML clause is generated
		expected = "<clause operator='or' deprecated='false' xml:lang='de'><field>subject</field><value>Quellenforschung</value></clause>"
		actual = None
		self.assertXMLEqual(expected, actual)

	def test_generate_clause_group(self):
		# given the material for two clauses and an operator,
		# appropriately generates a new clause group
		expected = "<clause-group operator='and' deprecated='false'><clause operator='or' deprecated='false' xml:lang='de'><field>subject</field><value>Quellenforschung</value></clause><clause operator='or' deprecated='false' xml:lang='en'><field>subject</field><value>Source criticism</value></clause></clause-group>"
		actual = None
		self.assertXMLEqual(expected, actual)

	def test_add_clause(self):
		# a given clause is added to the XML tree
		clause = None 
		self.assertIsNotNone(clause)

	def test_add_clause_group(self):
		# a given clause group is added to the XML tree
		clause_group = None
		self.assertIsNotNone(clause_group)

	def test_deprecate_clause(self):
		# the deprecation flag is correctly set and unset on clauses
		is_deprecated = False 
		self.assertTrue(is_deprecated)

	def test_deprecate_clause_group(self):
		# the deprecation flag is correctly set and unset on clause-groups
		is_deprecated = False
		self.assertTrue(is_deprecated)

	def test_negate_clause(self):
		# the negation (NOT) flag is correctly set and unset on clauses
		is_deprecated = False 
		self.assertTrue(is_deprecated)

	def test_negate_clause_group(self):
		# the negation (NOT) flag is correctly set and unset on clause-groups
		is_deprecated = False
		self.assertTrue(is_deprecated)

	def test_subsequent_nodes_inherit_not(self):
		# any clause added to a group with a "not" clause
		# already defined also has its flag set to "not"
		expected = True
		actual = None
		self.assertEquals(expected, actual)

	def test_add_clause_retains_order(self):
		# adding a clause does not affect the ordering of existing nodes
		expected_node_mark = "None"
		found_node_mark = ""
		self.assertEquals(expected_node_mark, found_node_mark)

	def test_add_clause_group_retains_order(self):
		# adding a clause group does not affect the ordering of existing nodes
		expected_node_mark = "None"
		found_node_mark = ""
		self.assertEquals(expected_node_mark, found_node_mark)

	def test_remove_clause_retains_order(self):
		# removing a clause does not affect node ordering
		expected_node_mark = "None"
		found_node_mark = ""
		self.assertEquals(expected_node_mark, found_node_mark)

	def test_remove_clause_group_retains_order(self):
		# removing a clause group does not affect node ordering
		expected_node_mark = "None"
		found_node_mark = ""
		self.assertEquals(expected_node_mark, found_node_mark)

	# we need to ensure that the boolean operators (AND|OR) are 
	# correctly handled when nodes are removed or added

	def test_first_node_operator_is_first(self):
		# the first node in a group of siblings is
		# without an operator and is labelled "FIRST"
		expected = "FIRST"
		actual = None
		self.assertEquals(expected, actual)

	def test_second_node_with_operator_unassigned_when_added(self):
		# any node added immediately after the first nodes
		# should be explicitly flagged as needing an operator
		expected = "UNASSIGNED"
		actual = None
		self.assertEquals(expected, actual)

	def test_second_node_shares_operator_with_following_siblings(self):
		expected = "AND"
		actual = None
		self.assertEquals(expected, actual)

	def test_subsequent_nodes_inherit_and(self):
		# any clause added to a group with an "AND" clause
		# already defined also has the "AND" operator
		expected = "AND"
		actual = None
		self.assertEquals(expected, actual)

	def test_subsequent_nodes_inherit_or(self):
		# any clause added to a group containing an "OR" clause
		# also has the "OR" operator
		expected = "OR"
		actual = None
		self.assertEquals(expected, actual)

	def test_remove_first_clause_changes_operator_on_second(self):
		# when the second node becomes the first, its operator 
		# should be "FIRST"
		expected = "FIRST"
		actual = None
		self.assertEquals(expected, actual)

	def test_remove_first_clause_has_no_operator_effect_on_third(self):
		# need to ensure that this effect does not spread too far
		expected = ""
		actual = None
		self.assertEquals(expected, actual)










