#!/usr/bin/python
################################################################
# Date: 07.02.2014
# Username: karrelsj
# Name: Jeffrey Karrels
# Description: Parse a Peach Pit StateModel into a visual graph
################################################################


import lxml
from lxml import etree
from lxml import objectify
import networkx as nx
import matplotlib.pyplot as plt
import argparse


namespaces = {'pit': 'http://peachfuzzer.com/2012/Peach'} 	

def findStateModel(root):
	for x in root.iterfind('pit:StateModel',namespaces=namespaces):
		if('initialState' in x.attrib):
			return x
	return None
	
def getInitialStateName(Element):
	if('initialState' in Element.attrib):
		return Element.attrib['initialState']
	else:
		return ''

def findStateByName(element,stateName):
	for x in element.findall('pit:State',namespaces=namespaces):
		if ('name' in x.attrib):
			if (x.attrib['name'] == stateName):
				return x
	return None

def findTransitions(element):
	transitions = []
	for x in element.findall('pit:Action',namespaces=namespaces):
		if('type' in x.attrib):
			if(x.attrib['type'] == 'changeState'):
				transitions.append(x.attrib['ref'])
	return transitions

if __name__ == "__main__":                                                      
	parser = argparse.ArgumentParser(description='Process a pit statemodel to a visual graph.')
	parser.add_argument('pitfile', metavar='pitfile', type=str, help='Pit File containing StateModel')
	parser.add_argument('--outformat', '-f', default='png',  choices=['png','dot'], help='Destination File Format')
	parser.add_argument('--outfile', '-o', type=str, help='Destination Filename')
	parser.add_argument('--namespace', '-n', type=str, default='http://peachfuzzer.com/2012/Peach', help='Pit File namespace')
	args=parser.parse_args()
	 
	#Update the pit file namespace   
	if args.namespace:
		namespaces['pit'] = args.namespace

	#Open the pitfile and parse to etree	
	with open(args.pitfile,'r') as f:
		parser = etree.XMLParser(remove_blank_text=True,ns_clean=True,remove_comments=True)
		tree = etree.parse(f,parser)
		root = tree.getroot()

	#Setup a digraph for the state model
	DG=nx.DiGraph()

	#Find the StateModel and Initial State
	grammar = findStateModel(root)
	strInitialState = getInitialStateName(grammar)

	#Create the node and edges for the StateModel
	for x in grammar.findall('pit:State',namespaces=namespaces):
		DG.add_node(x.attrib['name'])
		for transitionState in findTransitions(x):
			print x.attrib['name'] + "->" + transitionState
			DG.add_node(transitionState)
			DG.add_edge(x.attrib['name'],transitionState)
	

	#Draw the digraph
	pos=nx.spring_layout(DG)
	d = nx.degree(DG)
	nx.draw(DG,pos,nodelist=d.keys(), node_size=[(v+1)*500 for v in d.values()])
	nx.draw_networkx_labels(DG,pos)
	
	#Output the digraph
	if args.outformat == 'png':
		plt.savefig(args.outfile)
		print "File saved: " + args.outfile
	elif args.outformat == 'dot':
		nx.draw_graphviz(DG)
		nx.write_dot(args.outfile)
		print "File saved: " + args.outfile
	else:
		print "Unknown output format"
