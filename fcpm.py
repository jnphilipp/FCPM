#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
		This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import getopt
import operator
import re
import string
import sys
import time


grammer = ''
next = 0
nonterminal_symbol = '\\'
recompress_symbol = '#'
repair_pattern = ''
repair_text = ''
to_transform = ''
verbose = False


#################################################
##################################################


def main(argv):
	global grammer
	global nonterminal_symbol
	global recompress_symbol
	global repair_pattern
	global repair_text
	global to_transform
	global verbose

	try:
		opts, args = getopt.getopt(argv, 'hvg:t:p:r:n:f:', ['help', 'verbose', 'grammer=', 'repair_text=', 'repair_pattern=', 'recompress_symbol=', 'nonterminal_symbol=', 'transform='])
	except getopt.GetoptError:
		help()
		sys.exit(2)
	
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			help()
			sys.exit()
		elif opt in ("-v", "--verbose"):
			verbose = True
		elif opt in ("-g", "--grammer"):
			grammer = arg
		elif opt in ("-p", "--repair_pattern"):
			repair_pattern = arg
		elif opt in ("-t", "--repair_text"):
			repair_text = arg
		elif opt in ("-r", "--recompress_symbol"):
			recompress_symbol = arg
		elif opt in ("-n", "--nonterminal_symbol"):
			nonterminal_symbol = arg
		elif opt in ("-f", "--transform"):
			to_transform = arg

	if grammer == '' and (repair_text == '' or repair_pattern == '') and to_transform == '':
		help()
		sys.exit(2)

def help():
	print 'Fully Compressed Pattern Matching'
	print ''
	print 'Usage: fcpm.py [ OPTIONS ]\n'
	print 'Options supported by fcpm:'
	print '   -f or --transform\n         Path to a repair to transform it'
	print '   -g or --grammer\n         Path to the grammer file'
	print '   -h or --help\n         Print this message'
	print '   -n or --nonterminal_symbol\n         Symbol that indicats begin and end of a nonterminal\n         default: \\'
	print '   -p or --repair_pattern\n         Compressed pattern provied by the repair algorithm'
	print '   -r or --recompress_symbol\n         Symbol that indicats begin and end of recompressed symbols\n         default: #'
	print '   -t or --repair_text\n         Compressed text provied by the repair algorithm'
	print '   -v or --verbose\n         Enables detailed console output'



##################################################
##################################################
def transform_repair():
	global to_transform

	start_time = time.time()
	transformed = to_transform + '.transformed'
	current_index=0

	read = open(to_transform, 'r')
	write = open(transformed, 'w')
	for line in read:
		s = string.replace(line, '\n', '').split(' -> ')
		current_index = int(s[0])
		offset = 0
		while len(re.findall((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), s[1])) > 2:
			m = re.search((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), s[1])
			while m:
				write.write(str(current_index + offset) + ' -> ' + m.group(0) + '\n')
				s[1] = re.sub(re.escape(m.group(0)), (nonterminal_symbol + str(current_index + offset) + nonterminal_symbol).encode('string-escape'), s[1])

				offset += 1
				m = re.search((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), s[1])

			m = re.search(('(^.*?' + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol + '.+?' + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol + '.*?)(' + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol+ ')').encode('string-escape'), s[1])
			if m:
				write.write(str(current_index + offset) + ' -> ' + m.group(1) + '\n')
				s[1] = re.sub(re.escape(m.group(1)), (nonterminal_symbol + str(current_index + offset) + nonterminal_symbol).encode('string-escape'), s[1])
				offset += 1

		write.write(str(current_index + offset) + ' -> ' + s[1] + '\n')

	read.close()
	write.close()

	elapsed_time = time.time() - start_time
	print 'File transformed.'
	print 'Time:', elapsed_time

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
			if len(re.findall((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), line)) > 2:
				print 'Grammer has the wrong format. Only two nonterminals are permitted on each right side.'
				sys.exit(1)
			else:
				g.append(string.replace(line, '\n', ''))
	f.close()

	return (g, m, mn)

