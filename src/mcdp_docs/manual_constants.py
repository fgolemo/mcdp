import datetime
import mocdp


class MCDPManualConstants:
    
    pdf_metadata = 'pdf_metadata.txt'
    pdf_metadata_template = pdf_metadata + '.in'
    main_template = '00_main_template.html'
    
    macros = {}
    macros['PYMCDP_VERSION'] = mocdp.__version__
    # 'July 23, 2010'
    now = datetime.datetime.now()
    today = datetime.date.today()
    macros['PYMCDP_COMPILE_DATE'] = today.strftime("%B %d, %Y") 
    macros['PYMCDP_COMPILE_TIME'] = now.strftime("%I:%M%p")
    macros['PYMCDP_COMPILE_DATE_SHORT'] = today.strftime('%Y-%m-%d') 
    macros['AUTHOR'] = 'Andrea Censi' 
    macros['TITLE'] = 'Formal tools for co-design'
    macros['TITLE_CAPS'] = 'Formal Tools for Co-Design'
    macros['SUBJECT'] = 'all about co-design'
    
    keywords = ['co-design', 'optimization', 'systems']
    macros['KEYWORDS_PDF'] = "; ".join(keywords)
    macros['KEYWORDS_HTML'] = ", ".join(keywords)
    macros['PRODUCER'] = 'PyMCDP %s + PrinceXML + pdftk' % mocdp.__version__
    macros['GENERATOR'] = macros['PRODUCER']
    macros['CREATOR'] = 'PyMCDP %s' % mocdp.__version__
    
    # D:19970915110347
    macros['CREATION_DATE_PDF'] = "D:" + now.strftime("%Y%m%d%H%M%S-05'00'")
    macros['MOD_DATE_PDF'] = macros['CREATION_DATE_PDF']
    
#     InfoBegin
# InfoKey: dc:description
# InfoValue: This is a description
# InfoBegin
# InfoKey: dc:identifier
# InfoValue: myidentifier
# InfoBegin
# InfoKey: dc:source
# InfoValue: mcdp.mit.edu
# InfoBegin
# InfoKey: dc:rights
# InfoValue: Permissive license
# InfoBegin
# InfoKey: dc:type
# InfoValue: Text
# InfoBegin
# InfoKey: dc:title
# InfoValue: @@TITLE_CAPS
