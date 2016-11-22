# -*- coding: utf-8 -*-

"""This is NetLogoDoc. A small script that creates simple web pages based on the comments in a given NetLogo file.
NetLogoDoc It was inspired by various documentation formats, like JavaDoc and Python's various documentation systems. Originally written for Python 3, and thus may need the future package to run on Python 2. 

For further documentation, please see README.TXT
"""

from __future__ import print_function
from string import Template
from builtins import input
import sys
import re
import os
import errno
from shutil import copyfile

class NetLogoModuleAuthor:
	"""An author of a NetLogo module
	
	Attributes
	----------
	name : str
	       The name of the author
	email : str
	        The e-mail of the author
	"""
	def __init__(self, name, email):
		"""Constructs a NetLogoModuleAuthor object

		Parameters
		----------
		name : str
		       The name of the author
		email : str
		        The e-mail of the author
		"""
		self.name = name
		self.email = email
	
	def __repr__(self):
		"""Provides the textual representation of this NetLogoModuleAuthor
		
		Returns
		-------
		str
			A textual representation of this author
		"""
		return self.name + " ("+self.email+")"
	
	def __str__(self):
		"""Wraps __repr__() and returns a str
		
		Returns
		-------
		str
			The results of __repr__()
		"""
		return repr(self)

class NetLogoMethod:
	"""A NetLogo method
	
	Attributes
	----------
	name : str
	       The name of the module
	comment : str, optional
	          The comment on the method. Optional. Defaults to None
	report : str, optional
	         The data returned by this method. Optional. Defaults to None. 
	params : list
	         A list of parameters, represented as a list of tuples of name (str) and description (str, optional)
	"""
	def __init__(self, name, comment = None, report = None, *params):
		"""Creates a NetLogoMethod object
	
		Parameters
		----------
		name : str
		       The name of the module
		comment : str, optional
		          The comment on the method. Optional. Defaults to None. 
		report : str, optional
		         The data returned by this method. Optional. Defaults to None. 
		*params : list
	              A list of parameters to the function, represented as a list of tuples of name (str) and description (str, optional)
		"""
		self.name = name
		self.comment = comment
		self.report = report
		self.params = params

	def __repr__(self):
		"""Provides the textual representation of this NetLogoModuleAuthor
		
		Returns
		-------
		str
			A textual representation of this module
		"""
		s = str(self.name) + ": " + str(self.comment) + ". Takes " + str(len(self.params)) + " parameter(s)" 
		if len(self.params) > 0:
			s = s + ": "
			for param in self.params:
				s = s + str(param[0]) + " ("+ str(param[1])+"), "
			s = s[:-2]
		else:
			s = s+ "."
		return s
	
	def __str__(self):
		"""Wraps __repr__() and returns a str
		
		Returns
		-------
		str
			The results of __repr__()
		"""
		return repr(self)

class NetLogoModule:
	"""Defines a netlogo module

	Attributes
	----------
	name : str
	       The name of the module
	version : str or None, optional
	          The model version. Specified as str for convenience and to avoid problems with non-standard naming schemes. Optional. 
	author : str or None, optional
	         The author of the module. Assumed to be only one. Optional. 
	date : str or None, optional
	       When the module was last revised. Optional. 
	methods : list of NetLogoMethod
	        : A list of methods found in this module. 
	
	See also
	--------
	NetLogoMethod : The class defining a method
	"""
	def __init__(self, name, version=None, author=None, date=None):
		"""Constructs a NetLogoModule object
		name : str
		       The name of the module
		version : str or None, optional
	              The model version. Specified as str for convenience and to avoid problems with non-standard naming schemes. Optional. 
		author : str or None, optional
	             The author of the module. Assumed to be only one. Optional. 
		date : str or None, optional
	           When the module was last revised. Optional. 
		"""
		self.name = name
		self.version = version
		self.author = author
		self.date = date
		self.methods = []

	def add_method(self, method):
		"""Adds a method to this module

		Parameters
		----------
		method : NetLogoMethod
		         The method to be added to the module
		"""
		self.methods.append(method)

	def __repr__(self):
		"""Provides the textual representation of this NetLogoModule
		
		Returns
		-------
		str
			A textual representation of this module
		"""
		s = "NetLogo module \""+ str(self.name) +"\" version " + str(self.version) + ". Written by: " + str(self.author) + " on " + str(self.date) + ". "
		if len(self.methods) > 0:
			s = s + "\nContains " + str(len(self.methods)) + " methods:\n"
			for m in self.methods:
				s = s + str(m) + "\n"
		else:
			s = s + "Contains no methods"
		return s
	
	def __str__(self):
		"""Wraps __repr__() and returns a str
		
		Returns
		-------
		str
			The results of __repr__()
		"""
		return repr(self)

