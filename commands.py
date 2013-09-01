import sys
import os
import getopt
import shutil
import subprocess
import tempfile
from optparse import OptionParser
try:
    from play.utils import package_as_war
    PLAY10 = False
except ImportError:
    PLAY10 = True
# Here you can create play commands that are specific to the module, and extend existing commands
MODULE = 'cloudbees'

# Commands that are specific to your module

COMMANDS = []
for command in ["app:list", "app:deploy"]:
    COMMANDS.append("bees:%s" % command)
    COMMANDS.append("cloudbees:%s" % command)
    
class MyOptionParser(OptionParser):
    def error(self, msg):
        pass
def execute(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")
    parser = MyOptionParser()
    parser.add_option("-k", "--key", dest="key", help="Your key")
    parser.add_option("-s", "--secret", dest="secret", help="Your secret")
    parser.add_option("-d", "--app-domain", dest = "domain")
    parser.add_option("-m", "--message", dest = "message")
    parser.add_option("-n", "--app-name", dest = "name")
    parser.app_option("-u", "--url", dest = "url")
    options, args = parser.parse_args(args)
    app.check()
    war_path = None
    java_args = []
    
    
    bees_command = command[command.index(":")+1:]
    
    for item in ["key", "secret", "domain", "message", "name", "url"]:
        if eval('options.%s' % item) != None:
            java_args.append("-Dbees.api.%s=%s" % (item, eval('options.%s' % item)))

    if "app:deploy" in bees_command:
        generate_web_inf(app.path)
        war_path =  generate_war(app, env, args)
        java_args.append("-Dbees.app.war=%s" % war_path)
  
        
    #os.system('bees %s' (args.join(' ')))
    
    java_cmd = app.java_cmd(java_args, None, "play.modules.cloudbees.CloudBees", [bees_command])
    try:
        subprocess.call(java_cmd, env=os.environ)
    except OSError:
        print "Could not execute the java executable, please make sure the JAVA_HOME environment variable is set properly (the java executable should reside at JAVA_HOME/bin/java). "
        sys.exit(-1)
    print


# This will be executed before any command (new, run...)
def before(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")
    
# This will be executed after any command (new, run...)
def after(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")
    if command == 'new':
        appconf = open(os.path.join(app.path, 'conf/application.conf'), 'a')
        appconf.write("\n")
        appconf.write("# CloudBees Database configuration\n")
        appconf.write("# ~~~~~\n")
        appconf.write("# to deploy on cloudbees: uncomment, replace yourProject, yourDBName, login and password by the correct values\n")
        appconf.write("# and switch to the cloudbees profile before generating the war\n")
        appconf.write("# %cloudbees.db=java:/comp/env/jdbc/yourProject\n\n")
        appconf.write("# %cloudbees.db.url=jdbc:cloudbees://yourDBName\n")
        appconf.write("# %cloudbees.db.driver=com.cloudbees.jdbc.Driver\n")
        appconf.write("# %cloudbees.db.user=login\n")
        appconf.write("# %cloudbees.db.pass=password\n\n")
        appconf.write("# %cloudbees.jpa.dialect=org.hibernate.dialect.MySQLDialect\n")
        appconf.write("\n")
        appconf.write("# CloudBees Account configuration\n")
        appconf.write("# ~~~~~\n")
        appconf.write("# %cloudbees.bees.api.key=your key here\n")
        appconf.write("# %cloudbees.bees.api.secret=your secret here\n")
        
        
def generate_web_inf(path):
    war_dir = os.path.join(path,'war','WEB-INF')
    stax_app_path = os.path.join(war_dir, 'cloudbees-web.xml')
    if os.path.exists(stax_app_path):
        return False;
    if not os.path.exists(war_dir):
        os.makedirs(war_dir)
    f = open(stax_app_path, 'w')
    f.write("<?xml version=\"1.0\"?>\n")
    f.write("<cloudbees-web-app xmlns=\"http://www.cloudbees.com/xml/webapp/1\">\n")
    f.write("</cloudbees-web-app>")
    f.close()
    return True
    
def generate_war(app, env, args):
    java_cmd = app.java_cmd(args)
    if os.path.exists(os.path.join(app.path, 'tmp')):
        shutil.rmtree(os.path.join(app.path, 'tmp'))
    if os.path.exists(os.path.join(app.path, 'precompiled')):
        shutil.rmtree(os.path.join(app.path, 'precompiled'))
    java_cmd.insert(2, '-Dprecompile=yes')
    try:
        result = subprocess.call(java_cmd, env=os.environ)
        if not result == 0:
            print "~"
            print "~ Precompilation has failed, stop deploying."
            print "~"
            sys.exit(-1)

    except OSError:
        print "Could not execute the java executable, please make sure the JAVA_HOME environment variable is set properly (the java executable should reside at JAVA_HOME/bin/java). "
        sys.exit(-1)


    generate_web_inf(app.path)
    war_path = os.path.join(tempfile.gettempdir(), os.path.basename(app.path))
    package_as_war(app, env, war_path, "%s.war" % war_path)
    return "%s.war" % war_path
   
