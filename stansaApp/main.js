(function() {
    var childProcess = require("child_process");
    var oldSpawn = childProcess.spawn;
    function mySpawn() {
        logEverywhere('spawn called');
        logEverywhere(arguments);
        var result = oldSpawn.apply(this, arguments);
        return result;
    }
    childProcess.spawn = mySpawn;
})();

const {app, BrowserWindow} = require('electron')
// Module with utilities for working with file and directory paths.
const path = require('path')
// Module with utilities for URL resolution and parsing.
const url = require('url')

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

// Deep linked url
let deeplinkingUrl

// Force Single Instance Application
const shouldQuit = app.makeSingleInstance((argv, workingDirectory) => {
  // Someone tried to run a second instance, we should focus our window.

  // Protocol handler for win32
  // argv: An array of the second instance’s (command line / deep linked) arguments
  if (process.platform == 'win32') {
    // Keep only command line / deep linked arguments
    deeplinkingUrl = argv.slice(1)
  }
  logEverywhere("app.makeSingleInstance# " + deeplinkingUrl)
  updateRepository(deeplinkingUrl)

  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore()
        mainWindow.focus()
  }
})
if (shouldQuit) {
    app.quit()
    return
}

function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({width: 400, height: 200})

  // and load the index.html of the app.
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'index.html'),
    protocol: 'file:',
    slashes: true
  }))

  // ------------------------------------------------------
  // Open the DevTools.
  mainWindow.webContents.openDevTools()
  // ------------------------------------------------------

  mainWindow.setMenu(null);

  //console.log(app.getPath('userData'))
  //console.log(app.getAppPath())

  // Protocol handler for win32
  if (process.platform == 'win32') {
    // Keep only command line / deep linked arguments
    deeplinkingUrl = process.argv.slice(1)
  }
  logEverywhere("createWindow# " + deeplinkingUrl)
  updateRepository(deeplinkingUrl)

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })


}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow()
  }
})

// Define custom protocol handler. Deep linking works on packaged versions of the application!
app.setAsDefaultProtocolClient('stansa')

// Protocol handler for osx
app.on('open-url', function (event, url) {
  event.preventDefault()
  deeplinkingUrl = url
  logEverywhere("open-url# " + deeplinkingUrl)
  updateRepository(deeplinkingUrl)
})

// Log both at dev console and at running node console instance
function logEverywhere(s) {
    console.log(s)
    if (mainWindow && mainWindow.webContents) {
        mainWindow.webContents.executeJavaScript(`console.log("${s}")`)
    }
}



