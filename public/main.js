const { app, BrowserWindow } = require('electron')

const path = require('path')
const isDev = require('electron-is-dev')

require('@electron/remote/main').initialize()

const PY_DIST_FOLDER = 'dist-python' // python distributable folder
const PY_SRC_FOLDER = 'backend' // path to the python source
const PY_MODULE = 'run_app.py' // the name of the main module

const isRunningInBundle = () => {
  return require('fs').existsSync(path.join(__dirname, PY_DIST_FOLDER))
}

const getPythonScriptPath = () => {
  if (!isRunningInBundle()) {
    // console.log(isRunningInBundle())
    console.log(path.join(__dirname, PY_SRC_FOLDER, PY_MODULE))
    return path.join(__dirname, PY_SRC_FOLDER, PY_MODULE)
  }
  if (process.platform === 'win32') {
    console.log("jjfhgdf",path.join(__dirname, PY_DIST_FOLDER, PY_MODULE.slice(0, -3) + '.exe'))
    // alert("asdfasd")
    return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE.slice(0, -3) + '.exe')
  }
  console.log(path.join(__dirname, PY_DIST_FOLDER, PY_MODULE))
  return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE)
}

const startPythonSubprocess = () => {
  let script = getPythonScriptPath()
  console.log(script)
  if (isRunningInBundle()) {
    subpy = require('child_process').execFile(script, [],{ detached: true, shell: true, stdio: 'inherit' })
  } else {
    const { spawn } = require('child_process')
    const pythonProcess = spawn('python', [script],{ detached: true, shell: true, stdio: 'inherit' })

    pythonProcess.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`)
    })
    // subpy = require('child_process').spawn(`python ${script}`, { detached: true, shell: true, stdio: 'inherit' })
  }
  // if (subpy != null) {
  //   console.log('child process success on port ')
  // }
}

const killPythonSubprocesses = main_pid => {
  const python_script_name = path.basename(getPythonScriptPath())
  let cleanup_completed = false
  const psTree = require('ps-tree')
  psTree(main_pid, function (err, children) {
    let python_pids = children
      .filter(function (el) {
        return el.COMMAND == python_script_name
      })
      .map(function (p) {
        return p.PID
      })
    // kill all the spawned python processes
    python_pids.forEach(function (pid) {
      process.kill(pid)
    })
    subpy = null
    cleanup_completed = true
  })
  return new Promise(function (resolve, reject) {
    ;(function waitForSubProcessCleanup() {
      if (cleanup_completed) return resolve()
      setTimeout(waitForSubProcessCleanup, 30)
    })()
  })
}

function createWindow() {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
      enableRemoteModule: true
    }
  })

  win.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  )
}

app.on('ready', function () {
  createWindow()
  startPythonSubprocess()

})

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== "darwin") {
    // let main_process_pid = process.pid;
    killPythonSubprocesses(main_process_pid).then(() => {
      app.quit();
    });
  }
})

app.on('activate', function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0){
    createWindow()
    startPythonSubprocess()
  } 
})

// const { app, BrowserWindow } = require('electron')
// const path = require('path')
// const isDev = require('electron-is-dev')

// require('@electron/remote/main').initialize()

// const PY_SRC_FOLDER = 'backend' // path to the python source
// const PY_MODULE = 'run_app.py' // the name of the main module

// const getPythonScriptPath = () => {
//   return path.join(__dirname, PY_SRC_FOLDER, PY_MODULE)
// }

// const startPythonSubprocess = () => {
//   const script = getPythonScriptPath()
//   const { spawn } = require('child_process')
//   const pythonProcess = spawn('python', [script])

//   pythonProcess.stdout.on('data', (data) => {
//     console.log(`stdout: ${data}`)
//   })

//   pythonProcess.stderr.on('data', (data) => {
//     console.error(`stderr: ${data}`)
//   })

//   pythonProcess.on('close', (code) => {
//     console.log(`child process exited with code ${code}`)
//   })
// }

// function createWindow() {
//   // Create the browser window.
//   const win = new BrowserWindow({
//     width: 800,
//     height: 600,
//     webPreferences: {
//       contextIsolation: false,
//       nodeIntegration: true,
//       enableRemoteModule: true
//     }
//   })

//   win.loadURL(
//     isDev
//       ? 'http://localhost:3000'
//       : `file://${path.join(__dirname, '../build/index.html')}`
//   )
// }

// app.on('ready', function () {
//   createWindow()
//   startPythonSubprocess()
// })

// // Quit when all windows are closed.
// app.on('window-all-closed', function () {
//   if (process.platform !== "darwin") {
//     app.quit()
//   }
// })

// app.on('activate', function () {
//   if (BrowserWindow.getAllWindows().length === 0) createWindow()
// })
