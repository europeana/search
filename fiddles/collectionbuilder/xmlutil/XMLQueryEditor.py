import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib
import os
import re

class XMLQueryEditor:

	def __init__(self, query_name=""):
		if(query_name == ""):
			self._tree = self.initialise()
		else:
			self.query_name = query_name
			self._tree = self.build_tree_from_file()

	def initialise(self):
		tree = ET.ElementTree(ET.fromstring('<query/>'))
		root = tree.getroot()
		blank_group = self.generate_clause_group()
		root.append(blank_group)
		blank_clause = self.generate_clause()
		blank_group.append(blank_clause)
		blank_group.attrib["operator"] = self.determine_operator(None, blank_group)
		blank_clause.attrib["operator"] = self.determine_operator(blank_group, blank_clause)
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
		for child in parent.findall("*"):
			child.attrib["operator"] = self.determine_operator(parent, child)

	def remove_node_from_root(self, node_id):
		self._tree.getroot().remove(self._tree.getroot().find("*[@node-id=\"" + node_id + "\"]"))
		for child in self._tree.getroot():
			child.attrib["operator"] = self.determine_operator(self._tree.getroot(), child)

	def generate_clause(self, operator="UNASSIGNED", field="", value="", lang="en", deprecated=False, negated=False):
		clause = ET.Element("clause")
		clause.attrib["node-id"] = self.generate_identifier()
		clause.attrib["operator"] = operator
		clause.attrib["xml:lang"] = lang
		clause.attrib["deprecated"] = str(deprecated).lower()
		clause.attrib["negated"] = str(negated).lower()
		field_el = ET.SubElement(clause, "field")
		value_el = ET.SubElement(clause, "value")
		field_el.text = field
		value_el.text = value
		return clause

	def generate_clause_group(self, operator="UNASSIGNED", deprecated=False, negated=False):
		clause_group = ET.Element("clause-group")
		clause_group.attrib["node-id"] = self.generate_identifier()
		clause_group.attrib["operator"] = operator
		clause_group.attrib["deprecated"] = str(deprecated).lower()
		clause_group.attrib["negated"] = str(negated).lower()
		return clause_group

	def add_clausular_element(self, clausular_element, to_el_id=None):
		to_clause = self._tree.getroot()
		if(to_el_id is not None):
			to_clause = self.retrieve_node_by_id(to_el_id)
		clausular_element.attrib["negated"] = str(self.default_negation_setting(to_clause)).lower()
		to_clause.append(clausular_element)
		clausular_element.attrib["operator"] = self.determine_operator(to_clause, clausular_element)

	def default_negation_setting(self, parent):
		nots = ["not" for child in parent.findall("*") if child.attrib["negated"] == "true"]
		return len(nots) > 0

	def get_position(self, parent, child):
		position = 1
		for sibling in parent.findall("*"):
			if(sibling is child):
				break
			else:
				position += 1
		return position

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
		if(parent is None): return "FIRST"
		position_in_sibs = self.get_position(parent, child)
		if(position_in_sibs == 1):
			return "FIRST"
		if(child.attrib["operator"] != "UNASSIGNED"):
			return child.attrib["operator"]
		ands = ["and" for kid in parent.findall("*") if kid.attrib["operator"] == "AND"]
		ors = ["or" for kid in parent.findall("*") if kid.attrib["operator"] == "OR"]
		if(len(ands) > 0):
			return "AND"
		if(len(ors) > 0):
			return "OR"
		return "UNASSIGNED"
 
	def deprecate_by_id(self, node_id):
		dep = self.retrieve_node_by_id(node_id)
		try:
			dep.attrib["deprecated"] = "true"
		except KeyError:
			return None

	def undeprecate_by_id(self, node_id):
		undep = self.retrieve_node_by_id(node_id)
		try:
			undep.attrib["deprecated"] = "false"
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
		clause_as_string = (" " + operator + " " + negator + field + ":\"" + value + "\"")
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
		if(node_to_change is None): return None
		node_to_change.attrib["operator"] = new_operator






