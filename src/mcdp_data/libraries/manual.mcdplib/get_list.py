import markdown, os, bs4, sys

data = sys.stdin.read()
html = markdown.markdown(data)
soup = bs4.BeautifulSoup(html, 'html.parser')

files = []
for tag in soup.select('a'):
	href = tag['href']
	root = os.path.splitext(href)[0]	
	files.append(root)

print " ".join(_ + '.md' for _ in files)