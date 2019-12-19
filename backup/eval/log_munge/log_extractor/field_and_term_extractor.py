import os
import re

class FieldAndTermExtractor:


	def __init__(self, sought_field):
		self.entry_directory = os.path.join(os.path.dirname(__file__), 'intermediate_output', 'entries_by_session')
		self.terms_directory = os.path.join(os.path.dirname(__file__), 'final_output', 'fields_and_terms', sought_field)
		if(not(os.path.exists(self.terms_directory))):
			os.makedirs(self.terms_directory)	
		self.terms = []
		self.sought_field = sought_field
		self.base_regex = re.compile(self.sought_field + ":([\w]+)")
		self.phrase_regex = re.compile(self.sought_field + ":(\".+?\")")
		self.alt_phrase_regex = re.compile(self.sought_field + ":('.+?')")
		self.parens_regex = re.compile(self.sought_field + ":(\(.+?\))")
		self.field_finder = re.compile("'(" + self.sought_field + ")': ")
		self.bracket_tidier = re.compile("[\[\]]")

	def do_extraction(self):
		self.extract_terms()
		self.output_terms()

	def grab_terms(self, search_string):
		terms = self.parens_regex.findall(search_string)
		terms.extend(self.phrase_regex.findall(search_string))
		terms.extend(self.alt_phrase_regex.findall(search_string))
		terms.extend(self.base_regex.findall(search_string))
		return terms

	def extract_terms(self):
		for filename in os.listdir(self.entry_directory):
			with open(os.path.join(self.entry_directory, filename)) as inf:
				for line in inf.readlines():
					try:
						(searchtype, _, _, searchterm, constraints, _) = line.split("\t")
						constraints = self.tidy_constraints(constraints)
						if(searchtype == "SearchInteraction"):
							self.terms.extend(self.grab_terms(searchterm + " " + constraints))
					except ValueError:
						pass

	def tidy_constraints(self, constraints):
		field_tidied = self.field_finder.sub(r"\1:", constraints)
		constraints_tidied = self.bracket_tidier.sub("", field_tidied)
		return constraints_tidied

	def output_terms(self):
		with open(os.path.join(self.terms_directory, "termlist.txt"), 'w') as outf:
			for term in sorted(set(self.terms)):
				outf.write(term + "\n")

