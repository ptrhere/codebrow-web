import web
import httplib
import json
import re 
        
urls = (
    '/select/(.*)', 'select_project',
    '/list/(.*)', 'list_projects',
    '/filebrowse/(.*)', 'file_browser',
    '/codebrowse/(.*)', 'code_browser',
    '/search/(.*)', 'tag_search',
    '/history/(.*)', 'show_history'
)
app = web.application(urls, globals())
render = web.template.render('templates/')

# define functions we use in our templates here:
web.template.Template.globals.update(dict(
  render = render
))


# contacts backend and parses (JSONi) answer
#
def JSONrequest(server, port, url):
	httpconn = httplib.HTTPConnection(server,port)
	httpreq = httpconn.request("GET", url)
	httpreq = httpconn.getresponse()
	content = httpreq.read() 
	parsed = json.loads(content)
	return parsed

# searches for var in GET/POST and cookies
#
def getInput(name, default=None):
	user_data = web.input()
	result = default
	try :
		result = user_data[name] 
	except KeyError, e:
		print "no web.input["+name+"]";
		try:
			user_data_cookies = web.cookies()
			result = user_data_cookies[name]
		except:
			print "no cookies["+name+"]";
			result = default
	return result

#list projects available on the backend 
#
class list_projects:        
    def GET(self, name):
        if not name: 
            name = 'index'
        projects = JSONrequest("localhost", 8080,  "/p/")
	print projects
        return render.list_projects("browse projects",projects)

# shortcut to select default project
#
class select_project:        
    def GET(self, name):
        if not name: 
            name = 'index'
        projects = JSONrequest("localhost", 8080,  "/p/")
	web.setcookie("current_project_name", projects['name'] )
	return "<a href='http://localhost:8081/filebrowse/'>project</a>";

# browse the list of the projects' files and folders
#
class file_browser:        
    def GET(self, filepath):
        if not filepath: 
            filepath= '.'
	#foo = web.cookies()
	#current_project_name =  foo.current_project_name
	current_project_name = getInput("current_project_name", "")
	current_root_dir = getInput("current_root_dir", "/") 
	cd_parsed = JSONrequest("localhost", 8080,  "/fm/"+current_project_name+ "/"+filepath)
        return render.file_browser("File Browser", cd_parsed["rootdirectories"], cd_parsed["data"])


# helper function for code highlighting
#
in_comment = False
line_number = 1

def repl(m):
	global in_comment
	global line_number
	selected = m.group(1)
	print selected
	result = ""
	if selected == "\n":
		in_comment = False
		line_number += 1
		result = "<br/>" + str(line_number) + "  "
	elif selected == "//":
		in_comment = True	
		result = selected
		print "blah"
	else:
		if in_comment == False:
			result = "<a href='/tag/"+selected+"'>"+selected+"</a>"
		else:
			result = selected
	return result

# browse the code -- tags are hyperlinked
#
class code_browser:      
    def GET(self, filepath):
        if not filepath: 
            filepath= '.'
	current_project_name =  getInput("current_project_name", "gameduino")
	current_root_dir = "/" 
	cd_parsed = JSONrequest("localhost", 8080,  "/fm/"+current_project_name+ "/"+filepath)
	raw_code =  cd_parsed["data"]["content"]
	#raw_code = re.sub(r"\b(\n|\/\/|[a-zA-Z-_][a-zA-Z0-9_\/-]*)",r"<a href='/tag/\1'>\1</a>",raw_code)
	##should try this maybe http://docs.python.org/library/re.html#text-munging
	#raw_code = re.sub(r"\n",r"<br/>",raw_code)
	raw_code = re.sub(r"(\n|\/\/|\b[a-zA-Z-_][a-zA-Z0-9_\/-]*)",repl,raw_code)
        return render.code_browser("File Browser", cd_parsed["rootdirectories"], raw_code)

# search a certain tag
#
class tag_search:
    def GET(self, name):
        if not name:
            name = 'main'
        tagname = name
        return render.tag(tagname)

# show user's browsing history 
#
class show_history:        
    def GET(self, name):
	return "not implemented";

if __name__ == "__main__":
    web.webapi.internalerror = web.debugerror
    app.run()
