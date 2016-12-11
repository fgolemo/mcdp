from mocdp.dp_report.html import ast_to_html
import os
from contracts import contract    
from conf_tools import locate_files, GlobalConfig

GlobalConfig.global_load_dir('mocdp')

from reprep.utils.natsorting import natsorted

files = [os.path.join('../../mocdp/', f) 
	for f in [
	'examples/example-battery/battery.mcdp',
	'examples/example-catalogue/catalogue1.mcdp',
	'examples/example-catalogue/choose.mcdp',
	'examples/example-catalogue/catalogue_plus_coproduct-compacter.mcdp',
	]]

files.extend([
	'big2.mcdp',
])

descriptions = {
'battery': """

## Energetics + actuation

This example shows co-design of **energetics** (choose the battery)
and **actuation**. The **recursive co-design constraint** is that the actuators
must generate lift to transport the battery, and the battery must provide
power to the actuators.

""",
	'big2': """

## A complete example

This is a complete example. The ``template`` command
allows to create models without an underlying application.

	""",

	'catalogue1': """

## Simple catalogue

This is an example of a "catalogue"; MCDPs can work directly
with a "list of parts".

	""",
"choose": """

## Coproduct of design problems

This is an example of a simple *[coproduct][coproduct] of design problems*. The choice between
two types of battery switches according to the energy required.

[coproduct]: https://en.wikipedia.org/wiki/Coproduct

""",

"catalogue_plus_coproduct-compacter": """

## Complex co-product

This is a nontrivial example where we can choose either a simple 
cell, or a cell with a voltage converter.

"""

}

from StringIO import StringIO
from contracts import indent


from cdpview.plot import do_plots
from mocdp.exceptions import DPSemanticError, DPInternalError
import os

from collections import namedtuple 

outdir = '../examples/'
Example = namedtuple('Example', 
	'filename mcdp shortname description')
examples = []
for _f in files:
	contents = open(_f).read()
	mcdp = contents
	shortname = os.path.splitext(os.path.basename(_f))[0]
	description = descriptions.get(shortname,'')
	e = Example(filename=_f, mcdp=mcdp, shortname=shortname, description=description)
	examples.append(e)

@contract(returns=str)
def format_example(e):
	print('Filename: %s' % e.filename)
	text = ''
	# text += '<h2>Example <tt>%s</tt></h2>\n\n' % e.shortname

	text += e.description
	text += '\n\n'
	# text += "MCDPL Code:"
	code =   e.mcdp

	# code = code.replace('mcdp', '<strong>mcdp</strong>')
	text += '\n\n'
	try:
		text += ast_to_html(code)
	except BaseException as err:
		text += '<pre>%s</pre>' % err

	if False:
		text += '<pre class="mcdp"><code class="mcdp">\n'
		def escape(x):
			x = x.replace('<', '&lt;')
			return x
		
		text += indent(higlight_chunk(escape(code)), ' '*4)

		text += '\n</code></pre>\n'
		text += '\n\n'

	# plots = ['ndp_clean']
	plots = ['ndp_default']
	try:
		outputs = do_plots(e.filename, plots, outdir, extra_params="")
	except DPSemanticError as e:
		text += '\n\n<code class="DPSemanticError">%s</code>\n\n' % indent(str(e), ' ' * 4)
	except DPInternalError as e:
		text += '\n\n<code class="DPInternalError">%s</code>\n\n' % indent(str(e), ' ' * 4)
	else:

		for ext, name, data in outputs:
			out = os.path.splitext(e.filename)[0] +'-%s.%s' % (name, ext)
			with open(out, 'w') as f:
				f.write(data)
			if ext in ['png'] :
				imgurl =  os.path.relpath(out, os.path.dirname(e.filename)) 
				print('url: %r' % imgurl)
				text += '\n <img class="output" src="%s"/> \n\n' % (imgurl)

	text += '\n\n'

	return text


for i, e in enumerate(examples): 

	s = StringIO()

	s.write("""---
title: Example %d
shortitle: Example %d
layout: default
# permalink: examples.html
---

	""" % (i+1, i+1))
	
	text = format_example(e)

	s.write(text)

	out = os.path.join(outdir, '05_%02d_%s.md' % (i, e.shortname))
	print('writing to %s' % out)
	with open(out, 'w') as f:
		f.write(s.getvalue())
 
	