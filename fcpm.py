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


def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % re.escape(pattern), sub, string)

def rreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' ends 'string'.
    """
    return re.sub('%s$' % re.escape(pattern), sub, string)



def first(a, index):
	if a[index] == '':
		return ''
	else:
		m = re.search('^<([0-9]+?)>', a[index])
		if m:
			return first(a, int(m.group(1)))
		else:
			#m = re.search('^\(([0-9]+?)\)', a[index])
			m = re.search('^(\([0-9]+?\))|^(\(.\|[2-9]+?\))', a[index])
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
	#^(\([0-9]+?\))|^(\(.\|[2-9]+?\))
	m = re.search('^(\([0-9]+?\))|^(\(.\|[2-9]+?\))', a[index])
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

def next_symbol(a, nonterminal, prefix):
	if a[nonterminal] == '':
		return ''

	m = re.search('^' + re.escape(prefix) + '((\([0-9]+?\))|(\(.\|[2-9]+?\))|(<[0-9]+?>)|(.))', a[nonterminal])
	if m:
		return m.group(1)
	else:
		return ''

def prev_symbol(a, nonterminal, suffix):
	if a[nonterminal] == '':
		return ''

	m = re.search('((\([0-9]+?\))|(\(.\|[2-9]+?\))|(<[0-9]+?>)|(.))' + re.escape(suffix) + '$', a[nonterminal])
	if m:
		return m.group(1)
	else:
		return ''

def remove_nonterminal(a, nonterminal):
	for i in range(len(a)):
		a[i] = string.replace(a[i], '<' + str(nonterminal) + '>', '')

def remove_prefix(a, index):
	if a[index] == '':
		return

	s = next_symbol(a, index, '')
	block = ''
	symbol = ''
	len_block = 0
	while s != '':
		m = re.search('(<[0-9]+?>)|(\(.\|[2-9]+?\))|(.)', s)
		if m.group(3):
			if symbol == '':
				block = s
				symbol = s
				len_block += 1
			elif s == symbol:
				block += s
				len_block += 1
			else:
				break
		elif m.group(1):
			nonterminal = int(m.group(1)[1:-1])

			if symbol == '':
				m = re.search('^(.)$|^\((.)\|[2-9]+?\)$', a[nonterminal])
				if m:
					sym = m.group(1) if m.group(1) else m.group(2)
					m = re.search('^<' + str(nonterminal) + '>' + sym, a[index])
					if m:
						left_pop(a, nonterminal)
						remove_nonterminal(a, nonterminal)
					else:
						break
				else:
					break
			else:
				m = re.search('^(' + symbol + ')|^\((' + symbol + ')\|[2-9]+?\)', a[nonterminal])
				if m:
					left_pop(a, nonterminal)
				else:
					break
		elif m.group(2):
			if symbol == '':
				symbol = s[1]
				block = s
				len_block += int(s[3:-1])
			elif symbol == s[1]:
				block += s
				len_block += int(s[3:-1])
			else:
				break

		s = next_symbol(a, index, block)

	if len_block >= 2:
		a[index] = lreplace(block, '(' + symbol + '|' + str(len_block) + ')', a[index])

def remove_suffix(a, index):
	if a[index] == '':
		return

	s = prev_symbol(a, index, '')
	block = ''
	symbol = ''
	len_block = 0
	while s != '':
		m = re.search('(<[0-9]+?>)|(\(.\|[2-9]+?\))|(.)', s)
		if m.group(3):
			if symbol == '':
				block = s
				symbol = s
				len_block += 1
			elif s == symbol:
				block += s
				len_block += 1
			else:
				break
		elif m.group(1):
			nonterminal = int(m.group(1)[1:-1])

			if symbol == '':
				m = re.search('^(.)$|^\((.)\|[2-9]+?\)$', a[nonterminal])
				if m:
					sym = m.group(1) if m.group(1) else m.group(2)
					m = re.search('^<' + str(nonterminal) + '>' + sym, a[index])
					if m:
						left_pop(a, nonterminal)
						remove_nonterminal(a, nonterminal)
					else:
						break
				else:
					break
			else:
				m = re.search('(' + symbol + ')$|\((' + symbol + ')\|[2-9]+?\)$', a[nonterminal])
				if m:
					left_pop(a, nonterminal)
				else:
					break
		elif m.group(2):
			if symbol == '':
				symbol = s[1]
				block = s
				len_block += int(s[3:-1])
			elif symbol == s[1]:
				block += s
				len_block += int(s[3:-1])
			else:
				break

		s = next_symbol(a, index, block)

	if len_block >= 2:
		a[index] = lreplace(block, '(' + symbol + '|' + str(len_block) + ')', a[index])


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
		remove_suffix(a, i)
		left_pop(a, i)
		right_pop(a, i)

		if a[i] == '':
			remove_nonterminal(a, i)


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