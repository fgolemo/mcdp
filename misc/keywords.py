from mcdp_lang.syntax import Syntax, SyntaxIdentifiers

k = SyntaxIdentifiers.keywords
print "\n".join("<s>%s</s>" %_.lower() for _ in sorted(k))

from mcdp_lang.dealing_with_special_letters import greek_letters_utf8

print "".join(sorted(greek_letters_utf8.values()))