def parse_code(lines):
	"""Parses code to create NetLogoModule, NetLogoMethod, and NetLogoModuleAuthor objects. 
	This is very much a hack. Hic abundant leones. 

	Parameters
	----------
	lines : list of str
	        A list of strings containing NetLogo code. 
	"""
	firstline = True
	collect = {"name" : None, "version": None, "date": None, "author": None, "email": None} # Default values
	methods = []
	i = 0
	while i < len(lines):
		line = lines[i].strip() # Remove indentation and trailing whitespace
		if line.startswith(";;; "):
			line = line.strip(";").strip() # Just get the core text
			if firstline:
				collect["name"] = line
				firstline = False
			elif line.startswith("@"):
				linearr = line.split(" ", 1)
				collect[linearr[0].strip("@")] = linearr[1] # Add param to collection
			i+=1
		elif line.startswith("to ") or line.startswith("to-report "): # This captures both to and to-report statments
			linearr = line.split(" ", 2)
			i+=1
			comment = ""
			report = None
			params = []
			while lines[i].strip().startswith(";;; "):
				mline = lines[i].strip()
				if not mline.startswith(";;; @"): # Process comment. This is intentionally greedy and will append subsequent strings.
					comment = comment + mline.strip(";") + "\n"
				else:
					m = re.match(';;; @param ([a-zA-Z0-9_\-]+) ?([a-zA-Z0-9_\- ]*)', mline)
					m2 = re.match(';;; @report ([a-zA-Z0-9_\-] ?[a-zA-Z0-9_\- ]*)', mline)
					if m: 
						mg = m.groups()
						params.append([mg[0], mg[1]])
					elif m2:
						mg = m2.groups()
						report = mg[0]
				i+=1
			nlmethod = NetLogoMethod(linearr[1], comment, report, *params)
			methods.append(nlmethod)
		else:
			i+=1
	auth = NetLogoModuleAuthor(collect['author'], collect['email'])
	nlm = NetLogoModule(collect['name'], collect['version'], auth, collect['date']) 
	for method in methods:
		nlm.add_method(method)
	return nlm

def get_first_line(comment):
	"""Gets the first line of a comment. Convenience function. 

	Parameters
	----------
	comment : str
	          A complete comment. 

	Returns
	-------
	comment : str
	          The first line of the comment. 
	"""
	return comment.split("\n")[0]

def htmlize_line_breaks(comment):
	"""Formats comment to HTML by inserting <br/> tags at newlines.

	Parameters
	----------
	comment : str
	          Comment to format
	
	Returns
	-------
	comment : str
	          The HTMLized comment
	"""
	return comment.replace("\n", "\n<br/>\n")

def make_html(nlm):
	"""Creates the HTML representation of a NetLogoModel using Python's template system. 

	Parameters
	----------
	nlm : NetLogoModel
	      The NetLogoModel to be documented in HTML

	Returns
	-------
	out : str
	      The HTML representing the NetLogoModel
	"""
	import datetime

	with open("template.html", 'r') as fbody:
		bodytext = fbody.read()

	out = Template(bodytext)

	moverview = ""
	mdesc = ""
	for method in nlm.methods:
		moverview = moverview + "\n\t<tr>\n" + "\t\t<td class=\"method\"><a href=#method-"+method.name+">"+method.name +"</a></td>\n\t\t<td>"+get_first_line(method.comment)+"</td>\n\t</tr>"
		mdesc = mdesc + "\n\t<h2 class=\"method\" id=\"method-"+method.name+"\">"+method.name+"</h2>\n<p class=\"indent\">"+htmlize_line_breaks(method.comment)+"</p>\n"
		if method.report != None:
			mdesc = mdesc + "<h3 class=\"indent\">Return value</h3>\n<p class=\"indent\">"+str(method.report)+"</p>\n"
		if len(method.params) > 0:
			mdesc = mdesc + "<h3 class=\"indent\">Method parameters:</h3>\n<table class=\"params\"><tr><th>Parameter</th><th>Contents</th></tr>"
			for param in method.params:
				mdesc = mdesc + "\t<tr><td class=\"method\">"+param[0]+"</td><td>"+param[1]+"</td></tr>\n"
			mdesc = mdesc + "</table>"
	
	generated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	return out.substitute(title=nlm.name, author=nlm.author.name, email =nlm.author.email, version=nlm.version, date=nlm.date, generated=generated, method_overview=moverview, method_descriptions=mdesc)

def get_nls_from_nlogo(lines):
	"""Gets NetLogo source from an .nlogo file. 
	The nlogo file format contains a lot of different things, and thus we need to extract the actual NetLogo code from it. 

	Parameters
	----------
	lines : list of str
	        The contents of a file as a list of strings
	
	Returns
	-------
	lines : list of str
	        The NetLogo code. 
	"""
	breakline = len(lines)
	for i in range(len(lines)):
		line = lines[i].strip("\n")
		if line.startswith("@#$#@#$#@"):
			breakline = i
			break
	return lines[0:breakline]

def write_to_disk(outstr, fname):
	"""Writes the final HTML file to disk. 

	Parameters
	----------
	outstr : str
	         A string containing the HTML representation of the NetLogo module
	fname : str
	        The name of the original string
	Raises
	------
	OSError
	    Raised when the program fails to create the subdirectory
	"""
	foutdir = fname.split(".")[0] + "-docs"
	try:	
		os.makedirs(foutdir) # Create a relative path
	except FileExistsError:
		pass
	except OSError as error:
		if error.errno != errno.EEXISTS:
			raise
	with open(os.path.join(foutdir, "index.html"), 'w') as f:
		f.write(outstr)
		copyfile("style.css", os.path.join(foutdir, "style.css"))

def main():
	"""Main function. Loads data and write HTML to file."""
	if (len(sys.argv) > 1):
		fname = sys.argv[1]
	else:
		fname = input("Please specify file name: ")
	
	with open(fname, 'r') as f:
		if fname.endswith(".nlogo"):
			fread = get_nls_from_nlogo(f.readlines())
		else:
			fread = f.readlines()
		nlm = parse_code(fread)
	html_str = make_html(nlm)
	write_to_disk(html_str, fname)

if __name__ == '__main__':
	main()
