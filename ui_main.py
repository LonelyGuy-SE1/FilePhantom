"""
ui_main.py

Clean, minimal UI for Parallax File Finder.
"""

import wx
import os
import threading
import ctypes

import config
from indexer import FileIndexer
from search_engine import SearchEngine

# Set App User Model ID for Taskbar Icon
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
        
        # Centered content
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        lbl_title = wx.StaticText(panel, label="FILE FINDER")
        lbl_title.SetFont(wx.Font(42, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, config.FONT_FAMILY))
        lbl_title.SetForegroundColour(config.THEME["text"])
        content_sizer.Add(lbl_title, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=10)
        
        # Subtitle
        lbl_sub = wx.StaticText(panel, label="AI-Assisted Local Search (Parallax Runtime)")
        lbl_sub.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        lbl_sub.SetForegroundColour(config.THEME["text_dim"])
        content_sizer.Add(lbl_sub, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=40)
        
        # Path input
        self.txt_root_path = wx.TextCtrl(panel, value=os.getcwd(), size=(600, 40), style=wx.BORDER_SIMPLE)
        self.txt_root_path.SetBackgroundColour(config.THEME["panel_bg"])
        self.txt_root_path.SetForegroundColour(config.THEME["text"])
        self.txt_root_path.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        content_sizer.Add(self.txt_root_path, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        # Buttons row
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_browse = wx.Button(panel, label="BROWSE", size=(100, 36))
        self.btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
        btn_sizer.Add(self.btn_browse, flag=wx.RIGHT, border=8)
        
        self.btn_index = wx.Button(panel, label="INDEX", size=(100, 36))
        self.btn_index.Bind(wx.EVT_BUTTON, self.on_index)
        btn_sizer.Add(self.btn_index, flag=wx.RIGHT, border=8)
        
        self.btn_save = wx.Button(panel, label="SAVE", size=(80, 36))
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_index)
        btn_sizer.Add(self.btn_save, flag=wx.RIGHT, border=8)
        
        self.btn_load = wx.Button(panel, label="LOAD", size=(80, 36))
        self.btn_load.Bind(wx.EVT_BUTTON, self.on_load_index)
        btn_sizer.Add(self.btn_load)
        
        content_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=30)
        
        # Search box
        self.txt_search = wx.TextCtrl(panel, size=(600, 45), style=wx.TE_PROCESS_ENTER|wx.BORDER_SIMPLE)
        self.txt_search.SetBackgroundColour(config.THEME["panel_bg"])
        self.txt_search.SetForegroundColour(config.THEME["text"])
        self.txt_search.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        self.txt_search.SetHint("Type your search query...")
        self.txt_search.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        content_sizer.Add(self.txt_search, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        # Search Button
        self.btn_search = wx.Button(panel, label="SEARCH", size=(600, 40))
        self.btn_search.Bind(wx.EVT_BUTTON, self.on_search)
        content_sizer.Add(self.btn_search, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=20)
        
        # Results area
        self.scrolled_window = wx.ScrolledWindow(panel, size=(600, 400), style=wx.VSCROLL|wx.BORDER_NONE)
        self.scrolled_window.SetScrollRate(5, 5)
        self.scrolled_window.SetBackgroundColour(config.THEME["bg"])
        self.results_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.results_sizer)
        content_sizer.Add(self.scrolled_window, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=15)
        
        # Status
        self.lbl_status = wx.StaticText(panel, label="Ready")
        self.lbl_status.SetForegroundColour(config.THEME["text_dim"])
        self.lbl_status.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
        content_sizer.Add(self.lbl_status, flag=wx.ALIGN_CENTER)
        
        main_sizer.Add(content_sizer, flag=wx.ALIGN_CENTER)
        main_sizer.AddStretchSpacer(1)
        
        panel.SetSizer(main_sizer)

    def on_browse(self, event):
        dlg = wx.DirDialog(self, "Choose directory", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.txt_root_path.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_index(self, event):
        root = self.txt_root_path.GetValue().strip()
        if not root or not os.path.isdir(root):
            wx.MessageBox("Invalid folder.", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.lbl_status.SetLabel("Indexing files...")
        self.btn_index.Disable()
        threading.Thread(target=self._indexing_worker, args=(root,), daemon=True).start()

    def _indexing_worker(self, root):
        self.indexer.set_root_path(root)
        files = self.indexer.index_files(progress_callback=lambda msg: wx.CallAfter(self.lbl_status.SetLabel, msg))
        self.indexed_files = files
        wx.CallAfter(self._indexing_finished, len(files))

    def _indexing_finished(self, count):
        self.btn_index.Enable()
        self.lbl_status.SetLabel(f"Indexed {count} files. Ready.")

    def on_save_index(self, event):
        if not self.indexed_files:
            wx.MessageBox("No index to save.", "Info", wx.OK)
            return
        dlg = wx.FileDialog(self, "Save Index", wildcard="JSON (*.json)|*.json", style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.indexer.save_index(dlg.GetPath())
                self.lbl_status.SetLabel("Index saved.")
            except Exception as e:
                wx.MessageBox(f"Error: {e}", "Error", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()

    def on_load_index(self, event):
        dlg = wx.FileDialog(self, "Load Index", wildcard="JSON (*.json)|*.json", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                files = self.indexer.load_index(dlg.GetPath())
                self.indexed_files = files
                self.lbl_status.SetLabel(f"Loaded {len(files)} files.")
            except Exception as e:
                wx.MessageBox(f"Error: {e}", "Error", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()

    def on_search(self, event):
        if not self.indexed_files:
            wx.MessageBox("Please index or load files first.", "Info", wx.OK)
            return
        
        query = self.txt_search.GetValue().strip()
        if not query:
            return

        self.results_sizer.Clear(True)
        self.lbl_status.SetLabel("Refining results using the model running on Parallax...")
        self.btn_search.Disable()
        
        threading.Thread(target=self._search_worker, args=(query,), daemon=True).start()

    def _search_worker(self, query):
        try:
            results, reasoning = self.search_engine.search_parallax(query, self.indexed_files)
            wx.CallAfter(self._search_finished, results, reasoning)
        except Exception as e:
            wx.CallAfter(self._search_error, str(e))

    def _search_finished(self, results, reasoning):
        self.btn_search.Enable()
        self.lbl_status.SetLabel(f"Found {len(results)} matches.")
        
        self.scrolled_window.Freeze()
        
        for i, res in enumerate(results):
            result_panel = wx.Panel(self.scrolled_window)
            result_panel.SetBackgroundColour(config.THEME["panel_bg"])
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            # Rank + Name
            lbl_name = wx.StaticText(result_panel, label=f"#{i+1}  {res.file.name}")
            lbl_name.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, config.FONT_FAMILY))
            lbl_name.SetForegroundColour(config.THEME["text"])
            sizer.Add(lbl_name, flag=wx.LEFT|wx.TOP|wx.RIGHT, border=10)
            
            # Path
            lbl_path = wx.StaticText(result_panel, label=res.file.path)
            lbl_path.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, config.FONT_FAMILY))
            lbl_path.SetForegroundColour(config.THEME["text_dim"])
            sizer.Add(lbl_path, flag=wx.LEFT|wx.RIGHT, border=10)
            
            # Preview Snippet
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
        self.btn_search.Enable()
        self.lbl_status.SetLabel("Search failed.")
        wx.MessageBox(f"Search Error:\n{error_msg}", "Error", wx.OK|wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
