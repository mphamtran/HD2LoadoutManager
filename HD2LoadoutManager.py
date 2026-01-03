import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
from EquipmentLogic import equip

# folder containing larger equipped icons
equippedIconFolderPath = Path(__file__).parent / "equippedicons"
# folder containing grid icons from submenu
gridIconFolderPath = Path(__file__).parent / "gridicons"
# icon size in the dropdown grid
gridIconSize = (64, 64)
# column number in the dropdown grid
gridColNum = 4
# icon size after selecting
slotFrameIconSize = (120, 120)
# number of equipment
equipmentNum = 5
equipmentNames = ["Stratagem 1", "Stratagem 2", "Stratagem 3", "Stratagem 4", "Booster"]


# icon cache handling
def loadIcons(folderPath: Path):
    # list of paths to all .png files in folder
    allIconsPaths = list(folderPath.glob("*.png"))
    return allIconsPaths


"""cache icons to avoid garbage collection and speeds up repeated icon loading"""
class IconCache:
    def __init__(self):
        self.cache = {}

    def get(self, folderPath: Path, size):
        # return cached image if already loaded
        key = (folderPath, size)
        if key in self.cache:
            return self.cache[key]
        # otherwise load and resize image
        icon = Image.open(folderPath).resize(size)
        # converts pillow image to tkinter compatible image and then cache
        tkinterIcon = ImageTk.PhotoImage(icon)
        self.cache[key] = tkinterIcon
        return tkinterIcon

"""drop down Toplevel window for grid of icons, inherits tk.Toplevel (floating window)"""
class GridPopup(tk.Toplevel):
    def __init__(self, mainWindow, slotIndex, allIconsPaths, size=(420, 360), cols=3):
        super().__init__(mainWindow)

        self.mainWindow = mainWindow
        self.slotIndex = slotIndex
        self.allIconsPaths = allIconsPaths
        self.cols = cols
        self.w, self.h = size

        # make it work like a dropdown, automatically close popup if focus is lost or user presses Escape
        self.overrideredirect(True)
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())

        # scrollable canvas, vertical scrollbar setup
        self.canvas = tk.Canvas(self, width=self.w, height=self.h, highlightthickness=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # frame sits inside the canvas and holds all the buttons and labels (canvas can scroll but not frame)
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # build icon grid
        pad = 6
        for i, ipath in enumerate(self.allIconsPaths):
            # find what row/col current icon is placed at
            r, c = divmod(i, self.cols)
            # build button
            btn = tk.Button(
                self.frame,
                image=self.mainWindow.iconCache.get(ipath, (64, 64)),
                bd=0,
                command=lambda path=ipath: self.pick(path),
            )
            btn.grid(row=r, column=c, padx=pad, pady=pad)

        # scroll region update
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # mouse wheel scroll
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onMouseWheel(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), "units")

    def showBelow(self, widget):
        self.update_idletasks()

        xPos = widget.winfo_rootx()
        yPos = widget.winfo_rooty() + widget.winfo_height()

        self.geometry(f"{self.w}x{self.h}+{xPos}+{yPos}")
        self.focus_set()

    def pick(self, path: Path):
        self.mainWindow.setSlot(self.slotIndex, str(path.resolve()))
        self.destroy()

"""main window that manages the 5 equipment slots and opens popups"""
class MainWindow(tk.Tk):
    def __init__(self):
        # This calls tk.Tk.__init__(), which creates the actual main window.
        super().__init__()

        self.title("Helldivers 2 Loadout Manager")
        self.geometry("860x520")
        self.resizable(False, False)

        # icon cache handling
        self.iconCache = IconCache()
        self.allIconsPaths = loadIcons(gridIconFolderPath)
        # equipment slot icon handling
        self.selectedIconPaths = [None] * equipmentNum
        self.selectedIcons = [None] * equipmentNum
        self.selectedIconLabels = []
        self.selectedIconDescriptionLabels = []
        self.chooseButtons = []

        # title
        tk.Label(self, text="HELLDIVERS 2 Loadout Manager", font=("Segoe UI", 14, "bold")).pack(pady=8)

        # row that holds all the equipment slot frames
        row = tk.Frame(self)
        row.pack(padx=12, pady=6, fill="x")

        # populate row
        for i, name in enumerate(equipmentNames):
            # frame in row that holds button, image, description
            slotFrame = tk.Frame(row, bd=1, relief="ridge", padx=8, pady=8)
            slotFrame.pack(side="left", padx=6, pady=6)

            # select buttons
            button = tk.Button(slotFrame, text=f"{name} ▾", command=lambda idx=i: self.openGrid(idx))
            button.pack(fill="x")
            self.chooseButtons.append(button)

            # empty blank square before image
            holder = tk.Frame(slotFrame, width=slotFrameIconSize[0], height=slotFrameIconSize[1], bg="#000000")
            holder.pack_propagate(False)
            holder.pack(pady=6)

            # actual image
            iconLabel = tk.Label(holder, bg="#000000")
            iconLabel.pack(expand=True)
            self.selectedIconLabels.append(iconLabel)

            # descriptions
            description = tk.Label(slotFrame, text="None")
            description.pack()
            self.selectedIconDescriptionLabels.append(description)

        # equip button at the bottom
        tk.Button(self, text="EQUIP", font=("Segoe UI", 14, "bold"), command=self.onEquip).pack(pady=10)

    # event handlers
    def openGrid(self, slotIndex):
        if not self.allIconsPaths:
            messagebox.showinfo("No icons", f"No PNGs in: {gridIconFolderPath}")
            return
        gp = GridPopup(self, slotIndex, self.allIconsPaths, size=(420, 360), cols=gridColNum)
        gp.showBelow(self.chooseButtons[slotIndex])

    def setSlot(self, slotIndex, absPath: str):
        """When user picks an icon, update preview + caption."""
        self.selectedIconPaths[slotIndex] = absPath
        p = Path(absPath)
        ph = self.iconCache.get(p, slotFrameIconSize)
        self.selectedIcons[slotIndex] = ph
        self.selectedIconLabels[slotIndex].configure(image=ph)
        self.selectedIconDescriptionLabels[slotIndex].config(text=p.name)

    def onEquip(self):
        """When user clicks EQUIP, call the external equip() function."""
        ordered = self.selectedIconPaths[:]
        empty = [i + 1 for i, v in enumerate(ordered) if not v]
        if empty and not messagebox.askyesno("Missing", f"Slots {empty} empty. Continue?"):
            return
        print("Calling equip with:", ordered)
        equip(ordered)


if __name__ == "__main__":
    MainWindow().mainloop()
