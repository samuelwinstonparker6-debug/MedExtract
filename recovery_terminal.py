import tkinter as tk
import random
import json
import os

SETTINGS_FILE = "terminal_settings.json"

class RecoveryTerminal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Data Recovery Console")
        self.geometry("950x700")
        
        # Available curated visual themes
        self.themes = [
            {"name": "Matrix Green", "fg": "#39FF14", "bg": "#020A02", "accent": "#00FF00"},
            {"name": "Amber Alert", "fg": "#FFB000", "bg": "#0D0700", "accent": "#FFA500"},
            {"name": "Cyberpunk Cyan", "fg": "#00E5FF", "bg": "#080F19", "accent": "#0099FF"},
            {"name": "Classic Terminal", "fg": "#E5E5E5", "bg": "#121212", "accent": "#FFFFFF"},
            {"name": "Vaporwave Purple", "fg": "#BD93F9", "bg": "#120E1A", "accent": "#FF79C6"},
            {"name": "Tactical Red", "fg": "#FF3333", "bg": "#0F0202", "accent": "#FF5555"}
        ]
        self.theme_index = 0
        
        # Font families to cycle through
        self.fonts = ["Consolas", "Courier New", "Lucida Console", "MS Gothic"]
        self.font_index = 0
        self.font_size = 13
        
        # Speed levels: normal delay (ms per char)
        self.speeds = [25, 10, 0, 50] # 0 means instant
        self.speed_index = 0
        
        self.fullscreen_state = False
        
        # Load user settings if they exist
        self.load_settings()
        
        # Apply window theme and layout
        self.configure(bg=self.current_theme()["bg"])
        
        # Top Header Bar
        self.top_bar = tk.Frame(self, bg=self.current_theme()["bg"])
        self.top_bar.pack(fill=tk.X, side=tk.TOP, pady=5)
        
        self.header_left = tk.Label(
            self.top_bar,
            text="DF-RECOVERY-OS v2.4.1 // SECURE DECRYPTOR // SAMUEL_PARKER_HDD",
            fg=self.current_theme()["accent"],
            bg=self.current_theme()["bg"],
            font=(self.current_font(), 10, "bold")
        )
        self.header_left.pack(side=tk.LEFT, padx=15)
        
        # Main Display text widget
        self.text_area = tk.Text(
            self,
            bg=self.current_theme()["bg"],
            fg=self.current_theme()["fg"],
            insertbackground=self.current_theme()["fg"],
            font=(self.current_font(), self.font_size),
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=20,
            wrap=tk.WORD
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<Key>", lambda e: "break") # Block typing
        
        # Tag styling for highlighting recovery reports
        self.setup_tags()
        
        # Bottom HUD / Help panel
        self.bottom_bar = tk.Frame(self, bg=self.current_theme()["bg"])
        self.bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        self.help_label = tk.Label(
            self.bottom_bar,
            text="[F1: Theme]  [F2: Font Family]  [F3: Size+]  [F4: Size-]  [F5: Restart]  [F6: Typing Speed]  [F11: Fullscreen]  [Esc: Exit]",
            fg=self.dim_color(self.current_theme()["fg"]),
            bg=self.current_theme()["bg"],
            font=(self.current_font(), 9)
        )
        self.help_label.pack(side=tk.LEFT, padx=15)
        
        # Keyboard binds
        self.bind("<F1>", self.next_theme)
        self.bind("<F2>", self.next_font)
        self.bind("<F3>", self.increase_font)
        self.bind("<F4>", self.decrease_font)
        self.bind("<F5>", self.restart_recovery)
        self.bind("<F6>", self.next_speed)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", lambda e: self.destroy())
        
        # State for cursor blink
        self.blink_after_id = None
        self.blink_state = False
        
        # Run sequence
        self.start_recovery()

    # Core Settings functions
    def current_theme(self):
        return self.themes[self.theme_index]
        
    def current_font(self):
        return self.fonts[self.font_index]

    def current_speed_delay(self):
        return self.speeds[self.speed_index]

    def setup_tags(self):
        theme = self.current_theme()
        # Clean existing tags
        for tag in ["normal", "success", "info", "warn", "bold_report"]:
            self.text_area.tag_config(tag, foreground=theme["fg"])
            
        self.text_area.tag_config("success", foreground=theme["accent"], font=(self.current_font(), self.font_size, "bold"))
        self.text_area.tag_config("info", foreground=theme["fg"])
        self.text_area.tag_config("warn", foreground="#FF3333")
        self.text_area.tag_config("bold_report", foreground=theme["accent"], font=(self.current_font(), self.font_size, "bold"))

    def dim_color(self, hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"#{int(r*0.5):02x}{int(g*0.5):02x}{int(b*0.5):02x}"

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    self.theme_index = settings.get("theme_index", 0) % len(self.themes)
                    self.font_index = settings.get("font_index", 0) % len(self.fonts)
                    self.font_size = settings.get("font_size", 13)
                    self.speed_index = settings.get("speed_index", 0) % len(self.speeds)
            except Exception:
                pass # Fallback to defaults

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({
                    "theme_index": self.theme_index,
                    "font_index": self.font_index,
                    "font_size": self.font_size,
                    "speed_index": self.speed_index
                }, f)
        except Exception:
            pass

    def apply_appearance(self):
        theme = self.current_theme()
        font_name = self.current_font()
        
        self.configure(bg=theme["bg"])
        self.top_bar.configure(bg=theme["bg"])
        self.bottom_bar.configure(bg=theme["bg"])
        
        self.header_left.configure(fg=theme["accent"], bg=theme["bg"], font=(font_name, 10, "bold"))
        
        self.text_area.configure(
            bg=theme["bg"],
            fg=theme["fg"],
            insertbackground=theme["fg"],
            font=(font_name, self.font_size)
        )
        
        self.help_label.configure(
            fg=self.dim_color(theme["fg"]),
            bg=theme["bg"],
            font=(font_name, 9)
        )
        
        self.setup_tags()
        self.save_settings()

    # User Input Binds
    def next_theme(self, event=None):
        self.theme_index = (self.theme_index + 1) % len(self.themes)
        self.apply_appearance()
        
    def next_font(self, event=None):
        self.font_index = (self.font_index + 1) % len(self.fonts)
        self.apply_appearance()
        
    def increase_font(self, event=None):
        if self.font_size < 32:
            self.font_size += 1
            self.apply_appearance()
            
    def decrease_font(self, event=None):
        if self.font_size > 8:
            self.font_size -= 1
            self.apply_appearance()

    def next_speed(self, event=None):
        self.speed_index = (self.speed_index + 1) % len(self.speeds)
        self.apply_appearance()
        # Show brief speed alert in title
        speeds_names = ["Normal", "Fast", "Instant", "Slow"]
        self.header_left.configure(text=f"DF-RECOVERY-OS // SPEED SET TO: {speeds_names[self.speed_index].upper()}")
        self.after(1500, lambda: self.header_left.configure(text="DF-RECOVERY-OS v2.4.1 // SECURE DECRYPTOR // SAMUEL_PARKER_HDD"))
        self.save_settings()

    def toggle_fullscreen(self, event=None):
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)

    # Recovery Simulation Logic
    def start_recovery(self):
        # Cancel any active timers/blinking
        if self.blink_after_id:
            self.after_cancel(self.blink_after_id)
            self.blink_after_id = None
            
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.configure(state=tk.DISABLED)
        
        self.step_index = 0
        self.run_next_step()

    def run_next_step(self):
        steps = [
            self.show_boot_sequence,
            self.show_connection,
            self.show_progress_scan,
            self.show_decryption,
            self.show_final_report
        ]
        if self.step_index < len(steps):
            current_step = steps[self.step_index]
            self.step_index += 1
            current_step()

    def write_line(self, line_text, tag="normal", instant=False, callback=None):
        delay = self.current_speed_delay()
        if instant or delay == 0:
            self.text_area.configure(state=tk.NORMAL)
            self.text_area.insert(tk.END, line_text + "\n", tag)
            self.text_area.see(tk.END)
            self.text_area.configure(state=tk.DISABLED)
            if callback:
                callback()
            return

        def type_char(idx=0):
            if idx < len(line_text):
                self.text_area.configure(state=tk.NORMAL)
                self.text_area.insert(tk.END, line_text[idx], tag)
                self.text_area.see(tk.END)
                self.text_area.configure(state=tk.DISABLED)
                self.after(delay, lambda: type_char(idx + 1))
            else:
                self.text_area.configure(state=tk.NORMAL)
                self.text_area.insert(tk.END, "\n", tag)
                self.text_area.configure(state=tk.DISABLED)
                if callback:
                    callback()
        type_char()

    # Step Definitions
    def show_boot_sequence(self):
        lines = [
            "DF-RECOVERY-OS BOOT SYSTEM CORE v2.4.1",
            "INITIALIZING DECRYPTION ALGORITHMS... OK",
            "ESTABLISHING COMPORT CONNECTION... OK",
            "BYPASSING STORAGE DRIVE CONTROLLER FIRMWARE LOCK... DONE",
            "Targeting Device: Dell Inspiron 15 3593 (SSD 256GB)",
            "Preparing File Carving Engine (NTFS / GPT Signature Tables)..."
        ]
        
        def display_lines(idx=0):
            if idx < len(lines):
                self.write_line(lines[idx], "info", callback=lambda: display_lines(idx + 1))
            else:
                self.after(400, self.run_next_step)
        display_lines()

    def show_connection(self):
        self.write_line("\n[STATUS] SECURING CONNECTION TO DIRECT DATA REGISTERS...", "info")
        self.write_line("[WARN] BLOCK CORRUPTION DETECTED. ATTEMPTING RAW PHYSICAL BYPASS...", "warn")
        self.write_line("[STATUS] Connection Secured. Running raw block scan.\n", "success", callback=self.run_next_step)

    def show_progress_scan(self, percent=0):
        if self.current_speed_delay() == 0:
            # Instant completion
            self.write_line("[PROGRESS] Scanning Sectors: [██████████████████████████████] 100% (500,118,192 sectors)", "success")
            self.after(300, self.run_next_step)
            return

        bar_len = 30
        filled = int(percent / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        self.text_area.configure(state=tk.NORMAL)
        if percent > 0:
            # Delete the previous scanning progress line
            self.text_area.delete("insert -1c linestart", "insert")
            
        hex_addr = f"0x{random.randint(0x10000000, 0xFFFFFFFF):08X}"
        progress_text = f"Scanning: {hex_addr} [{bar}] {percent}%"
        self.text_area.insert(tk.END, progress_text + "\n", "info")
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)
        
        if percent < 100:
            # Decide step size
            step = 2 if percent < 80 else 1
            delay = random.randint(15, 60)
            self.after(delay, lambda: self.show_progress_scan(percent + step))
        else:
            self.after(200, self.run_next_step)

    def show_decryption(self):
        lines = [
            "\n[CARVER] Recovering file markers...",
            "[CARVER] Match: GPT Master Boot Record (MBR)",
            "[CARVER] Match: NTFS Master File Table ($MFT)",
            "[CARVER] Extracting file streams directly from flash cells...",
            "[INTEGRITY] Performing MD5 validation on recovered streams..."
        ]
        
        def display_lines(idx=0):
            if idx < len(lines):
                self.write_line(lines[idx], "info", callback=lambda: display_lines(idx + 1))
            else:
                self.after(400, self.run_next_step)
        display_lines()

    def show_final_report(self):
        report = (
            "\n"
            "======================================================================\n"
            "SSD Data Recovery (Dell Inspiron 15 3593)\n"
            "======================================================================\n\n"
            "Digital Forensics Recovery Started:  (8/10/2026) 13:01:99 Hrs\n"
            "Status                            :  Success\n"
            "Total recovered files             :  35000\n"
            "Time Elapsed                      :  3:20:45 Hrs\n\n"
            "Data Recovered                    :  234 Gigs\n"
            "Hash \n"
            "MD5                               :  ae1382b61f8221b204e9800998ecf842\n\n"
            "----------------------------------------------------------------------\n"
            "----------------------------------------------------------------------\n\n"
            "User    : Samuel Parker\n"
            "Password: *********\n\n\n"
            "Welcome back, Samuel\n"
            "======================================================================"
        )
        
        # Speed up typewriter slightly for the big final report block
        orig_delay = self.current_speed_delay()
        adjusted_delay = max(5, int(orig_delay * 0.4)) if orig_delay != 0 else 0
        
        if adjusted_delay == 0:
            self.text_area.configure(state=tk.NORMAL)
            self.text_area.insert(tk.END, report, "bold_report")
            self.text_area.see(tk.END)
            self.text_area.configure(state=tk.DISABLED)
            self.start_blinking()
            return

        def type_char(idx=0):
            if idx < len(report):
                self.text_area.configure(state=tk.NORMAL)
                self.text_area.insert(tk.END, report[idx], "bold_report")
                self.text_area.see(tk.END)
                self.text_area.configure(state=tk.DISABLED)
                self.after(adjusted_delay, lambda: type_char(idx + 1))
            else:
                self.start_blinking()
        type_char()

    # Bouncing terminal cursor effect at the end of execution
    def start_blinking(self):
        self.blink_state = False
        self.toggle_blink()

    def toggle_blink(self):
        self.text_area.configure(state=tk.NORMAL)
        text_content = self.text_area.get("1.0", "end - 1c")
        
        if text_content.endswith("█"):
            # Delete last character
            self.text_area.delete("end - 2c", "end - 1c")
        else:
            # Append cursor
            self.text_area.insert(tk.END, "█")
            
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)
        self.blink_after_id = self.after(500, self.toggle_blink)

    def restart_recovery(self, event=None):
        self.start_recovery()

if __name__ == "__main__":
    app = RecoveryTerminal()
    app.mainloop()
