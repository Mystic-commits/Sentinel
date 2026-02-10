#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tauri::Manager;

/// Backend process state
struct BackendProcess {
    child: Option<Child>,
}

/// Launch Python backend server
fn launch_backend() -> Result<Child, String> {
    println!("🚀 Launching FastAPI backend...");
    
    // Detect Python command (python3 on macOS/Linux, python on Windows)
    let python_cmd = if cfg!(target_os = "windows") {
        "python"
    } else {
        "python3"
    };
    
    // Get backend path (relative to current directory)
    let backend_path = if cfg!(debug_assertions) {
        // Development: relative to workspace
        "../../sentinel-core"
    } else {
        // Production: bundled with app
        "../sentinel-core"
    };
    
    println!("📂 Backend path: {}", backend_path);
    
    let child = Command::new(python_cmd)
        .args(&[
            "-m",
            "uvicorn",
            "sentinel_core.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "info",
        ])
        .current_dir(backend_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;
    
    println!("✅ Backend process started with PID: {}", child.id());
    Ok(child)
}

/// Health check the backend server
async fn wait_for_backend(max_attempts: u32) -> Result<(), String> {
    let client = reqwest::Client::new();
    let health_url = "http://localhost:8000/health";
    
    for i in 0..max_attempts {
        println!("🏥 Health check attempt {}/{}", i + 1, max_attempts);
        
        match client.get(health_url).send().await {
            Ok(response) if response.status().is_success() => {
                println!("✅ Backend is ready!");
                return Ok(());
            }
            Ok(response) => {
                println!("⚠️  Backend responded with status: {}", response.status());
            }
            Err(e) => {
                println!("⏳ Backend not ready yet: {}", e);
            }
        }
        
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    
    Err("Backend failed to start after maximum attempts".to_string())
}

/// Kill backend process
fn kill_backend(backend: &mut BackendProcess) {
    if let Some(mut child) = backend.child.take() {
        println!("🔪 Killing backend process (PID: {})...", child.id());
        
        match child.kill() {
            Ok(_) => {
                let _ = child.wait();
                println!("✅ Backend process terminated");
            }
            Err(e) => {
                eprintln!("❌ Failed to kill backend process: {}", e);
            }
        }
    }
}

fn main() {
    let backend = Arc::new(Mutex::new(BackendProcess { child: None }));
    
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_process::init())
        .setup(move |app| {
            let backend_clone = backend.clone();
            let _handle = app.handle().clone(); // Handle for future use if needed
            
            // Launch backend on startup
            tauri::async_runtime::spawn(async move {
                // Start backend
                match launch_backend() {
                    Ok(child) => {
                        backend_clone.lock().unwrap().child = Some(child);
                        
                        // Wait for backend to be ready
                        match wait_for_backend(30).await {
                            Ok(_) => {
                                println!("✅ Backend ready, UI should load now");
                            }
                            Err(e) => {
                                eprintln!("❌ Backend health check failed: {}", e);
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("❌ Failed to launch backend: {}", e);
                    }
                }
            });
            
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(move |_app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                // Kill backend on exit
                println!("🛑 Application exiting, cleaning up...");
                kill_backend(&mut backend.lock().unwrap());
            }
        });
}
