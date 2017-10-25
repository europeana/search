import xml.etree.ElementTree as ET
from datetime import datetime
from .InconsistentOperatorException import InconsistentOperatorException	
import hashlib
import copy
import os
import re

class XMLQueryEditor:

	def __init__(self, query_name=""):
		if(query_name == ""):
			self._tree = self.initialise()
		else:
			self.query_name = query_name
			self._tree = self.build_tree_from_file()
		self.check_operator_suppression()

	def initialise(self):
		tree = ET.ElementTree(ET.fromstring('<query/>'))
		root = tree.getroot()
		blank_group = self.generate_clause_group()
		root.append(blank_group)
		blank_clause = self.generate_clause()
		blank_group.append(blank_clause)
		return tree

	def build_tree_from_file(self):
		return self.load_query_file()

	def load_query_file(self):
		filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'stored_queries', self.query_name + ".xml")
		tree = ET.parse(filepath)
		return tree

	def get_tree(self):
		return self._tree

	def generate_identifier(self):
		timestamp = datetime.now()
		return self.convert_timestamp_to_identifier(timestamp)

	def convert_timestamp_to_identifier(self, timestamp):
		timestamp_as_string = timestamp.strftime("%Y%m%d%H%M%S%f")
		hashed_timestamp = hashlib.md5(timestamp_as_string.encode('utf8')).hexdigest()
		return hashed_timestamp

	def retrieve_node_by_id(self, node_id):
		node = self._tree.getroot().find(".//*[@node-id=\"" + node_id + "\"]")
		return node

	def remove_node_by_id(self, node_id):
		parent = self._tree.getroot().find(".//*[@node-id=\"" + node_id + "\"]/..")
		child = parent.find("*[@node-id=\"" + node_id + "\"]")
		parent.remove(child)
		self.check_operator_suppression()

	def remove_node_from_root(self, node_id):
		self._tree.getroot().remove(self._tree.getroot().find("*[@node-id=\"" + node_id + "\"]"))
		self.check_operator_suppression()

	def generate_clause(self, operator="AND", field="", value="", lang="en", deprecated=False, negated=False):
		clause = ET.Element("clause")
		clause.attrib["node-id"] = self.generate_identifier()
		clause.attrib["operator"] = operator
		clause.attrib["xml:lang"] = lang
		clause.attrib["deprecated"] = str(deprecated).lower()
		clause.attrib["negated"] = str(negated).lower()
		clause.attrib["operator-suppressed"] = "false"
		field_el = ET.SubElement(clause, "field")
		value_el = ET.SubElement(clause, "value")
		field_el.text = field
		value_el.text = value
		return clause

	def generate_clause_group(self, operator="AND", deprecated=False, negated=False):
		clause_group = ET.Element("clause-group")
		clause_group.attrib["node-id"] = self.generate_identifier()
		clause_group.attrib["operator"] = operator
		clause_group.attrib["deprecated"] = str(deprecated).lower()
		clause_group.attrib["negated"] = str(negated).lower()
		clause_group.attrib["operator-suppressed"] = "false"
		return clause_group

	def add_clausular_element(self, clausular_element, to_el_id=None, position=-1):
		to_clause = self._tree.getroot()
		if(to_el_id is not None):
			to_clause = self.retrieve_node_by_id(to_el_id)
		clausular_element.attrib["negated"] = str(self.default_negation_setting(to_clause)).lower()
		if(position == -1):
			to_clause.append(clausular_element)
		else:
			to_clause.insert(position, clausular_element)
		clausular_element.attrib["operator"] = self.determine_operator(to_clause, clausular_element)
		self.check_operator_suppression()

	def default_negation_setting(self, parent):
		nots = ["not" for child in parent.findall("*") if child.attrib["negated"] == "true"]
		return len(nots) > 0

	def get_effective_position(self, parent, child):
		position = 1
		for sibling in parent.findall("*"):
			if(sibling is child):
				break
			elif(sibling.attrib["deprecated"] == "true"):
				pass
			else:
				position += 1
		return position

	def determine_operator(self, parent, child):
		ors = ["or" for kid in parent.findall("*") if kid.attrib["operator"] == "OR"]
		if(len(ors) > 0):
			return "OR"
		return "AND"
 
	def deprecate_by_id(self, node_id):
		dep = self.retrieve_node_by_id(node_id)
		try:
			dep.attrib["deprecated"] = "true"
			self.check_operator_suppression()
		except KeyError:
			return None

	def undeprecate_by_id(self, node_id):
		undep = self.retrieve_node_by_id(node_id)
		try:
			undep.attrib["deprecated"] = "false"
			self.check_operator_suppression()
		except KeyError:
			return None

	def negate_by_id(self, node_id):
		neg = self.retrieve_node_by_id(node_id)
		try:
			neg.attrib["negated"] = "true"
		except KeyError:
			return None

	def unnegate_by_id(self, node_id):
		unneg = self.retrieve_node_by_id(node_id)
		try:
			unneg.attrib["negated"] = "false"
		except KeyError:
			return None

	def serialise_to_solr_query(self, xml_struct=None):
		query_string = ""
		if(self.query_is_undefined()): return "*:*"
		if(xml_struct is None):
			xml_struct = self._tree
		for child in xml_struct.findall("*"):
			tag = child.tag
			if(tag == "clause"):
				query_string += self.serialise_clause_to_solr_query(xml_struct, child)
			elif(child.attrib["deprecated"] == "false"): # if it's a clause group ....
				operator = self.construct_operator(xml_struct, child)
				negator = self.construct_negator(child)
				clausular_contents = self.serialise_to_solr_query(child)
				if(clausular_contents == ""):
					query_string += ""
				else:
					query_string += " " + operator + " " + negator + "(" + clausular_contents.strip() + ")"	
		query_string = re.sub(r'\s+', ' ', query_string)
		if(not(query_string.startswith(" AND") and not(query_string.startswith(" OR")))):
			query_string = query_string.lstrip()
		return query_string

	def serialise_clause_to_solr_query(self, parent, el):
		if(el.attrib["deprecated"] == "true"): return ""
		operator = self.construct_operator(parent, el)
		negator = self.construct_negator(el)
		field = el.find("field").text.strip()
		value = el.find("value").text.strip()
		if(field == "" or value == ""): return ""
		if(value != "*"): value = "\"" + value + "\""
		clause_as_string = (" " + operator + " " + negator + field + ":" + value)
		return clause_as_string

	def construct_operator(self, parent, el):
		pos = self.get_effective_position(parent, el)
		op = el.attrib["operator"]
		if(pos == 1):
			return ""
		if(op == "AND"):
			return "AND"
		if(op == "OR"):
			return "OR"
		return ""

	def construct_negator(self, el):
		neg = el.attrib["negated"]
		if(neg == "true"):
			return "-"
		else:
			return ""

	def query_is_undefined(self):
		defined_fields = [field for field in self._tree.getroot().findall(".//clause/field") if field.text != ""]
		return len(defined_fields) == 0

	def set_field(self, new_field, node_id):
		node_to_change = self.retrieve_node_by_id(node_id)
		if(node_to_change is None): return None
		node_to_change.find("field").text = new_field

	def set_value(self, new_value, node_id):
		node_to_change = self.retrieve_node_by_id(node_id)
		if(node_to_change is None): return None
		node_to_change.find("value").text = new_value

	def set_operator(self, new_operator, node_id):
		node_to_change = self.retrieve_node_by_id(node_id)
		if(node_to_change is None): 
			return None
		if(self.operators_are_consistent(new_operator, node_id)):
		#	node_to_change.attrib["operator"] = new_operator
			parent_id = self.find_clause_parent(node_id).get("node-id")
			self.set_all_operators(new_operator, parent_id)
		else:
			raise InconsistentOperatorException('Operators should all be the same')

	def set_all_operators(self, new_operator, node_id):
		parent_node = self.retrieve_node_by_id(node_id)
		for kid in parent_node.findall("./*"):
			kid.set("operator", new_operator)
		return parent_node

	def operators_are_consistent(self, new_operator, node_id):
		clause_parent = self.find_clause_parent(node_id)
		for clause_element in clause_parent.findall("./*[@operator][@operator-suppressed=\"false\"]"):
			if(clause_element.attrib["operator"] != new_operator and clause_element.attrib["node-id"] != node_id):
				return False
		return True

	def check_operator_suppression(self):
		root = self._tree.getroot()
		all_clauses = root.findall(".//*[@deprecated]")
		for clause in all_clauses:
			node_id = clause.get("node-id")
			preceding_clause_count = self.count_preceding_operators(node_id)
			if(preceding_clause_count == 0):
				clause.set("operator-suppressed", "true")
			elif(self.is_empty_clause_group(clause)):
				clause.set("operator-suppressed", "true")
			else:
				clause.set("operator-suppressed", "false")

	def count_preceding_operators(self, node_id):
		clause_parent = self.find_clause_parent(node_id)
		all_nodes = clause_parent.findall(".//*[@deprecated=\"false\"]")
		prev_nodes = []
		for node in all_nodes:
			if(node.get("node-id") == node_id):
				break
			else:
				prev_nodes.append(node)
		return len(prev_nodes)

	def find_clause_parent(self, node_id):
		all_groups = self._tree.getroot().findall(".//clause-group")
		for group in all_groups:
			if(group.find("./*[@node-id=\"" + node_id + "\"]")):
				return group
		return self._tree.getroot() 

	def is_empty_clause_group(self, clausular_group):
		if(clausular_group.tag != "clause-group"):
			return False
		else:
			return not self.group_has_active_clauses(clausular_group)

	def group_has_active_clauses(self, clause_group):
		all_clauses = clause_group.findall(".//clause")
		for clause in all_clauses:
			if(clause.attrib["deprecated"] == "false"):
				return True 
		return False

	def convert_to_clause_group(self, node_id):
		new_node = copy.deepcopy(self.retrieve_node_by_id(node_id))
		position = self.get_element_position(node_id)
		parent_node_id = self.find_clause_parent(node_id).attrib["node-id"]
		self.remove_node_by_id(node_id)
		new_parent = self.generate_clause_group()
		new_parent.append(new_node)
		self.add_clausular_element(new_parent, parent_node_id, position)
		return self.retrieve_node_by_id(parent_node_id)

	def get_element_position(self, node_id):
		parent_node = self.find_clause_parent(node_id)
		child_count = 0
		for child in parent_node.findall("*"):
			child_id = child.get("node-id")
			if(child_id == node_id):
				return child_count
			else:
				child_count += 1

	def ungroup_clause_group(self, group_id):
		group_parent = self.find_clause_parent(group_id)
		group_node = self.retrieve_node_by_id(group_id)
		group_position = self.get_element_position(group_id)
		kids = []
		for kid in group_node.findall("./*"):
			is_consistent = self.operators_are_consistent(kid.get("operator"), group_id)
			if(not is_consistent):
				raise InconsistentOperatorException("Ungrouping yields incompatible operators")
			kids.append(copy.deepcopy(kid))
		self.remove_node_by_id(group_id)
		for kid in reversed(kids):
			group_parent.insert(group_position, kid)
		self.check_operator_suppression()
		return group_parent

	def get_facet_query_for_clause(self, node_id):
		# essentially, for the facet query we 
		# (i) check to see whether the clause in question is an 'OR' clause
		# (ii) if not, then no facet query is needed
		# (iii) if it is, the query remains the same, but with all
		# sibling clauses excluded from consideration
		child_node = self.retrieve_node_by_id(node_id)
		parent_node = self.find_clause_parent(child_node.get("node-id"))
		if(child_node.get("operator") != "OR"):
			orig_dep = child_node.get("deprecated")
			child_node.set("deprecated", "true")
			fq = self.serialise_to_solr_query()
			child_node.set("deprecated", orig_dep)
		else:
			all_dep_statuses = []
			for child in parent_node.findall("./*[@deprecated]"):
				all_dep_statuses.append(child.get("deprecated"))
				child.set("deprecated", "true")
			fq = self.serialise_to_solr_query()
			all_dep_statuses.reverse()
			for child in parent_node.findall("./*[@deprecated]"):
				child.set("deprecated", all_dep_statuses.pop())
		if(fq == ""):
			fq = "*:*"
		return fq




