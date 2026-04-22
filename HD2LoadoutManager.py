import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
from EquipmentLogic import equip
import customtkinter as ctk
import json

# folder containing larger equipped icons
equippedIconFolderPath = Path(__file__).parent / "equippedicons"
# folder containing grid icons from submenu
gridIconFolderPath = Path(__file__).parent / "debugLOADSOFICONS"
# json path (holds strategems in loadout, expand to weps/armor/nade l8r
# also standardize variable naming between loadout/equipment/strategems l8r)
loadoutJson = Path(__file__).parent / "loadouts.json"
# icon size in the dropdown grid
gridIconSize = (64, 64)
# column number in the dropdown grid
gridColNum = 4
# icon size after selecting
slotFrameIconSize = (72, 72)
# number of equipment
equipmentNum = 5
equipmentNames = ["Stratagem 1", "Stratagem 2", "Stratagem 3", "Stratagem 4", "Booster"]


# icon cache handling
def loadIcons(folderPath: Path):
    # list of paths to all .png files in folder
    allIconsPaths = list(folderPath.glob("*.png"))
    return allIconsPaths


# json file handling
def loadJson(jsonPath: Path = loadoutJson):
    try:
        data = json.loads(jsonPath.read_text(encoding="utf-8"))
        return data.get("loadouts", {})
    except Exception:
        return {}


def saveLoadoutList(loadouts, jsonPath: Path = loadoutJson):
    # since "loadouts" will get stripped from .get
    data = {"loadouts": loadouts}
    jsonPath.write_text(json.dumps(data, indent=2), encoding="utf-8")


# cache icons to avoid garbage collection and speeds up repeated icon loading
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


# main window that manages the 5 equipment slots and opens popups
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
        self.title("Helldivers 2 Loadout Manager")
        self.geometry("1107x612")
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
        self.activeSlot = None

        # title
        ctk.CTkLabel(self, text="HELLDIVERS 2 Loadout Manager", font=("Segoe UI", 14, "bold")).pack(pady=8)

        mainFrame = ctk.CTkFrame(self)
        mainFrame.pack(padx=10, pady=10, fill="both", expand=True)
        mainFrame.grid_rowconfigure(0, weight=1)
        mainFrame.grid_columnconfigure(0, weight=1)
        mainFrame.grid_columnconfigure(1, weight=3)

        rightFrame = ctk.CTkFrame(mainFrame)
        rightFrame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # row that holds all the equipment slot frames
        row = ctk.CTkFrame(rightFrame)
        row.pack(padx=12, pady=6, fill="x")

        # populate row
        for i, name in enumerate(equipmentNames):
            # frame in row that holds button, image, description
            slotFrame = ctk.CTkFrame(row, corner_radius=8)
            slotFrame.pack(fill="x", padx=6, pady=6)

            # select buttons
            button = ctk.CTkButton(slotFrame, text=f"{name} ▾", fg_color="transparent", hover_color="#333333",
                                   command=lambda idx=i: self.selectSlot(idx))
            button.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.chooseButtons.append(button)

            # empty blank square before image
            holder = ctk.CTkFrame(slotFrame, width=slotFrameIconSize[0], height=slotFrameIconSize[1], fg_color="#000000")
            holder.pack_propagate(False)
            holder.pack(side="left", padx = 6, pady=6)

            # actual image
            iconLabel = ctk.CTkLabel(holder, text="")
            iconLabel.pack(expand=True)
            self.selectedIconLabels.append(iconLabel)

            # descriptions
            description = ctk.CTkLabel(slotFrame, text="")
            description.pack(side="left", expand=True)
            self.selectedIconDescriptionLabels.append(description)

        # scroll
        gridFrame = ctk.CTkScrollableFrame(mainFrame)
        gridFrame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # build icon grid
        pad = 6
        for i, ipath in enumerate(self.allIconsPaths):
            r, c = divmod(i, gridColNum)

            # frame for button, image, name
            gridItemFrame = ctk.CTkFrame(gridFrame, fg_color="transparent")
            gridItemFrame.grid(row=r, column=c, padx=pad, pady=pad, sticky="nsew")

            # build button
            btn = ctk.CTkButton(
                gridItemFrame,
                text="",
                width=gridIconSize[0],
                height=gridIconSize[1],
                fg_color="transparent",
                image=self.iconCache.get(ipath, gridIconSize),
                command=lambda path=ipath: self.pick(path),
            )
            btn.pack()

            # name
            imgName = Path(ipath).stem
            ctk.CTkLabel(
                gridItemFrame,
                text=imgName,
                wraplength=gridIconSize[0] + 20,
                font=ctk.CTkFont(size=11)
            ).pack(pady=(2, 0))

        for c in range(gridColNum):
            gridFrame.grid_columnconfigure(c, weight=1)

        ctk.CTkButton(rightFrame, text="EQUIP", font=("Segoe UI", 14, "bold"), command=self.onEquip).pack(side="right", padx=6)

    # event handlers
    #def openGrid(self, slotIndex):
    #    if not self.allIconsPaths:
    #        messagebox.showinfo("No icons", f"No PNGs in: {gridIconFolderPath}")
    #        return
    #    gp = GridPopup(self, slotIndex, self.allIconsPaths, size=(420, 360), cols=gridColNum)
    #    gp.showBelow(self.chooseButtons[slotIndex])

    def pick(self, path: Path):
        if self.activeSlot is None:
            messagebox.showinfo("No Slot Selected", "Please select a slot")
            return

        self.setSlot(self.activeSlot, str(path.resolve()))

    # when user clicks button next to slots
    def selectSlot(self, idx):
        self.activeSlot = idx

        # reset all highlights other
        for button in self.chooseButtons:
            button.configure(border_width=0)

        # highlight selected slot
        self.chooseButtons[idx].configure(
            border_width=2,
            border_color="cyan"
        )

    # when user picks an icon, update preview + caption
    def setSlot(self, slotIndex, absPath: str):
        self.selectedIconPaths[slotIndex] = absPath
        p = Path(absPath)
        ph = self.iconCache.get(p, slotFrameIconSize)
        self.selectedIcons[slotIndex] = ph
        self.selectedIconLabels[slotIndex].configure(image=ph)
        self.selectedIconDescriptionLabels[slotIndex].configure(text=p.stem)

    def onEquip(self):
        ordered = self.selectedIconPaths[:]
        empty = [i + 1 for i, v in enumerate(ordered) if not v]
        if empty and not messagebox.askyesno("Missing", f"Slots {empty} empty. Continue?"):
            return
        print("Calling equip with:", ordered)
        equip(ordered)


if __name__ == "__main__":
    MainWindow().mainloop()
