import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
from EquipmentLogic import equip
import customtkinter as ctk

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

        img = Image.open(folderPath).convert("RGBA")
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)

        self.cache[key] = ctk_img
        return ctk_img


"""drop down Toplevel window for grid of icons, inherits tk.Toplevel (floating window)"""
class GridPopup(ctk.CTkToplevel):
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

        # scroll
        self.scroll = ctk.CTkScrollableFrame(self, width=self.w, height=self.h)
        self.scroll.pack(fill="both", expand=True)

        # build icon grid
        pad = 6
        for i, ipath in enumerate(self.allIconsPaths):
            # find what row/col current icon is placed at
            r, c = divmod(i, self.cols)
            # build button
            btn = ctk.CTkButton(
                self.scroll,
                text="",
                width=gridIconSize[0],
                height=gridIconSize[1],
                fg_color="transparent",
                image=self.mainWindow.iconCache.get(ipath, (64, 64)),
                command=lambda path=ipath: self.pick(path),
            )
            btn.grid(row=r, column=c, padx=pad, pady=pad, sticky="nsew")

        for c in range(self.cols):
            self.scroll.grid_columnconfigure(c, weight=1)

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
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
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
        ctk.CTkLabel(self, text="HELLDIVERS 2 Loadout Manager", font=("Segoe UI", 14, "bold")).pack(pady=8)

        # row that holds all the equipment slot frames
        row = ctk.CTkFrame(self)
        row.pack(padx=12, pady=6, fill="x")

        # populate row
        for i, name in enumerate(equipmentNames):
            # frame in row that holds button, image, description
            slotFrame = ctk.CTkFrame(row, corner_radius=8)
            slotFrame.pack(side="left", padx=6, pady=6)

            # select buttons
            button = ctk.CTkButton(slotFrame, text=f"{name} ▾", command=lambda idx=i: self.openGrid(idx))
            button.pack(fill="x", padx=6, pady=6)
            self.chooseButtons.append(button)

            # empty blank square before image
            holder = ctk.CTkFrame(slotFrame, width=slotFrameIconSize[0], height=slotFrameIconSize[1], fg_color="#000000")
            holder.pack_propagate(False)
            holder.pack(pady=6)

            # actual image
            iconLabel = ctk.CTkLabel(holder, text="")
            iconLabel.pack(expand=True)
            self.selectedIconLabels.append(iconLabel)

            # descriptions
            description = ctk.CTkLabel(slotFrame, text="None")
            description.pack()
            self.selectedIconDescriptionLabels.append(description)

        # equip button at the bottom
        ctk.CTkButton(self, text="EQUIP", font=("Segoe UI", 14, "bold"), command=self.onEquip).pack(pady=10)

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
        self.selectedIconDescriptionLabels[slotIndex].configure(text=p.stem)

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
