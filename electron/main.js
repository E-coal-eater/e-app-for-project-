const { app, BrowserWindow, session } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let flaskProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });
  win.loadURL("http://127.0.0.1:5000");
  win.on("closed", () => {
    if (flaskProcess) flaskProcess.kill();
  });
}

app.whenReady().then(() => {

  // ▶ Start Flask backend
  flaskProcess = spawn("python", ["app.py"], {
    cwd: path.join(__dirname, ".."),
    shell: true
  });

  // Optional: log flask output
  flaskProcess.stdout.on("data", data => console.log(`Flask: ${data}`));
  flaskProcess.stderr.on("data", data => console.error(`Flask error: ${data}`));
  
  // Allow geolocation
  session.defaultSession.setPermissionRequestHandler(
      (webContents, permission, callback) => {
        if (permission === "geolocation") {
            callback(true); // ✅ allow
        } else {
            callback(false);
        }
      }
  );
  
  // Give Flask time to start
  setTimeout(createWindow, 2000);
});

app.on("window-all-closed", () => {
  if (flaskProcess) flaskProcess.kill();
  app.quit();
});