def load_repair_grammer():
	global repair_text
	global repair_pattern

	first = False
	g = []
	last_index = -1
	m = 0
	mn = 0

	f = open(repair_pattern, 'r')
	for line in f:
		s = re.sub('\n', '', line).split(' -> ')
		if last_index + 1 == int(s[0]):
			if len(re.findall((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), line)) > 2:
				print 'Grammer has the wrong format. Only two nonterminals are permitted on each right side.'
				sys.exit(1)
			else:
				g.append(s[1])
			last_index = int(s[0])
		else:
			for i in xrange(last_index + 1, int(s[0])):
				g.append('')
			last_index = int(s[0])
			if len(re.findall((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), line)) > 2:
				print 'Grammer has the wrong format. Only two nonterminals are permitted on each right side.'
				sys.exit(1)
			else:
				g.append(s[1])
	f.close()

	m = last_index

	f = open(repair_text, 'r')
	for line in f:
		s = re.sub('\n', '', line).split(' -> ')
		if last_index + 1 == int(s[0]) + m + 1:
			if len(re.findall((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), line)) > 2:
				print 'Grammer has the wrong format. Only two nonterminals are permitted on each right side.'
				sys.exit(1)
			else:
				g.append(modify_repair_nonterminals(s[1], m + 1))
			last_index = int(s[0]) + m + 1
		else:
			for i in xrange(last_index + 1, int(s[0]) + m + 1):
				g.append('')

			if len(re.findall((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), line)) > 2:
				print 'Grammer has the wrong format. Only two nonterminals are permitted on each right side.'
				sys.exit(1)
			else:
				g.append(modify_repair_nonterminals(s[1], m + 1))
			last_index = int(s[0]) + m + 1
	f.close()

	mn = last_index

	return (g, m, mn)

def modify_repair_nonterminals(rule, add):
	s = set(re.findall((nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol).encode('string-escape'), rule))
	nonterminals = list()

	for n in s:
		nonterminals.append(int(n))
	nonterminals = sorted(nonterminals, reverse=True)

	for nonterminal in nonterminals:
		rule = re.sub((nonterminal_symbol + str(nonterminal) + nonterminal_symbol).encode('string-escape'), ('\\' + str(nonterminal + add) + '\\').encode('string-escape'), rule)

	return rule


##################################################
##################################################


def is_terminal(symbol):
	if symbol == '':
		return False

	m = re.search((nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol).encode('string-escape'), symbol)
	if m:
		return False
	else:
		return True

def is_nonterminal(symbol):
	if symbol == '':
		return False

	m = re.search((nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol).encode('string-escape'), symbol)
	if m:
		return True
	else:
		return False

def val(g, index):
	if g[index] == '':
		return ''
	else:
		val_index = g[index]
		
		nonterminals = set(re.findall((nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol).encode('string-escape'), g[index]))
		
		for nonterminal in nonterminals:
			val_index = re.sub((nonterminal_symbol + str(nonterminal) + nonterminal_symbol).encode('string-escape'), val(g, int(nonterminal)).encode('string-escape'), val_index)

		return val_index

def print_rules(g):
	print '########################################'

	for i in xrange(len(g)):
		print i, ':', g[i]

	print '########################################'


#################################################
#################################################


def next_symbol(g, nonterminal, prefix):
	if g[nonterminal] == '':
		return ''

	m = re.search(('^' + prefix + '((' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')|(' + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol + ')|(.))').encode('string-escape'), g[nonterminal])
	if m:
		return m.group(1)
	else:
		return ''

def prev_symbol(g, nonterminal, suffix):
	if g[nonterminal] == '':
		return ''

	m = re.search(('((' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')|(' + nonterminal_symbol + '[0-9]+?' + nonterminal_symbol + ')|(.))' + suffix + '$').encode('string-escape'), g[nonterminal])
	if m:
		return m.group(1)
	else:
		return ''

def all_letters(g, m):
	letters = set()

	for i in xrange(m + 1):
		letters.update(set(re.sub((nonterminal_symbol + '[0-9]+?' + nonterminal_symbol).encode('string-escape'), '', g[i])))

	return list(letters)

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


##################################################
##################################################