function updateRepository(event) {
    var Client = require('svn-spawn');
    const osHomedir = require('os-homedir');
    const path = require('path');

    // Parsing arguments
    var argumentsStr = String(event);
    var commandArg = 'none';
    var pathArg = osHomedir() + '/Stansa/';
    var numberArg = '1';
    var nameArg = 'Stansa repository';
    var msgArg = 'Update';
    var commitArg = 0;
    var branchArg = '';
    var scriptArg = 0;
    var filesArg = '';
    var scriptParamsArg = '';

    if (argumentsStr.includes('://')) {
        var argumentsList = argumentsStr.split('://')[1].split('?')
        var argumentsLenght = argumentsList.length;
        for (var i = 0; i < argumentsLenght; i++) {
            if (argumentsList[i].substring(0,2) == 'f=') {
                commandArg = argumentsList[i].substring(2, argumentsList[i].length); } else
            if (argumentsList[i].substring(0,2) == 'p=') {
                pathArg = decodeURIComponent(argumentsList[i].substring(2, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,4) == 'uid=') {
                numberArg = decodeURIComponent(argumentsList[i].substring(4, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,5) == 'name=') {
                nameArg = decodeURIComponent(argumentsList[i].substring(5, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,4) == 'msg=') {
                msgArg = decodeURIComponent(argumentsList[i].substring(4, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,7) == 'commit=') {
                commitArg = decodeURIComponent(argumentsList[i].substring(7, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,7) == 'branch=') {
                branchArg = decodeURIComponent(argumentsList[i].substring(7, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,7) == 'script=') {
                scriptArg = decodeURIComponent(argumentsList[i].substring(7, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,6) == 'files=') {
                filesArg = decodeURIComponent(argumentsList[i].substring(6, argumentsList[i].length)) } else
            if (argumentsList[i].substring(0,10) == 'sc_params=') {
                scriptParamsArg = decodeURIComponent(argumentsList[i].substring(10, argumentsList[i].length)) }

        }
        }

    if (pathArg.substring(0,2) == '~\\' || pathArg.substring(0,2) == '~/') {
        pathArg = osHomedir() + '/' + pathArg.substring(2,pathArg.length);
        }

    var normalisedPath = path.normalize(pathArg.replace('\\', path.sep));

    var client = new Client({
            cwd: normalisedPath,
            username: 'username',
            password: 'password'
        })


    if (commandArg == "checkOut" || commandArg == "checkOut/") {
        logEverywhere("checking out the repository to the local path");

        var shell = require('shelljs');
        shell.mkdir('-p', normalisedPath);

        if (commitArg == '0') { // Checking out full repo
            logEverywhere("option 1")
            client.cmd(['co', 'svn://<ip-of-the-repository>/home/REPOS/repoId' + numberArg, '.'], function(err, data) {
                    logEverywhere('err: %s', err);
                    logEverywhere("check out done!");
                    app.quit()
                    return
                });
        } else { // Checking out revision of main
                logEverywhere("option 2")
                logEverywhere(commitArg)
                client.cmd(['co', 'svn://<ip-of-the-repository>/home/REPOS/repoId' + numberArg, '.', '-r' + commitArg], function(err, data) {
                    logEverywhere('err: %s', err);
                    logEverywhere("check out done!");
                    app.quit()
                    return
                });
            }


        }

    if (commandArg == "commit" || commandArg == "commit/") {

        var spawn = require('child_process').spawn;
        var appRootDir = require('app-root-dir').get();
        var svnCommand = appRootDir.replace('app.asar','') + 'bin\\svn.exe';
        var child = spawn(svnCommand, ['status', normalisedPath]);
        child.stdout.on('data', function(data) {
            var singleLine = data.toString();
            var statusLines = singleLine.split('\n');
            for (var i = 0; i < statusLines.length; i++) {
                    logEverywhere(statusLines[i]);
                    if (statusLines[i].substring(0,1) == "!") {
                        var pathToDelete = statusLines[i].substring(1,statusLines[i].length).trim();
                        logEverywhere(pathToDelete);
                        client.cmd(['rm', pathToDelete], function(error, stdout, stderr) {});
                    }
                }

        });

        logEverywhere('repo updated with removed files');

        client.addLocal(function(err, data) {
            logEverywhere('adding local changes for the commit');
            client.commit(msgArg, function(err, data) {
                logEverywhere('err: %s', err);
                logEverywhere('local changes has been committed!');
                app.quit()
                return
            });
        });

    }

    if (commandArg == "auto") {
        logEverywhere('Running an automatic stage')
        runAutoStage(numberArg, filesArg, scriptArg, scriptParamsArg);
        }

    if (commandArg == "none") {
      mainWindow.loadURL(url.format({
                pathname: path.join(__dirname, 'standby.html'),
                protocol: 'file:',
                slashes: true
              }))
        mainWindow.webContents.on('did-finish-load', function() {
            });

    }

}


function runAutoStage(repoId, filesArg, scriptId, scriptParamsArg) {
    logEverywhere("Running an automatic stage")
    var Client = require('svn-spawn');
    var shell = require('shelljs');
    const path = require('path');

    var appRootDir = require('app-root-dir').get().replace('app.asar','');
    var pathTemp = path.normalize(('C:\\Users\\matthews\\Documents\\Stansa\\electron-app\\AUTO-STAGE-FILES').replace('\\', path.sep));
    shell.mkdir('-p', pathTemp);
    logEverywhere(appRootDir);
    var client = new Client({
            cwd: pathTemp,
            username: 'Matthews',
            password: 'pwd'
        })
    //logEverywhere(argumentsStr);
    client.cmd(['co', 'svn://<ip-of-the-repository>/home/REPOS/repoId' + repoId, '.'], function(err, data) {
                    logEverywhere('err: %s', err);
                    logEverywhere("check out done!");

                    if (filesArg == '') {
                        logEverywhere('No files selected');
                        runVbaScript(pathTemp, '', scriptId);
                    } else {
                        logEverywhere(filesArg);
                        var files = filesArg.toString().split(',');
                        files.forEach(function(file){
                            logEverywhere(file);
                            runVbaScript(pathTemp, file, scriptId, scriptParamsArg);
                        });
                        }

                    commitAndCleanUp(repoId, pathTemp, scriptId);

                });

}



function runVbaScript(path, fileName, scriptId, scriptParamsArg) {
    var fs = require('fs');
    copySync('C:\\Users\\matthews\\Documents\\Stansa\\stansa-automate\\VBS\\script' + scriptId + '.vbs', path + '\\script' + scriptId + '.vbs', fs);
    logEverywhere('Copied over script file');

    const
        spawn = require( 'child_process' ).spawnSync,
        vbs = spawn( 'cscript.exe', [ path + '\\script' + scriptId + '.vbs', fileName, scriptParamsArg ] );
    logEverywhere( `Finished running the automatic stage` );
    logEverywhere( `status: ${vbs.status}` );
}




function commitAndCleanUp(repoId, pathTemp, scriptId) {
    logEverywhere('Commiting and cleaning up');
    var fs = require('fs');
    fs.unlinkSync(pathTemp + '\\script' + scriptId + '.vbs');

    var normalisedPath = '"' + pathTemp + '"';
    var spawn = require('child_process').spawn;
    var appRootDir = require('app-root-dir').get();
    var svnCommand = appRootDir.replace('app.asar','') + '\\bin\\svn.exe';

    var child = spawn(svnCommand, ['add', '--force', normalisedPath], { shell: true });
    child.stdout.pipe(process.stdout);
    child.stdout.on('data', function(data) {
        logEverywhere(data.toString());
    });

    child.on('close', function() {
        logEverywhere("Files added!");

        var child2 = spawn(svnCommand, ['commit', normalisedPath, '-m', '"AUTOMATIC STAGE ' + scriptId + '"'], { shell: true });
        child2.stdout.on('data', function(data) {
            logEverywhere(data.toString());
        });

        child2.on('close', function() {
            logEverywhere("Commit done!");

            deleteFolderRecursive(pathTemp);

            app.quit()
            return

        });
    })


    var deleteFolderRecursive = function(path) {
    if (fs.existsSync(path)) {
        fs.readdirSync(path).forEach(function(file, index){
          var curPath = path + "\\" + file;
          if (fs.lstatSync(curPath).isDirectory()) { // recurse
            deleteFolderRecursive(curPath);
          } else { // delete file
            fs.unlinkSync(curPath);
          }
        });
        fs.rmdirSync(path);
      }
    }

}

function copySync(src, dest, fs) {
  if (!fs.existsSync(src)) {
    return false;
  }

  var data = fs.readFileSync(src, 'utf-8');
  fs.writeFileSync(dest, data);
}
