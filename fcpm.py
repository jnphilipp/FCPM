#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import getopt
#import os
#import sys
#import time
#import subprocess
import re
import string

#def main(argv):
#	global pgdump

#	try:
#		opts, args = getopt.getopt(argv,"hd:m:p",["dir=", "method=", "pg_dump="])
#	except getopt.GetoptError:
#		print 'backup.py -d <backup dir> -m <backup method>'
#		sys.exit(2)
	
#	for opt, arg in opts:
#		if opt == '-h':
#			print 'backup.py -d <backup dir> -m <backup method>'
#			sys.exit()
#		elif opt in ("-d", "--dir"):
#			bdir = arg
#		elif opt in ("-m", "--method"):
#			method = arg
#		elif opt in ("-p", "--pg_dump"):
#			pgdump='dump'

#	if bdir == '' and pgdump == '':
#		print 'backup.py -d <backup dir>'
#		sys.exit(1)
		
def first(a, index):
	if a[index] == '':
		return ''
	else:
		m = re.search('^<([0-9]+?)>', a[index])
		if m:
			return first(a, int(m.group(1)))
		else:
			return a[index][0]

def last(a, index):
	if a[index] == '':
		return ''
	else:
		m = re.search('<([0-9]+?)>$', a[index])
		if m:
			return last(a, int(m.group(1)))
		else:
			return a[index][-1]

def left_pop(a, index):
	f = first(a, index)

	if f == '':
		return

	m = re.search('^<([0-9]+?)>', a[index])
	if m:
		left_pop(a, int(m.group(1)))
		a[index] = a[index][1:]
	else:
		a[index] = a[index][1:]

	for i in range(len(a)):
		a[i] = string.replace(a[i], '<' + str(index) + '>', f + '<' + str(index) + '>')

def right_pop(a, index):
	l = last(a, index)

	if l == '':
		return

	m = re.match('<([0-9]+?)>$', a[index])
	if m:
		right_pop(a, int(m.group(1)))
		a[index] = a[index][:-1]
	else:
		a[index] = a[index][:-1]

	for i in range(len(a)):
		a[i] = string.replace(a[i], '<' + str(index) + '>', '<' + str(index) + '>' + l)

def val(a, index):
	if a[index] == '':
		return ''
	else:
		val_index = a[index]
		nonterminals = set(re.findall('<([0-9]+?)>', a[index]))
		
		for nonterminal in nonterminals:
			val_index = string.replace(val_index, '<' + str(nonterminal) + '>', val(a, int(nonterminal)))

		return val_index

def remove_nonterminal(a, nonterminal):
	for i in range(len(a)):
		a[i] = string.replace(a[i], '<' + str(nonterminal) + '>', '')

def preprocessing(a, n, mn):
	for i in range(len(a)):
		if i == n or i == mn:
			continue

		left_pop(a, i)
		right_pop(a, i)

		if a[i] == '':
			remove_nonterminal(a, i)

def pair_comp(a, mn, pair):
	ii = len(a)

	for j in range(mn):
		f = first(a, j)
		l = last(a, j)

		for i in range(mn):
			b = pair[0] + '<' + str(j) + '>'
			if b in a[i] and pair[-1] == f:
				left_pop(a, j)

			b = '<' + str(j) + '>' + pair[-1]
			if b in a[i] and pair[0] == l:
				right_pop(a, j)

		a[j] = string.replace(a[j], pair, '<' + str(ii) + '>')

	a.append(pair)
	for i in range(mn):
		if a[i] == '':
			remove_nonterminal(a, i)


if __name__ == "__main__":
	#main(sys.argv[1:])

	a = []
	a.append('abb')
	a.append('<0>')
	a.append('<1><1>')
	a.append('fg')
	a.append('bbab')
	a.append('<3>a<4>b')
	a.append('<5>a<4>')
	a.append('w<3><6>c')
	a.append('<5>b<7>')

	print val(a, 2)
	print val(a, 8)
	print '################################'

	for i in range(len(a)):
		print i, ':', a[i]

	print '################################'	

	preprocessing(a, 2, 8)
	for i in range(len(a)):
		print i, ':', a[i]

	print '################################'

	pair_comp(a, 7, 'ab')
	for i in range(len(a)):
		print i, ':', a[i]

	print '################################'
	print val(a, 2)
	print val(a, 8)