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


def is_terminal(symbol):
	m = re.search('<([0-9]+?)>', symbol)

	if m:
		return False
	else:
		return True

def is_nonterminal(symbol):
	m = re.search('<([0-9]+?)>', symbol)

	if m:
		return True
	else:
		return False


def first(g, index):
	if g[index] == '':
		return ''
	else:
		m = re.search('^<([0-9]+?)>', g[index])
		if m:
			return first(g, int(m.group(1)))
		else:
			#m = re.search('^\(([0-9]+?)\)', g[index])
			m = re.search('^(\([0-9]+?\))|^(\(.\|[2-9]+?\))', g[index])
			if m:
				return m.group(0)
			else:
				return g[index][0]

def last(g, index):
	if g[index] == '':
		return ''
	else:
		m = re.search('<([0-9]+?)>$', g[index])
		if m:
			return last(g, int(m.group(1)))
		else:
			#m = re.search('\(([0-9]+?)\)$', g[index])
			m = re.search('\((([0-9]+?)|(.\|[2-9]+?))\)$', g[index])
			if m:
				return m.group(0)
			else:
				return g[index][-1]

def left_pop(g, index):
	f = first(g, index)

	if f == '':
		return

	m = re.search('^<([0-9]+?)>', g[index])
	if m:
		left_pop(g, int(m.group(1)))

	#m = re.search('^\(([0-9]+?)\)', g[index])
	#^(\([0-9]+?\))|^(\(.\|[2-9]+?\))
	m = re.search('^(\([0-9]+?\))|^(\(.\|[2-9]+?\))', g[index])
	if m:
		g[index] = g[index][len(m.group(0)):]
	else:
		g[index] = g[index][1:]

	for i in range(len(g)):
		g[i] = string.replace(g[i], '<' + str(index) + '>', f + '<' + str(index) + '>')

def right_pop(g, index):
	l = last(g, index)

	if l == '':
		return

	m = re.search('<([0-9]+?)>$', g[index])
	if m:
		right_pop(g, int(m.group(1)))

	#m = re.search('\(([0-9]+?)\)$', g[index])
	m = re.search('\((([0-9]+?)|(.\|[2-9]+?))\)$', g[index])
	if m:
		g[index] = g[index][:-len(m.group(0))]
	else:
		g[index] = g[index][:-1]

	for i in range(len(g)):
		g[i] = string.replace(g[i], '<' + str(index) + '>', '<' + str(index) + '>' + l)

def val(g, index):
	if g[index] == '':
		return ''
	else:
		val_index = g[index]
		nonterminals = set(re.findall('<([0-9]+?)>', g[index]))
		
		for nonterminal in nonterminals:
			val_index = string.replace(val_index, '<' + str(nonterminal) + '>', val(g, int(nonterminal)))

		return val_index

def next_symbol(g, nonterminal, prefix):
	if g[nonterminal] == '':
		return ''

	m = re.search('^' + re.escape(prefix) + '((\([0-9]+?\))|(\(.\|[2-9]+?\))|(<[0-9]+?>)|(.))', g[nonterminal])
	if m:
		return m.group(1)
	else:
		return ''

def prev_symbol(g, nonterminal, suffix):
	if g[nonterminal] == '':
		return ''

	m = re.search('((\([0-9]+?\))|(\(.\|[2-9]+?\))|(<[0-9]+?>)|(.))' + re.escape(suffix) + '$', g[nonterminal])
	if m:
		return m.group(1)
	else:
		return ''

def remove_nonterminal(g, nonterminal):
	for i in range(len(g)):
		g[i] = string.replace(g[i], '<' + str(nonterminal) + '>', '')

def remove_prefix(g, index):
	if g[index] == '':
		return

	s = next_symbol(g, index, '')
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
				m = re.search('^(.)$|^\((.)\|[2-9]+?\)$', g[nonterminal])
				if m:
					sym = m.group(1) if m.group(1) else m.group(2)
					m = re.search('^<' + str(nonterminal) + '>' + sym, g[index])
					if m:
						left_pop(g, nonterminal)
						remove_nonterminal(g, nonterminal)
					else:
						break
				else:
					break
			else:
				m = re.search('^(' + symbol + ')|^\((' + symbol + ')\|[2-9]+?\)', g[nonterminal])
				if m:
					left_pop(g, nonterminal)
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

		s = next_symbol(g, index, block)

	if len_block >= 2:
		g[index] = lreplace(block, '(' + symbol + '|' + str(len_block) + ')', g[index])

def remove_suffix(g, index):
	if g[index] == '':
		return

	s = prev_symbol(g, index, '')
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
				m = re.search('^(.)$|^\((.)\|[2-9]+?\)$', g[nonterminal])
				if m:
					sym = m.group(1) if m.group(1) else m.group(2)
					m = re.search('^<' + str(nonterminal) + '>' + sym, g[index])
					if m:
						left_pop(g, nonterminal)
						remove_nonterminal(g, nonterminal)
					else:
						break
				else:
					break
			else:
				m = re.search('(' + symbol + ')$|\((' + symbol + ')\|[2-9]+?\)$', g[nonterminal])
				if m:
					left_pop(g, nonterminal)
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

		s = next_symbol(g, index, block)

	if len_block >= 2:
		g[index] = lreplace(block, '(' + symbol + '|' + str(len_block) + ')', g[index])


