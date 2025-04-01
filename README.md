# Current Affairs - An Electricity Market Simulator
Summary goes here.

## Frameworks, Languages, and Libraries Used
Tools go here.

## Data Schema

## Deployment

For deployment, we use the cloud service Heroku and the Heroku CLI.

### Setup

1. Create a new directory and clone the repository: `git clone git@github.com:tpayne52/current_affairs.git`

2. Sign up for a Heroku account through this [link](https://signup.heroku.com/login)

3. Install the Heroku CLI depending on your OS.

    - **macOS**: `brew install heroku/brew/heroku`
    
    - **Windows**: Go to the Heroku [CLI download page](https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli) and download the Windows installer. Run the installer and follow the instructions to install it.
    
    - **Ubuntu/Debian**: `curl https://cli-assets.heroku.com/install-ubuntu.sh | sh`

4. Use the `heroku --version` command to verify your Heroku CLI installation.

### Push Code to Heroku Server

4. Using the Heroku CLI, log into your Heroku account using the `heroku login` command. This will open a browser window to authenticate your Heroku account.

5. Run `heroku create <your-app-name>` replace \<your-app-name\> with a unique name.

6. **(Optional)** Heroku needs a Procfile to know how to run the application. A default one has already been created in the repository. If you want to customize your application further, you can edit the Procfile.

7. Run `git push heroku <branch>` replace \<branch\> with the name of the git branch you would like to use. This will push your code to the Heroku server. **This may take a couple of minutes.**

### Start Server

8. Run `heroku ps:scale web=1` this will create one instance of your web process. Using one is more than sufficient for one classroom.

9. Run `heroku open` this will launch the app in the browser.

### Shutdown Server

10. Once you are finished using the server, run `heroku ps:scale web=0` this will prevent further charges while not in use.

### Summary
At this point, you should be able to:

1. Push code to a Heroku server
2. Start and run the application
3. Shut down the application



