from contracts.utils import raise_desc


def is_inside_markdown_quoted_block(s, i):
    before = s[:i]
    nbefore = before.count('\n~~~')
    
    if nbefore % 2 == 1:
        return True
        # we are in a quoted block -- replace back
        
    last_line = before.split('\n')[-1]
    if last_line.startswith(' '*4):
        return True

    return False

def censor_markdown_code_blocks(s):
    def line_transform(x): 
        return x
    def inside_tag(x): 
        return x
    def code_transform(_): 
        if not _.strip(): # ignore if empty
            return _
        else:
            return 'censored-code'
    return replace_markdown_line_by_line(s, line_transform, code_transform, inside_tag)
    

def replace_markdown_line_by_line(s, line_transform=None, code_transform=None, inside_tag=None):

    identity = lambda x: x
    if line_transform is None:  
        inside_tag = identity
    if inside_tag is None: 
        inside_tag = identity
    if code_transform is None: 
        code_transform = identity
        
    def eat_code_fence(line_in, line_out):
        # remove first
        l = line_in.pop(0)
        assert l.startswith('~~~')
        line_out.append(l + ' FENCE START')
        
        while line_in:
            l = line_in.pop(0)
            if l.startswith('~~~'):
                line_out.append(l  +  ' FENCE END')
                break
            else:
                l2 = code_transform(l)
                line_out.append(l2)
                
    def eat_tag(line_in, line_out):
        first_line = l = line_in[0]
        approximate_line = len(line_out)
        assert l.startswith('<')
        tagname = ''
        l = l[1:]
        v = lambda _: _.isdigit() or _.isalpha() or _ in ['_', '-'] 
        while l and v(l[0]):
            tagname += l[0]
            l = l[1:]
        if not tagname:
            msg = 'Cannot get tagname from line %r' % line_in[0]
            msg += '\n in:%s out= %s' % (line_in, line_out)
            raise ValueError(msg)
        # <tagname> okokokok </tagname>
        # <tagname /> okokokok
        can_close_by_short = True
        # search for end of tag
        i = 0
        while line_in:
            l = line_in.pop(0)
#             print('xml tag line %r' % l)
            l2 = inside_tag(l)
            line_out.append(l2)
            
            if can_close_by_short and '/>' in l:
#                 print('xml break by short')
                return
            
            effective = l if i > 0 else l[l.index(tagname):]
            if  ('>' in effective or '<' in effective) and can_close_by_short:
#                 print('xml cannot close by short anymore')
                can_close_by_short = False 
            
            # if first line then </tag> can be anywhere
            # if not first line, it should be at the beginning
            end_tag ='</%s>' % tagname 
            cond1 = (i == 0) and (end_tag in l)
            cond2 = (i > 0) and l.startswith(end_tag) 
            if cond1 or cond2:
#                 print('Found end tag %r' % end_tag)
                return
            else:
                pass
#                 print ('No %r in %r; continue' % (end_tag, l))
            i += 1
        msg = 'Cannot find matching tag to %r. Around line %d.' % (tagname, approximate_line)
        msg + '\n Remember I want it either on the first line (anywhere) or at the start of a line.'
        raise_desc(ValueError, msg, first_line=first_line)
    
    MARK = ' ' *4
    def eat_code(line_in, line_out):
        assert line_in[0].startswith(MARK)
        while line_in:
            l = line_in.pop(0)
            if l.startswith(MARK):
                l1 = l[len(MARK):]
                l2 = MARK + code_transform(l1)
                line_out.append(l2)
            else:
                line_in.insert(0, l)
                break
                
                               
    def transform(line_in, line_out):
        
        while line_in:
            l = line_in.pop(0)
#             print('considering xml (in %d out %d) %r' % (len(line_in), len(line_out), l))
            if l.startswith('~~~'):
                line_in.insert(0, l)
#                 print('considering xml fence')
                eat_code_fence(line_in, line_out)
            elif l.startswith('<'):
                line_in.insert(0, l)
#                 print('considering xml tag')
                eat_tag(line_in, line_out)
            elif l.startswith(MARK):
#                 print('considering xml code eat_code')
                line_in.insert(0, l)
                eat_code(line_in, line_out)
            else:
                line_out.append(line_transform(l))
                
    
    _in = s.split('\n')
    _out = []
    transform(_in, _out)
    res = "\n".join(_out)
    return res
    
    
# def replace_markdown_line_by_line0(s, line_transform, code_transform=None, inside_tag=None):
#     """
#        No support for nested tags:
#         
#             <tag>
#                 <tag> ... </tag>  # counted as comment because it is 4 lines
#             </tag>
#             
#             
#     """    
#     lines = s.split('\n')
#     block_started = False
#     tag_started = False
#     tagname = None
#     
#     
#     for i in range(len(lines)):
#         l = lines[i]
#         if block_started:
#             assert not tag_started
#             if l.startswith('~~~'):
#                 block_started = False
#             continue
#         elif tag_started:
#             assert not block_started
#             assert tagname is not None
#             
#             end = '</%s' % tagname
#             if end in l:
#                 #print('detected end of tag %r' % tagname)
#                 tag_started = False
#                 
#                 # some garbage after end
#                 i = l.index(end)
#                 closing = l.index('>', i)
#                 garbage = l[closing+1:]
#                 if garbage.strip():
#                     #print('trailing: %r' % garbage)
#                     l = garbage
#             else:
#                 lines[i] = inside_tag(lines[i])
#                 continue
#         else:
#             assert not block_started and not tag_started
#             if l.startswith('~~~'):
#                 block_started = False
#                 continue
#             if l.startswith('<'):
#                 tagname = ''
#                 while l and l[0].isalpha():
#                     tagname += l[0]
#                     l = l[1:]
#                 #print('detected start of tag %r' % tagname)
#                 continue
#             
#         
#         MARK = ' ' *4 
#         is_literal = l.startswith(MARK)
#         is_code = block_started or is_literal
#         
#         if is_code:
#         
#             if is_literal:
#                 l1 = l[len(MARK):]
#                 l2 = MARK + code_transform(l1)
#             else: 
#                 l2 = code_transform(l)
#        
#         else:
#             l2 = line_transform(l)
#         lines[i] = l2
#     s2 = "\n".join(lines)
# 
#     return s2