def preprocessing(g, m, mn):
	for i in range(len(g)):
		if i == m or i == mn:
			continue

		left_pop(g, i)
		right_pop(g, i)

		if g[i] == '':
			remove_nonterminal(g, i)

def pair_comp(g, mn, pair):
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

	for j in range(mn + 1):
		for i in range(mn + 1):
			f = first(g, j)
			b = first_pair + '<' + str(j) + '>'
			if b in g[i] and last_pair == f:
				left_pop(g, j)

			l = last(g, j)
			b = '<' + str(j) + '>' + last_pair
			if b in g[i] and first_pair == l:
				right_pop(g, j)

		g[j] = string.replace(g[j], pair, '(' + str(next_pair) + ')')

	for i in range(mn):
		if g[i] == '':
			remove_nonterminal(g, i)

	next_pair += 1

def rem_cr_blocks(g, m, mn):
	for i in range(len(g)):
		if i == m or i == mn:
			continue

		remove_prefix(g, i)
		remove_suffix(g, i)
		left_pop(g, i)
		right_pop(g, i)

		if g[i] == '':
			remove_nonterminal(g, i)

def non_pairs(g, m, mn):
	pairs = []

	for i in range(m, -1, -1):
		a = next_symbol(g, i, '')
		b = next_symbol(g, i, a)
		prefix = a

		while b != '':
			if a != b and is_terminal(a) and is_terminal(b):
				pairs.append(a + b)

			a = next_symbol(g, i, prefix)
			prefix += a
			b = next_symbol(g, i, prefix)

	return pairs

def cross_pairs(g, m, mn):
	pairs = []

	for i in range(m, -1, -1):
		a = next_symbol(g, i, '')
		b = next_symbol(g, i, a)
		prefix = a

		while b != '':
			if is_nonterminal(a):
				l = last(g, int(a[1:-1]))
				if l != b:
					pairs.append(l + b)
			elif is_nonterminal(b):
				f = first(g, int(b[1:-1]))
				if a != f:
					pairs.append(a + f)

			a = next_symbol(g, i, prefix)
			prefix += a
			b = next_symbol(g, i, prefix)

	return pairs

def compress_pair(g, mn, pair):
	global next_pair

	for i in range(mn):
		g[i] = string.replace(g[i], pair, '(' + str(next_pair) + ')')

	next_pair += 1
		

def fcpm(g, m, mn):
	#|val(X_m)| > 1
	preprocessing(g, m, mn)
	s = re.search('((\([0-9]+?\))|(\(.\|[2-9]+?\))|(<[0-9]+?>)|(.))', g[m])
	while s:
		pairs = non_pairs(g, m, mn)
		cpairs = cross_pairs(g, m, mn)

		for i in range(len(pairs)):
			compress_pair(g, mn, pairs[i])

		for i in range(len(cpairs)):
			pair_comp(g, mn, cpairs[i])
		break


def print_rules(g):
	print '########################################'

	for i in range(len(g)):
		print i, ':', g[i]

	print '########################################'




def gram1():
	g = []
	g.append('gbb')
	g.append('<0>')
	g.append('<1><1>')
	g.append('fg')
	g.append('bbab')
	g.append('<3>a<4>b')
	g.append('<5>a<4>')
	g.append('w<3><6>c')
	g.append('<5>b<7>')

	print '########################################'
	print val(g, 2)
	print val(g, 8)
	print_rules(g)

	preprocessing(g, 2, 8)
	print_rules(g)

	pair_comp(g, 8, 'ab')
	print_rules(g)

	pair_comp(g, 8, '(0)b')
	print_rules(g)

	pair_comp(g, 8, '(1)(1)')
	print_rules(g)

	print val(g, 2)
	print val(g, 8)
	print '########################################'


def gram2():
	g = []
	g.append('aa')
	g.append('<0>acca<0>')
	g.append('bb')
	g.append('<2>b<2>')
	g.append('<1><3>')
	g.append('bbbb')
	g.append('aaccaaa')
	g.append('<5>a<6>')
	g.append('<5>b<7>')
	g.append('<8>a<6>')
	g.append('<9>bbb<8>')

	#print '########################################'
	#print val(g, 4)
	#print val(g, 10)
	#print_rules(g)

	#preprocessing(g, 4, 10)
	#print_rules(g)

	#rem_cr_blocks(g, 4, 10)
	fcpm(g, 4, 10)
	print_rules(g)

	print '########################################'
	#print val(g, 4)
	#print val(g, 10)
	#print '########################################'


if __name__ == "__main__":
	#main(sys.argv[1:])
	#gram1()
	gram2()