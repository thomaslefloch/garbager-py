# fabriquez un fichier texte de dictionnaire contenant un mot par ligne
# il est important que toutes les lettres de l’alphabet soient présentes
# plus le nombre de mots sera élevé, meilleur sera le résultat
# un bon exemple se trouve par exemple sur:
# http://www.lexique.org/telLexique.php
# Prendre première colonne d’un fichier de lexique pour créer le dictionnaire:
# http://www.lexique.org/public/Lexique262.zip

import io
import os
import re
import bz2
import sys
import base64
import random
import codecs
import numbers
import argparse

#--------------------------------

# constantes
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
spaces          = "                        \t\t\t\t\t\n\n\n\r\f\v"
ext             = 'a85'
# différents encodages possibles:
algos           = ['b16', 'b32', 'b64', 'b85', 'a85']
ECALLBACKS      = {
	  'a85'     : base64.a85encode
	, 'b85'     : base64.b85encode
	, 'b64'     : base64.b64encode
	, 'b32'     : base64.b32encode
	, 'b16'     : base64.b16encode
}
DCALLBACKS      = {
	  'a85'     : base64.a85decode
	, 'b85'     : base64.b85decode
	, 'b64'     : base64.b64decode
	, 'b32'     : base64.b32decode
	, 'b16'     : base64.b16decode
}
OCALLBACKS      = {
	  'a85'     : { 'foldspaces': True }
	, 'b85'     : {}
	, 'b64'     : {}
	, 'b32'     : {}
	, 'b16'     : {}
}
ecallback       = ECALLBACKS[ext]
dcallback       = DCALLBACKS[ext]
ocallback       = OCALLBACKS[ext]

# variables
dico            = {}
lines           = []

#--------------------------------

# traitement d’erreur:
def Terminate(idx, **kwargs):
	REASON = {
	   0: 'Successful'
	,  1: 'Missing operation: please specify encode/decode in the command'
	,  2: 'File "' + kwargs.get('f', '') + '" unknown'
	,  3: 'Output file "' + kwargs.get('f', '') + '" already exists. Please use -f to overwrite or -o to change name.'
	,  4: 'Reading from file "' + kwargs.get('f', '') + '" failed.'
	,  5: 'Writing to file "' + kwargs.get('f', '') + '" failed.'
	,  6: 'Wordfile contains no words for letter "' + kwargs.get('c', '') + '".'
	,  7: 'Encoding algorithm "' + kwargs.get('a', '') + '" not in ' + ', '.join(algos) + '.'
	,  8: 'Garbage offset: "' + kwargs.get('n', '') + '" is not a positive integer.'
	,  9: 'Garbage (over)write: "' + kwargs.get('w', '') + '" is not in ["i", "o"].'
	, 10: 'Garbage offset overflow: ' + str(kwargs.get('o', '')) + ' > fsize("' + kwargs.get('f', '') + '") = ' + str(kwargs.get('s', '')) + '.'
	, 11: 'Garbage recovery length: "' + kwargs.get('n', '') + '" is not a positive integer.'
	, 12: 'Garbage decode overflow: offset ' + str(kwargs.get('o', '')) + ' + length ' + str(kwargs.get('l', '')) + ' = ' + str(kwargs.get('o', '')+kwargs.get('l', '')) + ' > fsize("' + kwargs.get('f', '') + '") = ' + str(kwargs.get('s', '')) + '.'
	, 13: 'Decoding error: input file "' + kwargs.get('f', '') + '" not "' + kwargs.get('e', '') + '" encoded.'
	}
	if REASON[idx]:
		print()
		print("ERROR(", idx, "): ", REASON[idx])
		print()
	parser.print_help(sys.stderr)
	sys.exit(idx)

#--------------------------------

# fonctions de bas niveau
def dumpclean(obj):
    if type(obj)   == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print(v)
    else:
        print(obj)

def isint(s):
	try:
		int(s)
		return True
	except ValueError:
		pass
	return False

def isposint(s):
	try:
		if int(s) > 0:
			return True
	except ValueError:
		pass
	return False

#--------------------------------

# vérifie l’existence d’un fichier 
def CheckFile(file):
	if not os.path.isfile(file):
		Terminate(2, f=file)
	return

#--------------------------------

# lecture/écriture d’un fichier en UTF-8
def ReadUTF8TextFile(file):
	try:
		infile = io.open(file, mode="r", encoding="utf-8")
		ulines = infile.readlines()
		infile.close()
	except:
		Terminate(4, f=file)
	for uline in ulines:
		lines.append(re.sub(r'\n$','',uline))
	lines.sort()
	if args.verbose > 2:
		print('Sorted contents of story init file ' + file)
		print()
		print(lines)
		print()
	return lines

