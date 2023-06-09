from PIL import Image
import tkinter as Tk
from tkinter import filedialog

textArt = str()
colourBW = [[]]
hVar1 = float()
hVar2 = float()

defaultDirectory = ""
def openFile():
    file = filedialog.askopenfilename (filetypes = (('Image', '*.png *.jpg *.jepg *.jpe *.jfif *.exif *.tiff *.tif *.webp *.bmp *.bid *.rle *.gif'),
                                                    ('Lossless Image', '*.png *.tiff *.tif *.bmp'),
                                                    ('All', '*.*')))
    return Image.open(file)


def getPixels(image):
    colourBW = [[0 for x in range (image.width)] for y in range ((image.height - image.height %2) // 2)]
    imageRGB = image.convert('RGB')
    for y in range (0, image.height - image.height %2, 2):
        for x in range (image.width):

            R = min(imageRGB.getpixel((x, y))[0] , imageRGB.getpixel((x, y+1))[0])
            G = min(imageRGB.getpixel((x, y))[1] , imageRGB.getpixel((x, y+1))[1])
            B = min(imageRGB.getpixel((x, y))[2] , imageRGB.getpixel((x, y+1))[2])

            colourBW[y//2][x] = percievedLightness(R, G, B)
            colourBW[y//2][x] = changeScale(100, 255, colourBW[y//2][x])
            colourBW[y//2][x] = round(colourBW[y//2][x])
    return colourBW
    

def changeScale(oldScale, newScale, value):
    return float ((value / oldScale) * newScale)

def changeScaleComplete(oldScaleLow, oldScaleHigh, newScalleLow, newScaleHigh, value):
    return float (((value - oldScaleLow) / oldScaleHigh) * (newScaleHigh - newScalleLow) + newScalleLow)

def Delinearise(RGBvalue):
    decimalRGBcolor = changeScale(255, 1, RGBvalue)
    
    if decimalRGBcolor <= 0.04045:
        return decimalRGBcolor / 12.92
    return ((decimalRGBcolor + 0.055) / 1.055) ** 2.4


def percievedLightness(R, G, B):
    luminance = 0.2126 * Delinearise(R) + 0.7152 * Delinearise(G) + 0.0722 * Delinearise(B)
    
    if luminance < 0.008856:
        return luminance * 903.3
    return luminance ** (1/3) * 116 - 16

def drawImage(lowScale, midScale, topScale):
    global colourBW
    midScale = 255 - midScale

    bottom = changeScaleComplete(0, 255, lowScale, topScale, changeScale(50, midScale, 25))
    middle = changeScaleComplete(0, 255, lowScale, topScale, midScale)
    top = changeScaleComplete(0, 255, lowScale, topScale, changeScale(50, midScale, 75))
    
    canvas = [
        "".join([
            "█" if curcolourBW < bottom else
            "▓" if curcolourBW < middle else
            "░" if curcolourBW < top else
            "─"
            for curcolourBW in map(int, row)
        ])
        for row in colourBW
    ]
    return "\n".join(canvas)

def saveFile(canvas):
    path = filedialog.asksaveasfilename (defaultextension = '.txt', filetypes = (('Text', '*.txt'),('All', '*.*')))
    if path is None:
        return
    
    try:
        file = open(path, 'w', encoding="utf-8")
    except:
        return

    file.write(canvas)
    return canvas

def openImage():
    image = openFile()
    global colourBW
    colourBW = getPixels(image)
    global textArt
    textArt = drawImage(int(colourSliderLow.get()), int(colourSliderMiddle.get()), int(colourSliderTop.get()))
    canvas.delete(1.0, Tk.END)
    canvas.insert(1.0, textArt)

def saveTextArt():
    if textArt == "":
        return
    saveFile(textArt)

def updateColourMiddle(midScale):
    global textArt
    textArt = drawImage(int(colourSliderLow.get()), int(midScale), int(colourSliderTop.get()))
    updateCanvas()
    
def updateColourLow(lowScale):
    global textArt
    textArt = drawImage(int(lowScale),  int(colourSliderMiddle.get()), int(colourSliderTop.get()))
    updateCanvas()

def updateColourTop(topScale):
    global textArt
    textArt = drawImage(int(colourSliderLow.get()), int(colourSliderMiddle.get()), int(topScale))
    updateCanvas()

def updateCanvas():
    global textArt
    scroll = scrollbarY.get()
    scroll = canvas.yview()[0]
    canvas.delete(1.0, Tk.END)
    canvas.insert(1.0, textArt)
    canvas.yview_moveto(scroll)   

def updateFont(fontSize):
    canvas.configure(font=("Courier", fontSize))


window = Tk.Tk()
window.title("TEXT ART GENERATOR")
window.geometry('600x800')


frameMain = Tk.Frame(window)
frameMain.pack(side=Tk.TOP, fill=Tk.X)

frameButtons = Tk.Frame(frameMain)
frameButtons.pack(side=Tk.RIGHT, fill=Tk.Y)

frameSliders = Tk.Frame(frameMain)
frameSliders.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)

frameColour = Tk.Frame(frameSliders)
frameColour.pack(side=Tk.TOP, expand=True, fill=Tk.X)

frameColourSliders = Tk.Frame(frameColour)
frameColourSliders.pack(side=Tk.BOTTOM, expand=True, fill=Tk.X)

frameZoom = Tk.Frame(frameSliders)
frameZoom.pack(side=Tk.BOTTOM, expand=True, fill=Tk.X)


openImg = Tk.Button(frameButtons, text="Open Image", width=15, command=openImage)
openImg.pack(side=Tk.TOP, expand=True, fill=Tk.Y)

saveTA = Tk.Button(frameButtons, text="Save To TextFile", width=15, command=saveTextArt)
saveTA.pack(side=Tk.BOTTOM, expand=True, fill=Tk.Y)


Tk.Label(frameColour, text="Colour Adjustment").pack(side=Tk.TOP,)
colourSliderMiddle = Tk.Scale(frameColourSliders ,orient = Tk.HORIZONTAL, from_= 0, to = 255, command=updateColourMiddle)
colourSliderMiddle.set(128)
colourSliderMiddle.pack(side=Tk.TOP, expand=True, fill=Tk.X)

colourSliderLow = Tk.Scale(frameColourSliders ,orient = Tk.HORIZONTAL, from_= 0, to = 127, command=updateColourLow)
colourSliderLow.set(0)
colourSliderLow.pack(side=Tk.LEFT, expand=True, fill=Tk.X)

colourSliderTop = Tk.Scale(frameColourSliders ,orient = Tk.HORIZONTAL, from_= 128, to = 255, command=updateColourTop)
colourSliderTop.set(255)
colourSliderTop.pack(side=Tk.RIGHT, expand=True, fill=Tk.X)


Tk.Label(frameZoom, text="Font Size").pack(side=Tk.TOP,)
fontSlider = Tk.Scale(frameZoom ,orient = Tk.HORIZONTAL, from_= 3, to = 25, command=updateFont)
fontSlider.set(8)
fontSlider.pack(side=Tk.BOTTOM, expand=True, fill=Tk.X)


scrollbarY = Tk.Scrollbar(window, orient=Tk.VERTICAL)
scrollbarX = Tk.Scrollbar(window, orient=Tk.HORIZONTAL)
canvas = Tk.Text(window, wrap=Tk.NONE, font=("Courier", 8), xscrollcommand=scrollbarX.set, yscrollcommand=scrollbarY.set)
scrollbarY.config(command=canvas.yview)
scrollbarX.config(command=canvas.xview)


scrollbarY.pack(side=Tk.RIGHT, fill=Tk.Y)
scrollbarX.pack(side=Tk.BOTTOM, fill=Tk.X)
canvas.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)

window.mainloop() 
