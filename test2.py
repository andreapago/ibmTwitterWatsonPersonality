__author__ = 'andrea'



import random
import string
import requests
import os
import json
import cherrypy

#os.environ['https_proxy']='https://192.168.56.101:3128/'

global tweetsData
global jsonPersonalityInsights
global personalityUserName



#main class exposed by cherrypy containing the main page
class TwitterPersonality(object):
    @cherrypy.expose
    def index(self):
        return open(os.path.abspath(os.getcwd()+"/public/index.html"))


#exposed class to interact with IBM Twitter service
class TwitterSearcher(object):
    exposed = True

    #remember of adding the right VCAP for the twitter service
    def __init__(self, vcapServices):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """

        # Local variables

        self.username = "put user"
        self.password = "put password"
        self.url = "https://"+self.username+":"+self.password+"@cdeservice.mybluemix.net:443/api/v1/messages/search"#?q="+searchTerm+"&size="+numberOfTweetsRequired

        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "twitter_insights"
            if svcName in services:
                print("Twitter Insights service found!")
                svc = services[svcName][0]["credentials"]
                self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Twitter Insights service was not found")



    def callIBMTwitterService(self, searchTerm):
        numberOfTweetsRequired = "20"
        r = requests.get(self.url+"?q="+searchTerm+"&size="+numberOfTweetsRequired)
        r.status_code
        #print r._content
        return r._content

    #the POST http is fired once the user click on the appropriate button in the browser
    @cherrypy.tools.accept(media='text/plain')
    def POST(self,search_text):
         print search_text
         jsonTweets = self.callIBMTwitterService(search_text)
         global tweetsData
         tweetsData = jsonTweets
         return jsonTweets


    
    # def GET(self, inputString):
    #      cherrypy.session['mystring'] = inputString
    #      return inputString


#exposed class to interact to provide the Twitter reply to the client (browser interface)
class TwitterReply(object):
    exposed = True



    #the GET http is fired once the Twitter messages are received by the server and the search action button is actually completed
    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
         #print "rispondo al messaggio"
         global tweetsData
         return self.callHtmlFormation(tweetsData)

    #given the Tweets in JSON IBM format they are used to created the updated page with proper HTML
    def callHtmlFormation(self, line):
        str =""
        #print "QUIIIIII"
        #print line
        #for line in open('/home/delta/watsonDemo/twitterFlow.txt', 'r'):
        jsonObj = json.loads(line)
        for tweets in (jsonObj["tweets"]):
            mexBody = tweets["message"]["body"]
            preferredUsername =  tweets["message"]["actor"]["preferredUsername"]
            image = tweets["message"]["actor"]["image"]
            displayName = tweets["message"]["actor"]["displayName"]
            str = str + '''<div class="i4twitter_item">
                <table style="width:700px; margin: 0 auto;">
                    <tr>
                        <td valign="middle" rowspan="3">
                        <input align="middle" type="button" class="search_button" id="personality-tweets" value="User personality" data-user="'''+preferredUsername+'''"/>
                        </td>
                    <td valign="middle" rowspan="3">
                            <img class="i4twitter_image" src="'''+ image + '''">
                        </td>
                        <td width="100%">
                            <span class="i4twitter_name">''' + displayName + '''</span>
                            <span class="i4twitter_user">@''' + preferredUsername + '''</span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <div style="border-bottom:1px solid silver;">
                                <span class="i4twitter_sentiment i4twitter_sentiment_' + "pippo" + '">
                                    &nbsp;
                                </span>
                                <span class="i4twitter_body">
                                    '''+mexBody+'''
                                </span>
                            </div>
                            <div id="display_personality_table'''+preferredUsername+'''">
	                        </div>
                        </td>
                    </tr>
                </table>
            </div>'''
        return str




#exposed class to interact to provide the Twitter reply to the client (browser interface)
class UserTweetsAndPersonalityRetriever(object):
    exposed = True


    #constructor
    def __init__(self, vcapServices):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """

        self.userName = ""

        # Local variables
        self.url = "https://gateway.watsonplatform.net/personality-insights/api"
        self.username = "put username"
        self.password = "put password"
            #"aeJmBS1mYFOj"

        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "personality_insights"
            if svcName in services:
                print("Personality Insights service found!")
                svc = services[svcName][0]["credentials"]
                self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Personality Insights service was not found")



    #the GET http is fired once the Twitter messages are received by the server and the search action button is actually completed
    @cherrypy.tools.accept(media='text/plain')
    def GET(self, user_name):
         print "USER:"
         print user_name
         global tweetsData

         str = self.callIBMTwitterServiceUser(user_name)
         print str
         #strDecoded = str.decode('utf-8')
         #json_file= open("test2.json","r")
         #json_file.write(strDecoded.encode('utf-8'))
         #myJsonStr = json_file.read()
         #json_file.close()

         #print "prova prova"
         #print myJsonStr

         #str2 = myJsonStr
         # .decode('utf-8')

         jsonObj = json.loads(str)
         content = ""


         for tweets in (jsonObj["tweets"]):
            mexBody = tweets["message"]["body"]
            content = content + " "+mexBody
            preferredUsername =  tweets["message"]["actor"]["preferredUsername"]
         global jsonPersonalityInsights
         jsonPersonalityInsights = self.requestPersonality(content)
         #to be removed below
         global personalityUserName
         personalityUserName = self.userName




    def callIBMTwitterServiceUser(self, user):
        username = "put username"
        pwd = "put password"
        numberOfTweetsRequired = "10000"
        print user
        #print "user passed:"+self.userName
        global personalityUserName
        personalityUserName = self.userName
        r = requests.get("https://"+username+":"+pwd+"@cdeservice.mybluemix.net:443/api/v1/messages/search?q=from:"+user+"&size="+numberOfTweetsRequired)
        r.status_code
        #print r._content
        return r._content

    def requestPersonality(self,jsonBody):
        headers = {"Content-Type": "text/plain"}#, "Accept-Language": "en", "Content-Language": "en"}#, "include_raw": "false", "headers": "false" }
        #query = { "include_raw": "false", "headers": "false" }
        payload = {"body": jsonBody}
        print payload
        print self.username
        print self.password
        print self.url+"/v2/profile"
        r = requests.post(self.url+"/v2/profile", auth = (self.username, self.password), headers=headers, data=payload)
        print r.content
        return r.content






    # @cherrypy.expose
    # def search(self, length=8):
    #     return ''.join(random.sample(string.hexdigits, int(length)))

