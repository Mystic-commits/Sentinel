#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::Serialize;
use std::{
    io::{BufRead, BufReader},
    process::{Child, Command, Stdio},
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};

#[derive(Clone, Serialize)]
struct Connection {
    port: u16,
    token: String,
}

#[derive(Default)]
struct Backend {
    child: Option<Child>,
    connection: Option<Result<Connection, String>>,
}

type SharedBackend = Arc<Mutex<Backend>>;

#[tauri::command]
fn desktop_connection(
    state: tauri::State<'_, SharedBackend>,
) -> Result<Option<Connection>, String> {
    state.lock().unwrap().connection.clone().transpose()
}

fn launch(state: &SharedBackend) -> Result<(), String> {
    let mut secret = [0u8; 32];
    getrandom::fill(&mut secret).map_err(|error| error.to_string())?;
    let token: String = secret.iter().map(|byte| format!("{byte:02x}")).collect();
    let filename = if cfg!(windows) {
        "sentinel-backend.exe"
    } else {
        "sentinel-backend"
    };
    let path = std::env::current_exe()
        .map_err(|error| error.to_string())?
        .with_file_name(filename);

    let mut command = Command::new(path);
    command
        .env("SENTINEL_ACCESS_TOKEN", &token)
        .env_remove("SENTINEL_ALLOWED_ORIGINS")
        .env_remove("SENTINEL_API_PREFIX")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit());
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }

    let mut backend = state.lock().unwrap();
    let mut child = command
        .spawn()
        .map_err(|error| format!("Could not start the bundled backend: {error}"))?;
    let output = child.stdout.take().expect("stdout pipe was requested");
    backend.child = Some(child);
    drop(backend);

    let mut lines = BufReader::new(output).lines();
    let ready = lines
        .next()
        .transpose()
        .map_err(|error| error.to_string())?;
    let port = ready
        .as_deref()
        .and_then(|line| line.strip_prefix("SENTINEL_READY "))
        .and_then(|port| port.parse::<u16>().ok())
        .filter(|port| *port > 0)
        .ok_or("The bundled backend exited before it reported readiness")?;
    state.lock().unwrap().connection = Some(Ok(Connection { port, token }));

    // Keep draining stdout for the lifetime of the child.
    for line in lines {
        if line.is_err() {
            break;
        }
    }
    state.lock().unwrap().connection = Some(Err("The bundled backend stopped".into()));
    Ok(())
}

fn stop(state: &SharedBackend) {
    let Some(mut child) = state.lock().unwrap().child.take() else {
        return;
    };
    // Closing stdin requests graceful shutdown, including for the frozen child.
    child.stdin.take();
    let deadline = Instant::now() + Duration::from_secs(3);
    while Instant::now() < deadline {
        if matches!(child.try_wait(), Ok(Some(_))) {
            return;
        }
        std::thread::sleep(Duration::from_millis(50));
    }
    let _ = child.kill();
    let _ = child.wait();
}

fn main() {
    let backend = SharedBackend::default();
    let startup = backend.clone();
    tauri::Builder::default()
        .manage(backend.clone())
        .invoke_handler(tauri::generate_handler![desktop_connection])
        .setup(move |_| {
            let startup = startup.clone();
            std::thread::spawn(move || {
                if let Err(error) = launch(&startup) {
                    startup.lock().unwrap().connection = Some(Err(error));
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("could not build Sentinel desktop")
        .run(move |_, event| {
            if matches!(event, tauri::RunEvent::Exit) {
                stop(&backend);
            }
        });
}
