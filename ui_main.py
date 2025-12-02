import wx
import os
import threading
import ctypes

import config
from indexer import FileIndexer
from search_engine import SearchEngine

try:
    myappid = 'parallax.filefinder.hackathon.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Local File Searcher", size=(900, 700))
        self.SetBackgroundColour(config.THEME["bg"])
        
        if os.path.exists("HthonLogo.PNG"):
            try:
                icon = wx.Icon("HthonLogo.PNG", wx.BITMAP_TYPE_ANY)
                self.SetIcon(icon)
            except Exception:
                pass

        self.indexer = FileIndexer()
        self.search_engine = SearchEngine()
        self.indexed_files = []
        
        self.init_ui()
        self.Center()

    def init_ui(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(config.THEME["bg"])
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl_title = wx.StaticText(panel, label="FILE FINDER")
        lbl_title.SetFont(wx.Font(42, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, config.FONT_FAMILY))
        lbl_title.SetForegroundColour(config.THEME["text"])
        content_sizer.Add(lbl_title, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=10)
        
        lbl_sub = wx.StaticText(panel, label="AI-Assisted Local Search (Parallax Powered)")
        lbl_sub.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        lbl_sub.SetForegroundColour(config.THEME["text_dim"])
        content_sizer.Add(lbl_sub, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=40)
        
        self.txt_root_path = wx.TextCtrl(panel, value=os.getcwd(), size=(600, 40), style=wx.BORDER_SIMPLE)
        self.txt_root_path.SetBackgroundColour(config.THEME["panel_bg"])
        self.txt_root_path.SetForegroundColour(config.THEME["text"])
        self.txt_root_path.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        content_sizer.Add(self.txt_root_path, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_browse = wx.Button(panel, label="BROWSE", size=(100, 36))
        self.btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
        btn_sizer.Add(self.btn_browse, flag=wx.RIGHT, border=8)
        
        self.btn_index = wx.Button(panel, label="INDEX", size=(100, 36))
        self.btn_index.SetToolTip("Scan the selected folder for files")
        self.btn_index.Bind(wx.EVT_BUTTON, self.on_index)
        btn_sizer.Add(self.btn_index, flag=wx.RIGHT, border=8)
        
        self.btn_save = wx.Button(panel, label="SAVE INDEX", size=(110, 36))
        self.btn_save.SetToolTip("Save the current file index to a JSON file")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_index)
        btn_sizer.Add(self.btn_save, flag=wx.RIGHT, border=8)
        
        self.btn_load = wx.Button(panel, label="LOAD INDEX", size=(110, 36))
        self.btn_load.SetToolTip("Load a previously saved file index")
        self.btn_load.Bind(wx.EVT_BUTTON, self.on_load_index)
        btn_sizer.Add(self.btn_load)
        
        content_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=30)
        
        self.txt_search = wx.TextCtrl(panel, size=(600, 45), style=wx.TE_PROCESS_ENTER|wx.BORDER_SIMPLE)
        self.txt_search.SetBackgroundColour(config.THEME["panel_bg"])
        self.txt_search.SetForegroundColour(config.THEME["text"])
        self.txt_search.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        self.txt_search.SetHint("Type your search query...")
        self.txt_search.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        content_sizer.Add(self.txt_search, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        search_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_hybrid = wx.Button(panel, label="Hybrid Search (Fast)", size=(295, 40))
        self.btn_hybrid.SetToolTip("Semantic search + AI (Faster, saves tokens)")
        self.btn_hybrid.Bind(wx.EVT_BUTTON, self.on_hybrid_search)
        search_btn_sizer.Add(self.btn_hybrid, flag=wx.RIGHT, border=10)
        
        self.btn_full = wx.Button(panel, label="Full AI Search (Slow)", size=(295, 40))
        self.btn_full.SetToolTip("Send ALL files to AI (Slower, comprehensive)")
        self.btn_full.Bind(wx.EVT_BUTTON, self.on_full_ai_search)
        search_btn_sizer.Add(self.btn_full)
        
        content_sizer.Add(search_btn_sizer, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        # Activity log section - moved here from bottom
        lbl_activity = wx.StaticText(panel, label="Activity Log")
        lbl_activity.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, config.FONT_FAMILY))
        lbl_activity.SetForegroundColour(config.THEME["text_dim"])
        content_sizer.Add(lbl_activity, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=5)
        
        self.txt_log = wx.TextCtrl(panel, size=(600, 80), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_SIMPLE)
        self.txt_log.SetBackgroundColour(config.THEME["panel_bg"])
        self.txt_log.SetForegroundColour(config.THEME["text_dim"])
        self.txt_log.SetFont(wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas"))
        content_sizer.Add(self.txt_log, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        self.scrolled_window = wx.ScrolledWindow(panel, size=(600, 220), style=wx.VSCROLL|wx.BORDER_NONE)
        self.scrolled_window.SetScrollRate(5, 5)
        self.scrolled_window.SetBackgroundColour(config.THEME["bg"])
        self.results_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.results_sizer)
        content_sizer.Add(self.scrolled_window, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        self.lbl_status = wx.StaticText(panel, label="Ready")
        self.lbl_status.SetForegroundColour(config.THEME["text_dim"])
        self.lbl_status.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        content_sizer.Add(self.lbl_status, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=5)

        self.gauge = wx.Gauge(panel, range=100, size=(600, 4), style=wx.GA_SMOOTH)
        self.gauge.SetBackgroundColour(config.THEME["panel_bg"])
        content_sizer.Add(self.gauge, flag=wx.ALIGN_CENTER)
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        
        self.log("Application started - Ready to index files")
        
        main_sizer.Add(content_sizer, flag=wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        
        panel.SetSizer(main_sizer)

    def on_timer(self, event):
        self.gauge.Pulse()

    def log(self, message):
        """Add a timestamped log entry to the activity log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.txt_log.AppendText(log_entry)

    def on_browse(self, event):
        dlg = wx.DirDialog(self, "Choose directory", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.txt_root_path.SetValue(path)
            self.log(f"Selected directory: {path}")
        dlg.Destroy()

    def on_index(self, event):
        root = self.txt_root_path.GetValue().strip()
        if not root or not os.path.isdir(root):
            self.log(f"ERROR: Invalid folder path: {root}")
            wx.MessageBox("Invalid folder.", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.log(f"Starting indexing process for: {root}")
        self.lbl_status.SetLabel("Indexing files...")
        self.btn_index.Disable()
        self.timer.Start(100)
        threading.Thread(target=self._indexing_worker, args=(root,), daemon=True).start()

    def _indexing_worker(self, root):
        self.indexer.set_root_path(root)
        files = self.indexer.index_files(progress_callback=lambda msg: wx.CallAfter(self.lbl_status.SetLabel, msg))
        self.indexed_files = files
        wx.CallAfter(self._indexing_finished, len(files))

    def _indexing_finished(self, count):
        self.timer.Stop()
        self.gauge.SetValue(0)
        self.btn_index.Enable()
        self.lbl_status.SetLabel(f"Indexed {count} files. Ready.")
        self.log(f"Indexing complete: {count} files indexed")

    def on_save_index(self, event):
        if not self.indexed_files:
            self.log("No index to save")
            wx.MessageBox("No index to save.", "Info", wx.OK)
            return
        dlg = wx.FileDialog(self, "Save Index", wildcard="JSON (*.json)|*.json", style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            try:
                self.indexer.save_index(filepath)
                self.lbl_status.SetLabel("Index saved successfully.")
                self.log(f"Index saved to: {filepath}")
                wx.MessageBox("Index saved successfully.", "Success", wx.OK)
            except Exception as e:
                self.log(f"ERROR saving index: {e}")
                wx.MessageBox(f"Error: {e}", "Error", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()

    def on_load_index(self, event):
        dlg = wx.FileDialog(self, "Load Index", wildcard="JSON (*.json)|*.json", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            try:
                files = self.indexer.load_index(filepath)
                self.indexed_files = files
                self.lbl_status.SetLabel(f"Successfully loaded {len(files)} files.")
                self.log(f"Loaded index from: {filepath} ({len(files)} files)")
                wx.MessageBox(f"Successfully loaded {len(files)} files from index.", "Success", wx.OK)
            except Exception as e:
                self.log(f"ERROR loading index: {e}")
                wx.MessageBox(f"Error: {e}", "Error", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()

    def on_search(self, event):
        # Default to hybrid if enter is pressed
        self.on_hybrid_search(event)

    def on_hybrid_search(self, event):
        self._initiate_search("hybrid")

    def on_full_ai_search(self, event):
        self._initiate_search("full")

    def _initiate_search(self, mode):
        if not self.indexed_files:
            self.log("Cannot search: No files indexed")
            wx.MessageBox("Please index or load files first.", "Info", wx.OK)
            return
        
        query = self.txt_search.GetValue().strip()
        if not query:
            return

        mode_desc = "Hybrid (Semantic + AI)" if mode == "hybrid" else "Full AI"
        self.log(f"Starting {mode_desc} search for: '{query}'")
        
        self.results_sizer.Clear(True)
        
        msg = "Running hybrid semantic + AI search (fast mode)..." if mode == "hybrid" else "Running full AI search (slow mode, all files)..."
        self.lbl_status.SetLabel(msg)
        
        self.btn_hybrid.Disable()
        self.btn_full.Disable()
        self.timer.Start(100)
        
        threading.Thread(target=self._search_worker, args=(query, mode), daemon=True).start()

    def _search_worker(self, query, mode):
        try:
            results, reasoning = self.search_engine.search(query, self.indexed_files, mode=mode)
            wx.CallAfter(self._search_finished, results, reasoning)
        except Exception as e:
            wx.CallAfter(self._search_error, str(e))

    def _search_finished(self, results, reasoning):
        self.timer.Stop()
        self.gauge.SetValue(0)
        self.btn_hybrid.Enable()
        self.btn_full.Enable()
        self.lbl_status.SetLabel(f"Found {len(results)} matches.")
        self.log(f"Search complete: {len(results)} matches found")
        
        self.scrolled_window.Freeze()
        
        if reasoning:
            reasoning_panel = wx.Panel(self.scrolled_window)
            reasoning_panel.SetBackgroundColour(config.THEME["panel_bg"])
            r_sizer = wx.BoxSizer(wx.VERTICAL)
            
            lbl_reasoning_title = wx.StaticText(reasoning_panel, label="AI Reasoning:")
            lbl_reasoning_title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, config.FONT_FAMILY))
            lbl_reasoning_title.SetForegroundColour(config.THEME["accent"])
            r_sizer.Add(lbl_reasoning_title, flag=wx.LEFT|wx.TOP|wx.RIGHT, border=10)
            
            lbl_reasoning = wx.StaticText(reasoning_panel, label=reasoning)
            lbl_reasoning.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
            lbl_reasoning.SetForegroundColour(config.THEME["text"])
            lbl_reasoning.Wrap(560)
            r_sizer.Add(lbl_reasoning, flag=wx.ALL, border=10)
            
            reasoning_panel.SetSizer(r_sizer)
            self.results_sizer.Add(reasoning_panel, flag=wx.EXPAND|wx.BOTTOM, border=10)

        for i, res in enumerate(results):
            result_panel = wx.Panel(self.scrolled_window)
            result_panel.SetBackgroundColour(config.THEME["panel_bg"])
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            lbl_name = wx.StaticText(result_panel, label=f"#{i+1}  {res.file.name}")
            lbl_name.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, config.FONT_FAMILY))
            lbl_name.SetForegroundColour(config.THEME["text"])
            sizer.Add(lbl_name, flag=wx.LEFT|wx.TOP|wx.RIGHT, border=10)
            
            lbl_path = wx.StaticText(result_panel, label=res.file.path)
            lbl_path.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
            lbl_path.SetForegroundColour(config.THEME["text_dim"])
            sizer.Add(lbl_path, flag=wx.LEFT|wx.RIGHT, border=10)
            
            preview_text = res.file.preview[:150] + "..." if len(res.file.preview) > 150 else res.file.preview
            lbl_preview = wx.StaticText(result_panel, label=preview_text)
            lbl_preview.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
            lbl_preview.SetForegroundColour(config.THEME["text_dim"])
            sizer.Add(lbl_preview, flag=wx.ALL, border=10)
            
            result_panel.SetSizer(sizer)
            self.results_sizer.Add(result_panel, flag=wx.EXPAND|wx.BOTTOM, border=5)
        
        self.scrolled_window.Layout()
        self.scrolled_window.FitInside()
        self.scrolled_window.Thaw()

    def _search_error(self, error_msg):
        self.timer.Stop()
        self.gauge.SetValue(0)
        self.btn_hybrid.Enable()
        self.btn_full.Enable()
        self.lbl_status.SetLabel("Search failed.")
        self.log(f"ERROR: Search failed - {error_msg}")
        wx.MessageBox(f"Search Error:\n{error_msg}", "Error", wx.OK|wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
