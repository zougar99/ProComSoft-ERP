"""
Theme Manager - LaserFlow
Manages dark/light theme switching
"""

from pathlib import Path
import json


class ThemeManager:
    """Manages application theme"""
    
    def __init__(self):
        self.config_path = Path("app_config.json")
        self.theme_dir = Path("ui")
        self._load_config()
    
    def _load_config(self):
        """Load theme configuration"""
        self.current_theme = "dark"
        
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme_mode", "dark")
            except:
                pass
    
    def _save_config(self):
        """Save theme configuration"""
        config = {}
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                pass
        
        config["theme_mode"] = self.current_theme
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def is_dark(self) -> bool:
        """Check if current theme is dark"""
        return self.current_theme == "dark"
    
    def toggle_theme(self) -> str:
        """Toggle between dark and light theme"""
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        
        self._save_config()
        return self.current_theme
    
    def load_theme(self) -> str:
        """Load theme QSS content"""
        # Always use design_system.qss as base
        design_system = self.theme_dir / "design_system.qss"
        
        if design_system.exists():
            try:
                with open(design_system, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace CSS variables with actual colors based on theme
                # Qt/QSS doesn't fully support CSS variables, so we replace them
                if self.current_theme == "dark":
                    # Dark theme color mappings
                    replacements = [
                        ("var(--bg-primary)", "#111827"),
                        ("var(--bg-surface)", "#1F2937"),
                        ("var(--bg-hover)", "#374151"),
                        ("var(--border-default)", "#374151"),
                        ("var(--border-focus)", "#3B82F6"),
                        ("var(--text-primary)", "#F9FAFB"),
                        ("var(--text-secondary)", "#D1D5DB"),
                        ("var(--text-muted)", "#9CA3AF"),
                        ("var(--accent-primary)", "#3B82F6"),
                        ("var(--accent-hover)", "#2563EB"),
                        ("var(--accent-pressed)", "#1E40AF"),
                        ("var(--status-success)", "#16A34A"),
                        ("var(--status-warning)", "#F59E0B"),
                        ("var(--status-error)", "#DC2626"),
                        ("var(--status-info)", "#0EA5E9"),
                        ("var(--topbar-bg)", "#1F2937"),
                        ("var(--topbar-border)", "#374151"),
                        ("var(--sidebar-bg)", "#111827"),
                        ("var(--sidebar-text)", "#F9FAFB"),
                        ("var(--sidebar-hover)", "#374151"),
                        ("var(--sidebar-active)", "#3B82F6"),
                    ]
                    for old, new in replacements:
                        content = content.replace(old, new)
                else:
                    # Light theme color mappings (default)
                    replacements = [
                        ("var(--bg-primary)", "#F5F6F8"),
                        ("var(--bg-surface)", "#FFFFFF"),
                        ("var(--bg-hover)", "#F3F4F6"),
                        ("var(--border-default)", "#E6E8EC"),
                        ("var(--border-focus)", "#2563EB"),
                        ("var(--text-primary)", "#1F2937"),
                        ("var(--text-secondary)", "#6B7280"),
                        ("var(--text-muted)", "#9CA3AF"),
                        ("var(--accent-primary)", "#2563EB"),
                        ("var(--accent-hover)", "#1D4ED8"),
                        ("var(--accent-pressed)", "#1E40AF"),
                        ("var(--status-success)", "#16A34A"),
                        ("var(--status-warning)", "#F59E0B"),
                        ("var(--status-error)", "#DC2626"),
                        ("var(--status-info)", "#0EA5E9"),
                        ("var(--topbar-bg)", "#FFFFFF"),
                        ("var(--topbar-border)", "#E6E8EC"),
                        ("var(--sidebar-bg)", "#1F2937"),
                        ("var(--sidebar-text)", "#F9FAFB"),
                        ("var(--sidebar-hover)", "#374151"),
                        ("var(--sidebar-active)", "#2563EB"),
                    ]
                    for old, new in replacements:
                        content = content.replace(old, new)
                
                return content
            except Exception as e:
                print(f"Error loading design_system.qss: {e}")
                import traceback
                traceback.print_exc()
                pass
        
        # Try professional theme
        professional_theme = self.theme_dir / "theme_professional.qss"
        if professional_theme.exists():
            try:
                with open(professional_theme, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                pass
        
        # Fallback to regular themes
        theme_file = "theme.qss"
        if self.current_theme == "light":
            theme_file = "theme_light.qss"
        
        theme_path = self.theme_dir / theme_file
        
        if theme_path.exists():
            try:
                with open(theme_path, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                pass
        
        # Return default professional theme if file not found
        return """
        QWidget {
            background-color: #f0f4f8;
            color: #2c3e50;
            font-family: "Segoe UI", "Arial", sans-serif;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton#Primary {
            background-color: #27ae60;
        }
        QPushButton#Primary:hover {
            background-color: #229954;
        }
        QLabel {
            color: #2c3e50;
        }
        QLabel#PageTitle {
            font-size: 24pt;
            font-weight: 700;
        }
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #bdc3c7;
        }
        QHeaderView::section {
            background-color: #34495e;
            color: #ffffff;
            font-weight: 600;
        }
        """
