# mindmeld-blueprints
Blueprints for the MindMeld Platform

This repo contains blueprints for various conversational apps. A blueprint is a core reference implementation of a MindMeld Workbench conversational app. Blueprints can be leveraged to kick start  development on a new workbench application with 
a similar use case.

## Available Blueprints

### Food Ordering

The Food Ordering blueprint is a conversational app for ordering food from a food delivery service such as Amazon Restaurants, Caviar or JustEat. This blueprint will demonstrate building an application for interacting with a number of restaurants with different menus.

### Home Assistant

The Home Assistant blueprint is a conversational app that helps users to control appliances, lights, doors, thermostat and check the weather. This blueprint will demonstrate building an application with multiple intents, domains, entities and roles.

### Video Discovery
The Video Discovery blueprint is a conversational app that helps users to search for and ask questions about movies and tv shows. This blueprint will demonstrate the extensive usage of the Knowledge Base component.

## Updating S3 Tarballs

If you make changes to any of the blueprints, be sure to update the tarballs on S3. There are three folders in S3
where you must upload the new tarball: mindmeld-blueprints-develop, mindmeld-blueprints-staging, and 
mindmeld-blueprints-master. The following is are instructions to follow using home_assistant as an
example.


1. Create a tarball after deleting any temporary files within the directory.
```bash
tar -cfz app.tar.gz home_assistant/
```

2. Remove the existing tarballs in each of the three locations.
```bash
aws s3 rm s3://mindmeld-blueprints-master/home_assistant/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-staging/home_assistant/app.tar.gz
aws s3 rm s3://mindmeld-blueprints-develop/home_assistant/app.tar.gz
```

3. Upload your new tarball.
```bash
aws s3 cp app.tar.gz s3://mindmeld-blueprints-staging/home_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-develop/home_assistant/app.tar.gz
aws s3 cp app.tar.gz s3://mindmeld-blueprints-master/home_assistant/app.tar.gz
```

4. Check that your upload was successful. To specify which bucket to download from, change the 
```mindmeld_url``` value in the ```~/.mmworkbench.config``` file. Using the value 
https://devcenter.mindmeld.com will result in pulling from the **mindmeld-blueprints-master** bucket, 
https://staging-devcenter.mindmeld.com from **mindmeld-blueprints-staging**, and 
https://develop-devcenter.mindmeld.com from **mindmeld-blueprints-develop**.

```bash
mmworkbench blueprint home_assistant
```