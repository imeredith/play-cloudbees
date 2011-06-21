package play.modules.cloudbees;

import play.Play;
import com.cloudbees.api.*;

import java.io.File;
import java.io.FileInputStream;
import java.util.List;
import java.util.Properties;

public class CloudBees {
    private BeesClient client;
    String domain = null;
    String message = null;
    String name = null;
    
    public CloudBees(String key, String secret) {
        client = new BeesClient("https://api.cloudbees.com/api", key, secret, "xml", "1.0");
        
        domain = System.getProperty("bees.api.domain", Play.configuration.getProperty("bees.api.domain"));
        message = System.getProperty("bees.api.message", Play.configuration.getProperty("bees.api.message", "Play! Deployment"));
        name = System.getProperty("bees.api.name", Play.configuration.getProperty("bees.api.name"));    
    }
    
    public static void main(String [] args) {
        File root = new File(System.getProperty("application.path"));
        Play.init(root, System.getProperty("play.id", ""));
        Thread.currentThread().setContextClassLoader(Play.classloader);
        
        
        String key = Play.configuration.getProperty("bees.api.key");
        String secret = Play.configuration.getProperty("bees.api.secret");
        
        key = System.getProperty("bees.api.key", key);
        secret = System.getProperty("bees.api.secret", secret);
        
        if(key == null || key.length() == 0) {
            System.out.println("bees.api.key is not set in application.conf or from --key");
        }
        
        if(secret == null || secret.length() == 0) {
            System.out.println("bees.api.secret is not set in application.conf or from --secret");
        }
        
        if(key == null || key.length() == 0 || secret == null || secret.length() == 0) {
            System.out.println("Please refer to https://grandcentral.cloudbees.com/user/keys"); //TODO
            System.exit(1);
        }
        
        // Add = to the end of the secret incase it was forgotten.
        if(secret.charAt(secret.length()-1) != '='){
            secret += "=";
        }
    
        CloudBees bees = new CloudBees(key, secret);
        
        if(args != null && args.length > 0) {
            String command = args[0];
            if(command.equals("app:list")) {
                bees.listApplications();
            } else if(command.equals("app:deploy")) {
                bees.deployApplication();
            } else if(command.equals("db:list")) {
                bees.listDatabases();
            } else if(command.equals("db:create")) {
                //bees.createDatabase();
            }
        }       
       
    }
    
    public void listApplications() {
        try {
            ApplicationListResponse res = client.applicationList();
            System.out.println("CloudBees Applications:");
            for (ApplicationInfo applicationInfo: res.getApplications()) {
                System.out.println(applicationInfo.getId());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void deployApplication() {
        try {
            boolean isError = false;
            
            String warFile = System.getProperty("bees.app.war");
            if(warFile == null || warFile.length() == 0) {
                System.out.println("WarFile not set. (This should be automatic, please submit a bug report)");
                isError = true;
            }
            
            if(domain == null || domain.length() == 0) {
                System.out.println("App Domain not set");
                isError = true;
            }
            if(name == null || name.length() == 0) {
                System.out.println("App name not set");
                isError = true;
            }
            
            if(isError) {
                System.exit(1);
            }
            
            ApplicationDeployArchiveResponse res = client.applicationDeployWar(domain + "/" + name, "", message,
                                                    warFile, null, true,
                                                    new HashWriteProgress());
            System.out.println("Application " + res.getId() + " deployed: " + res.getUrl());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void listDatabases() {
        try {
            DatabaseListResponse res = client.databaseList();
            System.out.println("CloudBees Databases:");
            for (DatabaseInfo applicationInfo: res.getDatabases()) {
                System.out.println(applicationInfo.getName());
            }
        } catch (Exception e) {
            throw new RuntimeException("Application List failure: " + e.getMessage(), e);
        }
    }
    
  

}