#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import operator
import re
import string
import sys


next_pair=0
grammer=''
verbose=False


def main(argv):
	global grammer
	global verbose

	try:
		opts, args = getopt.getopt(argv, 'hvg:', ['help', 'verbose', 'grammer='])
	except getopt.GetoptError:
		print 'fcpm.py -v <verbose> -g <grammer file>'
		sys.exit(2)
	
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print 'fcpm.py -v <verbose> <grammer file>'
			sys.exit()
		elif opt in ("-v", "--verbose"):
			verbose = True
		elif opt in ("-g", "--grammer"):
			grammer = arg

	if grammer == '':
		print 'fcpm.py -v <verbose> -g <grammer file>'
		sys.exit(2)

def lreplace(pattern, sub, string):
	return re.sub('^%s' % re.escape(pattern), sub, string)

def rreplace(pattern, sub, string):
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

def expand(block):
	if block == '':
		return ''

	m = re.search('\((.)\|([2-9]+?)\)', block)
	s = ''
	if m:
		for i in xrange(int(m.group(2))):
			s += m.group(1)

	return s

def first(g, index):
	if g[index] == '':
		return ''
	else:
		m = re.search('^<([0-9]+?)>', g[index])
		if m:
			return first(g, int(m.group(1)))
		else:
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
			m = re.search('\((([0-9]+?)|(.\|[2-9]+?))\)$', g[index])
			if m:
				return m.group(0)
			else:
				return g[index][-1]

def left_pop(g, mn, index):
	f = first(g, index)

	if f == '':
		return

	m = re.search('^<([0-9]+?)>', g[index])
	if m:
		left_pop(g, mn, int(m.group(1)))

	m = re.search('^(\([0-9]+?\))|^(\(.\|[2-9]+?\))', g[index])
	if m:
		g[index] = g[index][len(m.group(0)):]
	else:
		g[index] = g[index][1:]

	for i in xrange(mn + 1):
		g[i] = string.replace(g[i], '<' + str(index) + '>', f + '<' + str(index) + '>')

def right_pop(g, mn, index):
	l = last(g, index)

	if l == '':
		return

	m = re.search('<([0-9]+?)>$', g[index])
	if m:
		right_pop(g, mn, int(m.group(1)))

	m = re.search('\((([0-9]+?)|(.\|[2-9]+?))\)$', g[index])
	if m:
		g[index] = g[index][:-len(m.group(0))]
	else:
		g[index] = g[index][:-1]

	for i in xrange(mn + 1):
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

def remove_nonterminal(g, mn, nonterminal):
	for i in xrange(mn + 1):
		g[i] = string.replace(g[i], '<' + str(nonterminal) + '>', '')

def remove_prefix(g, mn, index):
	if g[index] == '':
		return

	s = next_symbol(g, index, '')
	block = ''
	symbol = ''
	len_block = 0
	while s != '':
		m = re.search('(<[0-9]+?>)|(\(.\|[2-9]+?\))|(\([0-9]+?\))|(.)', s)
		if m.group(4):
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
						left_pop(g, mn, nonterminal)
						remove_nonterminal(g, mn, nonterminal)
					else:
						break
				else:
					break
			else:
				m = re.search('^(' + symbol + ')|^\((' + symbol + ')\|[2-9]+?\)', g[nonterminal])
				if m:
					left_pop(g, mn, nonterminal)
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
		elif m.group(3):
			break

		s = next_symbol(g, index, block)

	if len_block >= 2:
		g[index] = lreplace(block, '(' + symbol + '|' + str(len_block) + ')', g[index])

def remove_suffix(g, mn, index):
	if g[index] == '':
		return

	s = prev_symbol(g, index, '')
	block = ''
	symbol = ''
	len_block = 0
	while s != '':
		m = re.search('(<[0-9]+?>)|(\(.\|[2-9]+?\))|(\([0-9]+?\))|(.)', s)
		if m.group(4):
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
						right_pop(g, mn, nonterminal)
						remove_nonterminal(g, mn, nonterminal)
					else:
						break
				else:
					break
			else:
				m = re.search('(' + symbol + ')$|\((' + symbol + ')\|[2-9]+?\)$', g[nonterminal])
				if m:
					right_pop(g, mn, nonterminal)
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
		elif m.group(3):
			break

		s = next_symbol(g, index, block)

	if len_block >= 2:
		g[index] = rreplace(block, '(' + symbol + '|' + str(len_block) + ')', g[index])


def preprocessing(g, m, mn):
	for i in xrange(mn + 1):
		if i == m or i == mn:
			continue

		left_pop(g, mn, i)
		right_pop(g, mn, i)

		if g[i] == '':
			remove_nonterminal(g, mn, i)

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

	for j in xrange(mn + 1):
		for i in xrange(mn + 1):
			f = first(g, j)
			b = first_pair + '<' + str(j) + '>'
			if b in g[i] and last_pair == f:
				left_pop(g, mn, j)

			l = last(g, j)
			b = '<' + str(j) + '>' + last_pair
			if b in g[i] and first_pair == l:
				right_pop(g, mn, j)

		g[j] = string.replace(g[j], pair, '(' + str(next_pair) + ')')

	for i in xrange(mn + 1):
		if g[i] == '':
			remove_nonterminal(g, mn, i)

	next_pair += 1