def fcpm(g, m, mn):
	global verbose
	global next

	start_time = time.time()
	sys.stdout.write("searching")
	sys.stdout.flush()

	if verbose:
		print '\nBefor starting:'
		print_rules(g)

	preprocessing(g, m, mn)
	letters = all_letters(g, m)

	if verbose:
		print 'After preprocessing:'
		print_rules(g)

	s = re.search(('^((' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')|(.))$').encode('string-escape'), g[m])
	while not s:
		sys.stdout.write(".")
		sys.stdout.flush()
		
		pairs = non_pairs(g, m, mn)
		cpairs = cross_pairs(g, m, mn)

		rem_cr_blocks(g, m, mn)
		fix_beginning(g, m, mn, first(g, m))
		fix_ending(g, m, mn, last(g, m))

		if verbose:
			print '\nAfter fixing begin and end:'
			print_rules(g)

		for i in xrange(len(pairs)):
			pair_comp(g, mn, pairs[i])

		for i in xrange(len(cpairs)):
			pair_comp(g, mn, cpairs[i])

		for i in xrange(len(letters)):
			compress_block(g, m, mn, letters[i])

		if verbose:
			print 'After pair and block compression:'
			print_rules(g)

		if g[m] == '':
			break
		s = re.search(('^((' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')|(.))$').encode('string-escape'), g[m])

	matches=0
	for i in xrange(m + 1, mn + 1):
		matches += len(re.findall(g[m].encode('string-escape'), g[i].encode('string-escape')))

	sys.stdout.write("\n")

	if matches != 0:
		print 'Pattern found %s times.' % matches
	else:
		print 'Pattern not found.'

	elapsed_time = time.time() - start_time
	print 'Time:', elapsed_time

def preprocessing(g, m, mn):
	for i in xrange(mn + 1):
		if i == m or i == mn:
			continue

		left_pop(g, mn, i)
		right_pop(g, mn, i)

		if g[i] == '':
			remove_nonterminal(g, mn, i)

def fix_beginning(g, m, mn, beginning):
	global next

	s = next_symbol(g, m, beginning)
	if is_nonterminal(s):
		nonterminal = int(s[1:-1])
		s = first(g, nonterminal)
		left_pop(g, mn, nonterminal)

	if beginning == s:
		compress_block(g, m, mn, beginning)
	else:
		pair_comp(g, mn, beginning + s)

def fix_ending(g, m, mn, ending):
	global next

	s = prev_symbol(g, m, ending)

	if is_nonterminal(s):
		nonterminal = int(s[1:-1])
		s = last(g, nonterminal)
		right_pop(g, mn, nonterminal)


	if ending == s:
		compress_block(g, m, mn, ending)
	else:
		pair_comp(g, mn, s + ending)

def pair_comp(g, mn, pair):
	global next

	m = re.search(('^' + recompress_symbol + '([0-9]+?)' + recompress_symbol).encode('string-escape'), pair)
	if m:
		first_pair = m.group(0)
	else:
		first_pair = pair[0]

	m = re.search((recompress_symbol + '([0-9]+?)' + recompress_symbol + '$').encode('string-escape'), pair)
	if m:
		last_pair = m.group(0)
	else:
		last_pair = pair[-1]

	if first_pair == last_pair:
		return

	for j in xrange(mn + 1):
		for i in xrange(mn + 1):
			f = first(g, j)
			b = first_pair + nonterminal_symbol + str(j) + nonterminal_symbol
			if b in g[i] and last_pair == f:
				left_pop(g, mn, j)

			l = last(g, j)
			b = nonterminal_symbol + str(j) + nonterminal_symbol + last_pair
			if b in g[i] and first_pair == l:
				right_pop(g, mn, j)

		g[j] = re.sub(pair.encode('string-escape'), (recompress_symbol + str(next) + recompress_symbol), g[j])

	for i in xrange(mn + 1):
		if g[i] == '':
			remove_nonterminal(g, mn, i)

	next += 1

def rem_cr_blocks(g, m, mn):
	for i in xrange(mn + 1):
		if i == m or i == mn:
			continue

		remove_prefix(g, mn, i)
		remove_suffix(g, mn, i)

		if g[i] == '':
			remove_nonterminal(g, mn, i)

