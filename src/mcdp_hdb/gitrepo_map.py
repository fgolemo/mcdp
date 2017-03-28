'''

Types of mapping to filesystem:
- directory
- file_utf8
- yaml
- skip: do not create subdirectory. Next child should have a pattern.

# directory and file also have an associated pattern, default = %
# e.g. %.mcdp_user

Defaults:
- if it has children: directory
- if it is a string: file_utf8
- if it is an integer:  

now we should specify the mapping to the filesystem
the default is directory if it has children, files (UTF8) if it has not
so we just need to say that the user identification is  

'''