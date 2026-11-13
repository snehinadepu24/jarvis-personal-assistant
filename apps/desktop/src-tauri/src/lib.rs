use tauri::{
    menu::{Menu, MenuItem},
    tray::{TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};

// Single implementation of close_orb (removes duplicate)
#[tauri::command]
fn close_orb(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("orb") {
        // Hide first, then close to ensure resources are released
        let _ = window.hide();
        window.close().map_err(|e| e.to_string())?
    }
    Ok(())
}

#[tauri::command]
fn toggle_orb(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("orb") {
        let is_visible = window.is_visible().map_err(|e| e.to_string())?;
        if is_visible {
            window.hide().map_err(|e| e.to_string())?;
        } else {
            window.show().map_err(|e| e.to_string())?;
            window.set_focus().map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}


#[tauri::command]
fn toggle_dashboard(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        let is_visible = window.is_visible().map_err(|e| e.to_string())?;
        if is_visible {
            window.hide().map_err(|e| e.to_string())?;
        } else {
            window.show().map_err(|e| e.to_string())?;
            window.set_focus().map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .setup(|app| {
            // Setup System Tray
            let toggle_orb_item = MenuItem::with_id(app, "toggle_orb", "Toggle Floating Orb", true, None::<&str>)?;
            let toggle_dash_item = MenuItem::with_id(app, "toggle_dash", "Open Dashboard", true, None::<&str>)?;
            let quit_item = MenuItem::with_id(app, "quit", "Quit JARVIS", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&toggle_orb_item, &toggle_dash_item, &quit_item])?;

            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "toggle_orb" => {
                        let _ = toggle_orb(app.clone());
                    }
                    "toggle_dash" => {
                        let _ = toggle_dashboard(app.clone());
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click { .. } = event {
                        let app = tray.app_handle();
                        let _ = toggle_dashboard(app.clone());
                    }
                })
                .build(app)?;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![toggle_orb, toggle_dashboard, close_orb])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