def WriteUTF8TextFile(file, contents):
	try:
		outfile = io.open(file, mode="w", encoding="utf-8")
		outfile.write(contents)
		outfile.close()
	except:
		Terminate(5, f=file)
	if args.verbose > 2:
		print('Contents of story file written ' + file)
		print()
		print(str(contents).encode('ascii','ignore'))
		print()
	return

#--------------------------------

# écriture d’un fichier quelconque 
def WriteFile(file, contents):
	try:
		outfile = open(file, "wb")
		outfile.write(contents)
		outfile.close()
	except:
		Terminate(5, f=file)

#--------------------------------

# lecture du dictionnaire
def ReadStory(file, lines):
	CheckFile(file)
	lines = ReadUTF8TextFile(file)

def PrepareStoryBoard(lines):
	for c in ascii_lowercase:
		rex = re.compile(r'^%s' %c)
		dico[c] = list(filter(rex.match, lines))
		if len(dico[c]) < 1:
			Terminate(6, c=c)
	if args.verbose:
		print("PrepareStoryBoard gives:")
		for c in ascii_lowercase:
			print("letter '"+c+"' len= ", len(dico[c]))

#--------------------------------

# processus de garbager
def BigBedTimeStory(stream):
	flood = ''
	for c in stream:
		if c.islower():
			flood = flood + dico[c][random.randint(0, len(dico[c]) -1 )]
		elif c.isupper():
			if random.randint(0,1):
				flood = flood + str(dico[c.lower()][random.randint(0, len(dico[c.lower()]) -1 )]).capitalize()
			else:
				flood = flood + str(dico[c.lower()][random.randint(0, len(dico[c.lower()]) -1 )]).upper()
		else:
			flood = flood + c + str(random.randint(0,10000))
		for i in range(random.randint(1,2)):
			flood = flood + spaces[random.randint(0,len(spaces)-1)]
	flood = flood + "\n"
	return flood

def UntellStory(flood):
	stream=''
	words = re.split(r'\s+',flood)
	for w in words:
		if w:
			stream = "%s%s" %(stream,w[0])
	return stream

#--------------------------------

# lecture des arguments sur la ligne de commande 
parser       = argparse.ArgumentParser()
requiredArgs = parser.add_argument_group('required arguments (at least 1)')
parser.add_argument      ("-v" , "--verbose" , action = "count", default = 0, help = "increase output verbosity")
parser.add_argument      ("-ro", "--readonly", action = "store_true", help = "only display, do not write resulting file to disk")
parser.add_argument      ("-f" , "--force"   , action = "store_true", help = "force overwrite resulting file")
parser.add_argument      ("-c" , "--compress", action = "store_true", help = "bz2 -9 (de)compress file before (de)encoding")
parser.add_argument      ("-r" , "--rot13"   , action = "store_true", help = "apply rot13 input/output after loading/before saving")
parser.add_argument      ("-s" , "--story"   ,                        help = "tells a nice story from wordfile")
parser.add_argument      ("-o" , "--output"  ,                        help = "output file name (default: fname+/-[.algo])")
parser.add_argument      ("-a" , "--algo"    ,                        help = "encoding algorithm: "+ ', '.join(algos) + " [default: " + ext + "]")
parser.add_argument      ("-g" , "--garbage" , nargs  = 4           , help = "gerbage file, offset, [i]nsert/[o]verwrite (encode), length to recover (decode). NB: no encoded output file if garbage.")
requiredArgs.add_argument("-d" , "--decode"  ,                        help = "decode a previously encoded base64 file")
requiredArgs.add_argument("-e" , "--encode"  ,                        help = "encode a file in base64")
args         = parser.parse_args()
if args.verbose:
	print('ENCODE filename: ', args.encode)
	print('DECODE filename: ', args.decode)
	dumpclean(args)
	print()

if not args.encode and not args.decode:
	Terminate(1)

if args.algo:
	if not (args.algo in algos):
		Terminate(7, a=args.algo)
	ext = args.algo

