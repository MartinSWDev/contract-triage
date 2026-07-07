// Contract Triage desktop app.
// Thin Rust shell: every command shells out to the project's Python API
// (`src/app_api.py`) via the project venv, so all analysis logic stays in one
// place. This is a local tool run from the repo checkout on the user's machine.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde_json::Value;
use std::path::PathBuf;
use std::process::Command;

/// Project root = <repo>/app/src-tauri -> up two levels -> <repo>.
fn project_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|p| p.parent())
        .expect("manifest dir has two ancestors")
        .to_path_buf()
}

fn python_bin() -> PathBuf {
    // Allow an override; otherwise use the project venv.
    if let Ok(p) = std::env::var("TRIAGE_PYTHON") {
        return PathBuf::from(p);
    }
    project_root().join(".venv/bin/python")
}

fn api_script() -> PathBuf {
    project_root().join("src/app_api.py")
}

fn run_api(args: &[&str]) -> Result<Value, String> {
    let output = Command::new(python_bin())
        .arg(api_script())
        .args(args)
        .current_dir(project_root())
        .output()
        .map_err(|e| format!("failed to launch python: {e}"))?;
    if !output.status.success() {
        return Err(format!(
            "python exited {}: {}",
            output.status,
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    serde_json::from_slice(&output.stdout).map_err(|e| {
        format!(
            "could not parse JSON ({e}): {}",
            String::from_utf8_lossy(&output.stdout)
        )
    })
}

#[tauri::command]
fn default_dir() -> String {
    project_root().join("samples").to_string_lossy().into_owned()
}

#[tauri::command]
fn list_contracts(dir: String) -> Result<Value, String> {
    run_api(&["list", &dir])
}

#[tauri::command]
fn run_contract(path: String) -> Result<Value, String> {
    run_api(&["run", &path])
}

#[tauri::command]
fn contract_detail(path: String) -> Result<Value, String> {
    run_api(&["detail", &path])
}

#[tauri::command]
fn run_eval() -> Result<Value, String> {
    run_api(&["eval"])
}

/// Open a file with the OS default handler (e.g. the redlined .docx in Word).
/// The path comes from our own backend, not user input.
#[tauri::command]
fn open_path(path: String) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    let mut cmd = {
        let mut c = Command::new("open");
        c.arg(&path);
        c
    };
    #[cfg(target_os = "linux")]
    let mut cmd = {
        let mut c = Command::new("xdg-open");
        c.arg(&path);
        c
    };
    #[cfg(target_os = "windows")]
    let mut cmd = {
        let mut c = Command::new("cmd");
        c.args(["/C", "start", "", &path]);
        c
    };
    cmd.spawn().map_err(|e| format!("could not open {path}: {e}"))?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            default_dir,
            list_contracts,
            run_contract,
            contract_detail,
            run_eval,
            open_path
        ])
        .run(tauri::generate_context!())
        .expect("error while running Contract Triage");
}
