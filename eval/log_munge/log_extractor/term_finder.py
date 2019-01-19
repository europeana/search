# scans through term files looking for a given term
# when found, copies that line to a new output file
# TODO: currently limited to a single term

import os

class TermFinder:

	def __init__(self, search_term):
		self.search_term = search_term.lower()
		self.entry_directory = os.path.join(os.path.dirname(__file__), 'intermediate_output', 'entries_by_session')
		self.output_file = os.path.join(os.path.dirname(__file__), 'final_output', 'terms', search_term.strip() + '.txt')	
		self.log_lines = []

	def find_term(self):
		for filename in os.listdir(self.entry_directory):
			with open(os.path.join(self.entry_directory, filename)) as inf:
				for line in inf.readlines():
					if(self.search_term in line.lower()):
						self.log_lines.append(line)

	def output_found_lines(self):
		with open(self.output_file, 'w') as outf:
			for line in self.log_lines:
				outf.write(line)

