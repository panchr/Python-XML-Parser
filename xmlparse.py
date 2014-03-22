# xmlparse.py
# Rushy Panchal
# Copyright 2014

'''xmlparse.py provides classes and functions to easily parse XML source files (or direct XML source)'''

import xml.etree.ElementTree as et
import re

### Constants

STRING = "string"
FILE = "file"
ATTRIBUTES = "attrib"
TAG = "tag"
TEXT = "text"
TAIL = "tail"
ALL = [ATTRIBUTES, TAG, TEXT, TAIL]
INDENT_PATTERN = re.compile(">\\s+<")

### Main functions

def parse(data, type):
	'''Parses the data and returns an XMLParser instance
	
	parse(raw_xml, STRING) --> XMLParser instance (interpreted as a string)
	parse(xml_path, FILE) 	--> XMLParser instance (interpreted as a file path)
	parse(raw_path)				--> XMLParser instance (interpreted as a file path)'''
	return XMLParser.parse(data, type)

def dictionary(data, type, **options):
	'''Parses the data and returns a dictionary
	
	dictionary(
		"""
		<data>
			<category attribute = "5">
				test_text
			</category>
		</data>
		"""
		)
		-->
		{'category': 
			{
				'text': 'test_text', 
				'tail': '\n\t\t',
				'tag': 'category',
				'attrib': {
					'attribute': '5'
						}
				}, 
			'text': '',
			'tail': None,
			'tag': 'data',
			'attrib': {}
			}
			
	Supported options:
		contains (ALL) --- what to add per XML element (supports: TAG, TAIL, TEXT, ATTRIBUTES, ALL); use a list for more than one'''
	return parse(data, type).get(**options)
	
### Main classes

class XMLParser:
	'''XML Parser class
	
	Usage is the same as the parse function.'''
	def __init__(self, data, type = FILE):
		if type == STRING:
			self.parsedXML = et.fromstring(data)
		elif type == FILE:
			self.parsedXML = et.parse(data)
			
		else:
			raise TypeError("type should be STRING or FILE")
	
	@staticmethod
	def parse(data, type):
		'''Parses the XML string or file, and returns an XMLParser object
		
		This is the same as the global parse function'''
		return XMLParser(data, type)
		
	def get(self, **options):
		'''Returns a dictionary representation of the XML
		
		See the global dictionary function'''
		if hasattr(self, 'xmlStructure'):
			return self.xmlStructure.dictionary
		else:
			self.xmlStructure = XMLStructure(self.parsedXML, **options)
			return self.get()
		
class XMLStructure(object):
	'''Recursively navigates an XML Element Tree and creates a dictionary representation
	
	This is automatically instantiated, so do not call it directly'''
	def __init__(self, xml, **options):
		self.xml = xml
		if isinstance(self.xml, et.Element):
			self.root = self.xml
		elif isinstance(self.xml, et.ElementTree):
			self.root = self.xml.getroot()
		else:
			raise TypeError("xml must be an ElementTree or Element instance")
		attributesToAdd = options.get('contains', ALL)
		self.dictionary = self.parseDictionary(self.root, *attributesToAdd)
		
	def parseDictionary(self, element, *attributes):
		'''Recursively creates the dictionary representation of the XML Element Tree
		
		Do not call directly --- used internally'''
		items = Object({attribute: getattr(element, attribute) for attribute in attributes})
		if len(element):
			for elem in element:
				elem_items = self.parseDictionary(elem, *attributes)
				if hasattr(items, elem.tag):
					items[elem.tag] = [items[elem.tag], elem_items]
				else:
					items[elem.tag] = elem_items
		return items
		
class Object(dict, object):
	'''A dictionary-type object that also functions as a JSON object'''
	def __getattribute__(self, key):
		'''Gets an attribute from the dictionary
		
		Example:
			x = Object(a = "string", b = 2)
			x["a"] --> "string"
			x.a --> "string"
			x.b += 3
			x.b --> 5'''
		try:
			return self[key]
		except KeyError:
			return object.__getattribute__(self, key)

	def __setattr__(self, key, value):
		'''Sets a value in the dictionary
		Same as self[key] = value
	
		returns None'''
		self[key] = value
		