def rem_cr_blocks(g, m, mn):
	for i in xrange(mn + 1):
		if i == m or i == mn:
			continue

		remove_prefix(g, mn, i)
		remove_suffix(g, mn, i)
		left_pop(g, mn, i)
		right_pop(g, mn, i)

		if g[i] == '':
			remove_nonterminal(g, mn, i)

def non_pairs(g, m, mn):
	pairs = []

	for i in xrange(m, -1, -1):
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

	for i in xrange(m, -1, -1):
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

	for i in xrange(mn + 1):
		g[i] = string.replace(g[i], pair, '(' + str(next_pair) + ')')

	next_pair += 1

def compress_block(g, mn, letter, max_length=-1):
	block = set()

	for i in xrange(mn + 1):
		prefix = ''
		tmp_block = ''
		tmp_block_comp = ''
		a = next_symbol(g, i, prefix)

		while a != '':
			if is_terminal(a):
				m = re.search('\(' + letter + '\|[2-9]+?\)', a)
				if m:
					if max_length == -1:
						tmp_block += a
						tmp_block_comp += expand(a)
					else:
						if len(tmp_block_comp) < max_length:
							tmp_block += a
							tmp_block_comp += expand(a)
				elif len(a) == 1:
					if a == letter:
						if max_length == -1:
							tmp_block += a
							tmp_block_comp += a
						else:
							if len(tmp_block_comp) < max_length:
								tmp_block += a
								tmp_block_comp += a
				else:
					if len(tmp_block_comp) >= 2:
						block.add((tmp_block_comp, tmp_block))
						tmp_block = ''
						tmp_block_comp = ''
			else:
				if len(tmp_block_comp) >= 2:
					block.add((tmp_block_comp, tmp_block))
					tmp_block = ''
					tmp_block_comp = ''

			prefix += a
			a = next_symbol(g, i, prefix)

		if len(tmp_block_comp) >= 2:
			block.add((tmp_block_comp, tmp_block))
			tmp_block = ''
			tmp_block_comp = ''

	block = list(block)
	block.sort(reverse=True, key=operator.itemgetter(0))
	for j in xrange(len(block)):
		for i in xrange(mn + 1):
			g[i] = string.replace(g[i], block[j][1], '(' + letter + '|' + str(len(block[j][0])) + ')')

def all_letters(g, m):
	letters = set()

	for i in xrange(m + 1):
		letters.update(set(re.sub('<[0-9]+?>', '', g[i])))

	return list(letters)

def fix_beginning(g, m, mn, beginning):
	s = next_symbol(g, m, beginning)
	if is_nonterminal(s):
		nonterminal = int(s[1:-1])
		s = first(g, nonterminal)
		left_pop(g, mn, nonterminal)

	if beginning == s:
		compress_block(g, mn, beginning, 2)
	else:
		compress_pair(g, mn, beginning + s)

def fix_ending(g, m, mn, ending):
	s = prev_symbol(g, m, ending)
	if is_nonterminal(s):
		nonterminal = int(s[1:-1])
		s = last(g, nonterminal)
		right_pop(g, mn, nonterminal)


	if ending == s:
		compress_block(g, mn, ending, 2)
	else:
		compress_pair(g, mn, s + ending)

def fcpm(g, m, mn):
	global verbose
	global next_pair

	if verbose:
		print_rules(g)

	preprocessing(g, m, mn)
	letters = all_letters(g, m)

	if verbose:
		print_rules(g)

	s = re.search('^((\([0-9]+?\))|(\(.\|[2-9]+?\))|(.))$', g[m])
	while not s:
		pairs = non_pairs(g, m, mn)
		cpairs = cross_pairs(g, m, mn)

		f = first(g, m)
		l = last(g, m)
		if f == l:
			lreplace(f, '(' + str(next_pair) + ')', g[m])
			next_pair += 1

			fix_beginning(g, m, mn, f)
			fix_ending(g, m, mn, l)
		else:
			fix_beginning(g, m, mn, f)
			fix_ending(g, m, mn, l)

		for i in xrange(len(pairs)):
			compress_pair(g, mn, pairs[i])

		for i in xrange(len(cpairs)):
			pair_comp(g, mn, cpairs[i])

		rem_cr_blocks(g, m, mn)
		for i in xrange(len(letters)):
			compress_block(g, mn, letters[i])

		if verbose:
			print_rules(g)

		s = re.search('^((\([0-9]+?\))|(\(.\|[2-9]+?\))|(.))$', g[m])

	s = re.search(re.escape(g[m]), val(g, mn))
	if s:
		print 'Pattern found.'
	else:
		print 'Pattern not found.'


def print_rules(g):
	print '########################################'

	for i in xrange(len(g)):
		print i, ':', g[i]

	print '########################################'

def load_grammer():
	global grammer

	first = False
	g = []
	m = 0
	mn = 0

	f = open(grammer, 'r')
	for line in f:
		if not first:
			s = line.split(';')
			m = int(s[0])
			mn = int(s[1])
			first = True
		else:
			g.append(string.replace(line, '\n', ''))

	return (g, m, mn)


if __name__ == "__main__":
	main(sys.argv[1:])
	g, m, mn = load_grammer()
	fcpm(g, m, mn)