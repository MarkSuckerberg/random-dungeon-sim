from flask import Flask
from main import GetTables
from user import DoRoll
from markupsafe import escape
from markdown import markdown

app = Flask(__name__)
roll_tables = GetTables()

htmlHead = """
<!DOCTYPE html>
<html>
	<head>
		<title>Roll Tables</title>
		<style>
			@media (prefers-color-scheme: dark){
				body {
					background:#000;
					color:#fff
				}
			}
			body{
				margin:1em auto;
				max-width:40em;
				padding:0 .62em 3.24em;
				font:1.2em/1.62 sans-serif
			}
			h1,h2,h3 {
				line-height:1.2
			}
			@media print{
				body{
					max-width:none
				}
			}
		</style>
	</head>
	<body>
"""

htmlFoot = """
	</body>
</html>
"""

@app.route('/')
def home():
	page = "<h1>Roll Tables</h1>\n"
	page += "<ul>\n"
	for table in roll_tables:
		page += f"<li><a href='/{table}'>{table.title()}</a></li>\n"
	page += "</ul>"

	return htmlHead + page + htmlFoot

@app.route('/<table>')
def roll_table(table):
	table = escape(table)

	if table not in roll_tables:
		return f"Table '{table}' not found."

	page = f"<h1>{table.title()}</h1>\n"
	page += f"<a href='/'>Home</a> | <a href='/{table}'>Roll again</a>\n"
	page += markdown(DoRoll(roll_tables, table))

	return htmlHead + page + htmlFoot
