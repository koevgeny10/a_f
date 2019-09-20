from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import black, blue, white
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY




styles = getSampleStyleSheet()
styleN = styles['Normal']


pdfmetrics.registerFont(TTFont('AdonisC', 'Ahellya.ttf'))

def ruler(сan):
    can.setFont("AdonisC", 6)
    for i in range(0, 900, 20):
        can.drawString(0, i, "{}--".format(i) + '        --         ' * 30)
        can.drawString(i, 0, "|{}".format(i))

def drawRamka(can, y, text):
    # maxline = 110
    # text = text.replace('\n', ' ')
    # words = text.split(' ')
    # lines = []
    # line = []
    # i = 0
    # while True:
    #     line.append(words[i])
    #     if words[i] == words[-1]:
    #         lines.append(line)
    #         break
    #
    #     if len(' '.join(line)) > maxline:
    #         lines.append(line)
    #         line = []
    #     i += 1
    #
    # i = 0
    # while i < len(lines):
    #     lines[i] = ' '.join(lines[i])
    #     i += 1



    global styleN
    styleN.alignment = TA_JUSTIFY
    leading = styleN.leading

    text = Paragraph(text, styleN)
    lines = text.breakLines(560)
    print(lines)

    textHeight = leading * len(lines.lines)



    can.setStrokeColor(blue)
    can.rect(30, y - textHeight - 10 - 5, 570, textHeight + 10 + 5) # Рамка
    head = 'Висновок'
    headWidth = stringWidth(head, 'AdonisC', 10)
    can.setFillColor(blue)
    can.rect(30 + 15, y - 10, 30 + headWidth + 5, 20, fill = 1) # прямоугольник в шапке (сверху)
    can.setFillColor(white)
    can.setFont("AdonisC", 10)
    can.drawString(30 + 15 + 30, y - 5, head) # надпись в шапке
    can.setFillColor(black)

    text.wrapOn(can, 560, textHeight)
    text.drawOn(can, 30 + 5, y - textHeight - 10)
    
    # text = can.beginText() #текст
    # text.setTextOrigin(30 + 5, y - 5 - 10 - 5)
    # text.setFont("AdonisC", 10)
    # text.textLines(lines)
    # can.drawText(text)


output = PdfFileWriter()
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
#ruler(can)
text = '''I am drawing text atop a base image via PIL. One of the requirements is for it to overflow to the next line(s) if the combined width of all characters exceeds the width of the base image.

Currently I'm using textwrap.wrap(text, width=16) to accomplish this. Here width defines the number of characters to accommodate in one line. Now the text can be anything since it's user generated. So the problem is that hard-coding width won't take into account width variability due to font type, font size and character selection.

What do I mean?

Well imagine I'm using DejaVuSans.ttf, size 14. A W is 14 in length, whereas an 'i' is 4. For a base image of width 400, up to 100 i characters can be accommodated in a single line. But only 29 W characters. I need to formulate a smarter way of wrapping to the next line, one where the string is broken when the sum of character-widths exceeds the base image width.

Can someone help me formulate this? An illustrative example would be great!'''

drawRamka(can, 283, text)

can.save()
packet.seek(0)
new_pdf = PdfFileReader(packet)
output.addPage(new_pdf.getPage(0))
outputStream = open("ramka.pdf", "wb")
output.write(outputStream)
outputStream.close()