class PersonalityShower(object):
     exposed = True


     #the GET http is fired once the User push the personality button
     #creates the updatef web page in order to show the results
     @cherrypy.tools.accept(media='text/plain')
     def GET(self):
         global personalityUserName
         print personalityUserName
         global tweetsData
         global jsonPersonalityInsights

         updatedWebPageSource = self.callHtmlPersonalityFormation(jsonPersonalityInsights)
         return updatedWebPageSource






     def callHtmlPersonalityFormation(self, jsonPersonality):
        jsonObj = json.loads(jsonPersonality)
        webPage = '''<div class="CSS_Table_Example" style="width:600px">
                    <table >
                        <tr>
                            <td>
                                Trait
                            </td>
                            <td >
                                Score
                            </td>

                        </tr>'''
        for elements in jsonObj["tree"]["children"]:
            for child in elements["children"]:
                mainCategory = child["category"] #"Main Category:",child["category"]
                percentageMainCat = int(float(child["percentage"])*100)
                webPage = webPage + '''<tr>

                            <td>'''+mainCategory+'''</td>
                            <td>'''+str(percentageMainCat)+"%"'''</td>


                        </tr>'''
                for childChild in child["children"]:
                    #print childChild
                    #print "Sub Category:",
                    subCategory = childChild["name"]
                    percentageSubCat =  int(float(childChild["percentage"])*100)
                    errorSubCat = int(float(childChild["sampling_error"])*100)
                    webPage = webPage + '''
                        <tr>
                            <td>'''+subCategory+'''</td>
                            <td>'''+str(percentageSubCat)+"% +-"+str(errorSubCat)+"%"'''</td>

                        </tr>'''
        webPage = webPage +'''
                    </table>
                </div>'''
        return webPage



#main method and configuration of the cherrypy location of the exposed resources
if __name__ == '__main__':
     conf = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './public/'
         },
         "/images": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "./public/images"
        },
         "/search": {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         "/tweetResults": {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         "/tweetUserMine": {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         "/personalityResults": {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
     }

     # Get host/port from the Bluemix environment, or default to local
     HOST_NAME = os.getenv("VCAP_APP_HOST", "127.0.0.1")
     PORT_NUMBER = int(os.getenv("VCAP_APP_PORT", "8080"))
     cherrypy.config.update({
        "server.socket_host": HOST_NAME,
        "server.socket_port": PORT_NUMBER,
    })

     webapp = TwitterPersonality()
     webapp.search = TwitterSearcher(os.getenv("VCAP_SERVICES"))
     webapp.tweetResults = TwitterReply()
     webapp.tweetUserMine = UserTweetsAndPersonalityRetriever(os.getenv("VCAP_SERVICES"))
     webapp.personalityResults = PersonalityShower()

     cherrypy.quickstart(webapp, '/', conf)
