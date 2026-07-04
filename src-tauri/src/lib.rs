use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::Manager;

struct BackendProcess(Mutex<Option<Child>>);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            start_backend(app);
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                if let Some(state) = window.app_handle().try_state::<BackendProcess>() {
                    if let Ok(mut guard) = state.0.lock() {
                        if let Some(mut child) = guard.take() {
                            let _ = child.kill();
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn start_backend(app: &tauri::App) {
    let repo_root = std::env::current_dir()
        .ok()
        .and_then(|cwd| {
            if cwd.ends_with("src-tauri") {
                cwd.parent().map(|p| p.to_path_buf())
            } else {
                Some(cwd)
            }
        })
        .unwrap_or_else(|| std::path::PathBuf::from("."));

    let backend_dir = repo_root.join("backend");
    let python = std::env::var("NOVELA_PYTHON").unwrap_or_else(|_| "python3".to_string());

    let child = Command::new(&python)
        .args([
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8742",
        ])
        .current_dir(&backend_dir)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();

    match child {
        Ok(c) => {
            app.manage(BackendProcess(Mutex::new(Some(c))));
        }
        Err(e) => {
            eprintln!("Failed to start Novela backend: {e}");
            eprintln!("Run manually: cd backend && uvicorn app.main:app --port 8742");
        }
    }
}