# garbaging d’un fichier 
if args.garbage:
	CheckFile(args.garbage[0])
	if not isposint(args.garbage[1]):
		Terminate(8, n=args.garbage[1])
	goff = int(args.garbage[1])
	if not (args.garbage[2] in ['i', 'o'] ) and args.encode:
		Terminate(9, w=args.garbage[2])
	gsiz = os.path.getsize(args.garbage[0])
	if (goff > gsiz):
		Terminate(10, o=goff, s=gsiz, f=args.garbage[0])
	if not isposint(args.garbage[3]):
		Terminate(11, n=args.garbage[3])
	glen = int(args.garbage[3])
	if (goff+glen > gsiz) and args.decode:
		Terminate(12, o=goff, l=glen, s=gsiz, f=args.garbage[0])
	if args.verbose:
		print("Garbage file: " + args.garbage[0] + ", offset / len: " + str(goff) + " / " + str(glen) + ", [i]nsert/[o]verwrite: ", args.garbage[2])

# préparation des callbacks 
ecallback = ECALLBACKS[ext]
dcallback = DCALLBACKS[ext]
ocallback = OCALLBACKS[ext]
if args.verbose > 1:
	print("Encoding algorithm chosen: " + ext + ", encoding function callback: " + str(ecallback) + ", decoding function callback: " + str(dcallback))

# encodage d’un fichier 
if args.encode:
	CheckFile(args.encode)
	with open(args.encode, "rb") as file:
		fcontents = file.read()
		file.close()
		if args.compress:
			fcontents = bz2.compress(fcontents, 9)
		encoded_string = str(ecallback(fcontents, **ocallback), 'cp437')
		if args.verbose:
			print("File contents to encode:")
			print(encoded_string)
	if args.story:
		ReadStory(args.story, lines)
		PrepareStoryBoard(lines)
	if args.story:
		encoded_string = BigBedTimeStory(encoded_string)
		if args.verbose > 1:
			print("Encoded file contents storied:")
			print(encoded_string.encode("utf-8","ignore"))
	if args.rot13:
		encoded_string = codecs.encode(encoded_string, 'rot13')
	if args.readonly:
		print('# Not saving resulting file. Enjoy it below:')
		dumpclean(encoded_string)
	else:
		if args.garbage:
			try:
				with open(args.garbage[0], mode='rb') as gfile:
					gcontent = gfile.read()
					gfile.close()
			except:
				Terminate(4, f=args.garbage[0])
			bstr = str.encode(encoded_string)
			if (args.garbage[2] == "i"):
				ncontent = bytes(gcontent[:goff]+bstr+gcontent[goff:])
			else:
				ncontent = bytes(gcontent[:goff]+bstr+gcontent[goff+len(bstr):])
			try:
				with open(args.garbage[0], mode='wb') as gfile:
					gfile.write(ncontent)
					gfile.close()
			except:
				Terminate(5, f=args.garbage[0])
			if args.verbose > 2:
				print()
				print("encoded garbage:")
				print(str(bstr))
				print()
			print("Garbage encoding operation succeeded. Wrote " + str(len(bstr)) + " bytes starting from position " + str(goff) + " [keep that in mind...]")
		else:
			if args.output:
				ofile = args.output
			else:
				ofile = args.encode+"."+ext
			if os.path.isfile(ofile) and not args.force:
				Terminate(3, f=ofile)
			elif args.verbose:
				print('Writing output file "' + ofile + '"')
			WriteUTF8TextFile(ofile, encoded_string)

# décodage d’un fichier 
if args.decode:
	if args.garbage:
		try:
			with open(args.garbage[0], 'rb') as gfile:
				gfile.seek(goff)
				decoded_string = gfile.read(glen).decode('cp437')
				gfile.close()
		except:
			Terminate(4, f=args.garbage[0])
	else:
		CheckFile(args.decode)
		try:
			with open(args.decode, "rb") as file:
				decoded_string = file.read().decode('cp437')
				file.close()
		except:
			Terminate(4, f=args.decode)
	if args.verbose > 2:
		print("Encoded file contents to decode:")
		print(decoded_string)
		print()
	if args.rot13:
		decoded_string = codecs.encode(decoded_string, 'rot_13')
	if args.story:
		decoded_string = UntellStory(decoded_string)
		if args.verbose > 1:
			print("Encoded file contents unstoried:")
			print(str(decoded_string))
	try:
		decoded_string = dcallback(decoded_string, **ocallback)
	except:
		Terminate(13, f=args.decode, e=ext)
	if args.compress:
		decoded_string = bz2.decompress(decoded_string)
	if args.readonly:
		print('# Not saving resulting file. Enjoy it below:')
		dumpclean(decoded_string)
	else:
		if args.output:
			ofile = args.output
		else:
			ofile = re.sub(r'\.%s$' %ext, '', args.decode)
		if os.path.isfile(ofile) and not args.force:
			Terminate(3, f=ofile)
		elif args.verbose:
			print('Writing output file "' + ofile + '"')
		obytes = bytes(decoded_string)
		WriteFile(ofile, obytes)

