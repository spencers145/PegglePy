try:
    import tkinter
    from tkinter import filedialog
    tkinterInstalled = True
except ImportError:
    print("WARN: Tkinter is not installed. You will be unable to load or save levels.")
    print("Please install tkinter")
    tkinterInstalled = False

import pickle # sort of abusing pickle to save the level data (it works, but I dont really think pickle is meant for this)

from local.config import debug, WIDTH, HEIGHT

from local.peg import Peg

if tkinterInstalled:
    def fileSelectWindow():
        #initiate tinker and hide window 
        main_win = tkinter.Tk() 
        main_win.withdraw()

        main_win.overrideredirect(True)
        main_win.geometry('0x0+0'+str(round(WIDTH/2))+'+'+str(round(HEIGHT/2)))

        main_win.deiconify()
        main_win.lift()
        main_win.focus_force()

        #open file selector 
        main_win.sourceFile = filedialog.askopenfilename(parent=main_win, initialdir= "./levels", title='Please select a level to open', 
                                                            filetypes = (("PegglePy Level File", "*.lvl*"), ("all files", "*")))

        selected_file = main_win.sourceFile

        #close window after selection 
        main_win.destroy()

        if str(selected_file) == '()' or str(selected_file) == '':
            selected_file = None

        if debug:
            print("File selected: '" + str(selected_file) +"'")

        # returns the path to the selected file
        return selected_file


    def fileSaveWindow():
        #initiate tinker and hide window 
        main_win = tkinter.Tk() 
        main_win.withdraw()

        main_win.overrideredirect(True)
        main_win.geometry('0x0+0'+str(round(WIDTH/2))+'+'+str(round(HEIGHT/2)))

        main_win.deiconify()
        main_win.lift()
        main_win.focus_force()

        #open file selector 
        main_win.sourceFile = filedialog.asksaveasfile(parent=main_win, initialdir= "./levels", title='Please name the level', 
                                                            filetypes = (("PegglePy Level File", "*.lvl*"), ("all files", "*")),
                                                            defaultextension = ".lvl", initialfile = "Untitled Level")

        selected_file = main_win.sourceFile

        #close window after selection 
        main_win.destroy()

        if selected_file == None:
            if debug:
                print("WARN: File was not saved")
            return None

        if debug:
            print("File saved: '" + str(selected_file.name) +"'")

        # returns the path to the selected file
        return str(selected_file.name)
        
# tkinter is not installed (do nothing, default level will be used)
else:
    def fileSelectWindow():
        print("Tkinter is not installed, you will be unable to load or save levels.")
        print("Please install tkinter.")
        print("Loading default level...")
        return None

    def fileSaveWindow():
        print("Tkinter is not installed, you will be unable to load or save levels.")
        print("Please install tkinter.")
        print("Loading default level...")
        return None


def loadData(filePath: str | None = None, centerPegs: bool = True) -> tuple[list[Peg], str]:
    if filePath == None:
        filePath = fileSelectWindow()

    posList = createDefaultPegsPos()
    if filePath != None:
        try:
            with open(filePath, 'rb') as f:
                posList = pickle.load(f)

        except Exception: # if the file selected is invalid generate the default level and use it instead
            if debug:
                print("WARN: Unable to open file: \"" + str(filePath) + "\". using default level (No file created or loaded)")

            posList = createDefaultPegsPos()

    # if no file was selected
    elif filePath == None and debug:
        print("WARN: No file selected, using default level (No file created or loaded)")
        

    # using x and y tuple, create list of peg objects
    pegs = []
    for xyPos in posList:
        x, y = xyPos
        pegs.append(Peg(x, y))
    
    if centerPegs:
        # adjust the positions of every peg to be centered on the screen based on WIDTH and HEIGHT
        # get the position of the left most peg
        leftMostPeg = pegs[0]
        for peg in pegs:
            if peg.pos.x < leftMostPeg.pos.x:
                leftMostPeg = peg
        rightMostPeg = pegs[0]
        for peg in pegs:
            if peg.pos.x > rightMostPeg.pos.x:
                rightMostPeg = peg

        # find the center of the left most and right most pegs
        centerOfLeftAndRightPegs = (leftMostPeg.pos.x + rightMostPeg.pos.x)/2
        # find the center of the screen
        screenCenter = WIDTH/2
        # find the difference between the center of the screen and the center of the left and right most pegs
        difference = screenCenter - centerOfLeftAndRightPegs

        # adjust the position of every peg by the difference
        for peg in pegs:
            peg.pos.x += difference


    
    return pegs, filePath


def saveData(pegs: list[Peg], filePath: str | None = None):
    if filePath == None:
        filePath = fileSaveWindow()

    posList = getPegPosList(pegs)
    try:
        print(posList)
        # create a new pickle file
        with open(filePath, 'wb') as f:
            pickle.dump(posList, f)
    except Exception as e:
        if debug:
            print("ERROR: Unable to save file: \"" + str(filePath) + "\". Exception: " + str(e))
            print("Check that the file path is valid and that you have write permissions")
        return str(Exception)



def getPegPosList(pegs):
    posList = []
    for peg in pegs:
        x, y = peg.pos.x, peg.pos.y
        posList.append((x, y))

    return posList


def createDefaultPegsPos():
    # default level ("peggle clone")
    posList = [(533, 380),
               (639, 380),
               (745, 379),
               (866, 379),
               (968, 377),
               (1096, 375),
               (1047, 478),
               (922, 479),
               (815, 491),
               (701, 498),
               (590, 506),
               (390, 373),
               (249, 380),
               (115, 372),
               (371, 621),
               (505, 620),
               (645, 607),
               (878, 615),
               (1005, 615),
               (1104, 614),
               (1154, 720),
               (1061, 713),
               (936, 724),
               (836, 726),
               (574, 724),
               (708, 739),
               (765, 617),
               (444, 497),
               (320, 497),
               (161, 481),
               (245, 607),
               (111, 599),
               (445, 719),
               (304, 713),
               (172, 721),
               (61, 738),
               (48, 489),
               (46, 273),
               (186, 289),
               (315, 283),
               (459, 288),
               (588, 285),
               (703, 283),
               (799, 283),
               (924, 277),
               (1033, 278),
               (1153, 274),
               (1141, 472),
               (168, 632)]

    return posList

if __name__ == '__main__':
    print("Warning !!! Be careful, files may be overwritten or deleted")

    testPegs, filepath = loadData()
    print (str(len(testPegs)) + " pegs found in the level")
    
    testPegs = [Peg(1,1)]
    #saveData(testPegs)
    print(fileSaveWindow())