def remove_prefix(g, mn, index):
	if g[index] == '':
		return

	symbol = first(g, index)
	left_pop(g, mn, index)
	while first(g, index) == symbol:
		left_pop(g, mn, index)

def remove_suffix(g, mn, index):
	if g[index] == '':
		return

	symbol = last(g, index)
	right_pop(g, mn, index)
	while last(g, index) == symbol:
		right_pop(g, mn, index)

def compress_block(g, m, mn, letter):
	if letter == '':
		return

	global next
	blocks = set()

	for i in xrange(m + 1):
		block = re.findall((letter + '+').encode('string-escape'), g[i])
		for b in block:
			if len(b) > 1:
				blocks.add(b)

	blocks = list(blocks)
	blocks.sort(reverse=True)
	for j in xrange(len(blocks)):
		for i in xrange(mn + 1):
			block = re.findall((letter + '+').encode('string-escape'), g[i])
			for b in block:
				if len(b) > len(blocks[j]):
					g[i] = re.sub(b, (recompress_symbol + str(next) + recompress_symbol + b[:-len(blocks[j])] + recompress_symbol + str(next) + recompress_symbol).encode('string-escape'), g[i])
				elif len(b) == len(blocks[j]):
					g[i] = re.sub(blocks[j], (recompress_symbol + str(next) + recompress_symbol).encode('string-escape'), g[i])

		next += 1


##################################################
##################################################


def first(g, index):
	if g[index] == '':
		return ''
	else:
		m = re.search(('^' + nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol).encode('string-escape'), g[index])
		if m:
			return first(g, int(m.group(1)))
		else:
			m = re.search(('^(' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')').encode('string-escape'), g[index])
			if m:
				return m.group(0)
			else:
				return g[index][0]

def last(g, index):
	if g[index] == '':
		return ''
	else:
		m = re.search((nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol + '$').encode('string-escape'), g[index])
		if m:
			return last(g, int(m.group(1)))
		else:
			m = re.search(('(' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')$').encode('string-escape'), g[index])
			if m:
				return m.group(0)
			else:
				return g[index][-1]

def left_pop(g, mn, index):
	f = first(g, index)

	if f == '':
		return

	m = re.search(('^' + nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol).encode('string-escape'), g[index])
	if m:
		left_pop(g, mn, int(m.group(1)))

	m = re.search(('^(' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')').encode('string-escape'), g[index])
	if m:
		g[index] = g[index][len(m.group(0)):]
	else:
		g[index] = g[index][1:]

	for i in xrange(mn + 1):
		g[i] = re.sub((nonterminal_symbol + str(index) + nonterminal_symbol).encode('string-escape'), (f + nonterminal_symbol + str(index) + nonterminal_symbol).encode('string-escape'), g[i])

def right_pop(g, mn, index):
	l = last(g, index)

	if l == '':
		return

	m = re.search((nonterminal_symbol + '([0-9]+?)' + nonterminal_symbol + '$').encode('string-escape'), g[index])
	if m:
		right_pop(g, mn, int(m.group(1)))

	m = re.search(('(' + recompress_symbol + '[0-9]+?' + recompress_symbol + ')$').encode('string-escape'), g[index])
	if m:
		g[index] = g[index][:-len(m.group(0))]
	else:
		g[index] = g[index][:-1]

	for i in xrange(mn + 1):
		g[i] = re.sub((nonterminal_symbol + str(index) + nonterminal_symbol).encode('string-escape'), (nonterminal_symbol + str(index) + nonterminal_symbol + l).encode('string-escape'), g[i])

def remove_nonterminal(g, mn, nonterminal):
	for i in xrange(mn + 1):
		g[i] = re.sub((nonterminal_symbol + str(nonterminal) + nonterminal_symbol).encode('string-escape'), '', g[i])

##################################################
##################################################


if __name__ == "__main__":
	g = None

	main(sys.argv[1:])

	if repair_text != '' and repair_pattern != '':
		g, m, mn = load_repair_grammer()
	elif grammer != '':
		g, m, mn = load_grammer()
	elif to_transform != '':
		transform_repair()

	if g != None:
		fcpm(g, m, mn)