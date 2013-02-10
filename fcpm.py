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


#\((([0-9]+?)|(.\|[2-9]+?))\)

next_pair=0


def first(a, index):
	if a[index] == '':
		return ''
	else:
		m = re.search('^<([0-9]+?)>', a[index])
		if m:
			return first(a, int(m.group(1)))
		else:
			#m = re.search('^\(([0-9]+?)\)', a[index])
			m = re.search('^\((([0-9]+?)|(.\|[2-9]+?))\)', a[index])
			if m:
				return m.group(0)
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
			#m = re.search('\(([0-9]+?)\)$', a[index])
			m = re.search('\((([0-9]+?)|(.\|[2-9]+?))\)$', a[index])
			if m:
				return m.group(0)
			else:
				return a[index][-1]

def left_pop(a, index):
	f = first(a, index)

	if f == '':
		return

	m = re.search('^<([0-9]+?)>', a[index])
	if m:
		left_pop(a, int(m.group(1)))

	#m = re.search('^\(([0-9]+?)\)', a[index])
	m = re.search('^\((([0-9]+?)|(.\|[2-9]+?))\)', a[index])
	if m:
		a[index] = a[index][len(m.group(0)):]
	else:
		a[index] = a[index][1:]

	for i in range(len(a)):
		a[i] = string.replace(a[i], '<' + str(index) + '>', f + '<' + str(index) + '>')

def right_pop(a, index):
	l = last(a, index)

	if l == '':
		return

	m = re.search('<([0-9]+?)>$', a[index])
	if m:
		right_pop(a, int(m.group(1)))

	#m = re.search('\(([0-9]+?)\)$', a[index])
	m = re.search('\((([0-9]+?)|(.\|[2-9]+?))\)$', a[index])
	if m:
		a[index] = a[index][:-len(m.group(0))]
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

def remove_prefix(a, index):
	if a[index] == '':
		return

	#m = re.search('^' + a[index][0] + '+', a[index])
	m = re.search('^<([0-9]+?)>', a[index])
	if m:
		print 'f'
		#left_pop(a, int(m.group(1)))
	else:
		m = re.search('^(' + a[index][0] + '+)<([0-9]+?)>', a[index])
		if m:
			f = first(a, m.group(2))
			fm = re.search('\((.)\|([2-9]+?)\)', f)

			if fm:
				if fm.group(1) == a[index][0]:
					left_pop(a, m.group(2))
			elif a[index][0] == f:
				left_pop(a, m.group(2))

		m = re.search('^(' + a[index][0] + '+)|((' + a[index][0] + '+)\(' + a[index] + '\|([2-9]+?)\))', a[index])
		if m:
			if m.group(1) and len(m.group(1)) >= 2:
				a[index] = string.replace(a[index], m.group(1), '(' + a[index][0] + '|' + str(len(m.group(1))) + ')')
			elif m.group(2):
				a[index] = string.replace(a[index], m.group(2), '(' + a[index][0] + '|' + str(len(m.group(3)) + int(m.group(4))) + ')')


def preprocessing(a, n, nm):
	for i in range(len(a)):
		if i == n or i == nm:
			continue

		left_pop(a, i)
		right_pop(a, i)

		if a[i] == '':
			remove_nonterminal(a, i)

def pair_comp(a, nm, pair):
	global next_pair

	m = re.search('^\(([0-9]+?)\)', pair)
	if m:
		first_pair = m.group(0)
	else:
		first_pair = pair[0]

	m = re.search('\(([0-9]+?)\)$', pair)
	if m:
		last_pair = m.group(0)
	else:
		last_pair = pair[-1]

	for j in range(nm + 1):
		for i in range(nm + 1):
			f = first(a, j)
			b = first_pair + '<' + str(j) + '>'
			if b in a[i] and last_pair == f:
				left_pop(a, j)

			l = last(a, j)
			b = '<' + str(j) + '>' + last_pair
			if b in a[i] and first_pair == l:
				right_pop(a, j)

		a[j] = string.replace(a[j], pair, '(' + str(next_pair) + ')')

	for i in range(nm):
		if a[i] == '':
			remove_nonterminal(a, i)

	next_pair += 1

def rem_cr_blocks(a, n, nm):
	for i in range(len(a)):
		if i == n or i == nm:
			continue

		remove_prefix(a, i)


def print_rules(a):
	print '########################################'

	for i in range(len(a)):
		print i, ':', a[i]

	print '########################################'




def gram1():
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

	print '########################################'
	print val(a, 2)
	print val(a, 8)
	print_rules(a)

	preprocessing(a, 2, 8)
	print_rules(a)

	pair_comp(a, 8, 'ab')
	print_rules(a)

	pair_comp(a, 8, '(0)b')
	print_rules(a)

	pair_comp(a, 8, '(1)(1)')
	print_rules(a)

	print val(a, 2)
	print val(a, 8)
	print '########################################'


def gram2():
	a = []
	a.append('aa')
	a.append('<0>acca<0>')
	a.append('bb')
	a.append('<2>b<2>')
	a.append('<1><3>')
	a.append('bbbb')
	a.append('aaccaaa')
	a.append('<5>a<6>')
	a.append('<5>b<7>')
	a.append('<8>a<6>')
	a.append('<9>bbb<8>')

	#print '########################################'
	#print val(a, 4)
	#print val(a, 10)
	#print_rules(a)

	preprocessing(a, 4, 10)
	#print_rules(a)

	rem_cr_blocks(a, 4, 10)
	print_rules(a)

	print '########################################'
	#print val(a, 4)
	#print val(a, 10)
	#print '########################################'


if __name__ == "__main__":
	#main(sys.argv[1:])
	#gram1()
	gram2()