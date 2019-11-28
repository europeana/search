# a very basic term extractor - really just splitting the lines
# found in the logfiles

import os

class TermExtractor:

	def __init__(self):
		self.entry_directory = os.path.join(os.path.dirname(__file__), 'intermediate_output', 'entries_by_session')
		self.terms_directory = os.path.join(os.path.dirname(__file__), 'final_output', 'terms')	
		self.terms = []

	def extract_terms(self):
		for filename in os.listdir(self.entry_directory):
			file_terms = []
			with open(os.path.join(self.entry_directory, filename)) as inf:
				for line in inf.readlines():
					try:
						(searchtype, _, _, searchterm, _, _) = line.split("\t")
						if(searchtype == "SearchInteraction" and searchterm != "NO VALUE PROVIDED"):
							file_terms.append(searchterm.strip())
					except ValueError:
						pass
			self.terms.extend(set(file_terms))

	def output_terms(self, outfile_name):
		with open(os.path.join(self.terms_directory, outfile_name), 'w') as outf:
			for term in sorted(self.terms):
				outf.write(term + "\n")
