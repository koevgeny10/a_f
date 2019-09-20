from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
styleN = styles['Normal']
#pdfmetrics.registerFont(TTFont('AdonisC', 'Ahellya.ttf'))
pdfmetrics.registerFont(TTFont('HelveticaNeueC', 'HelveticaNeue.ttf'))
st_font = 'HelveticaNeueC'


def ruler(can):
    can.setFont(st_font, 6)
    #can.setFont("AdonisC", 6)
    for i in range(0, 900, 20):
        can.drawString(0, i, "{}--".format(i) + '        --         ' * 30)
        can.drawString(i, 0, "|{}".format(i))


existing_pdf = PdfFileReader(open("REP_template.pdf", "rb"))
output = PdfFileWriter()


# 1
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
can.setFont(st_font, 12)
can.drawString(220, 365, "Жигалов Юлій Анатолійович")
can.setFont(st_font, 10)
can.drawString(460, 265, "26/01/1971")
can.drawString(460, 245, "12/04/2018")
can.drawString(460, 227, "Кущ Олександр")
can.drawString(460, 210, "Ткачук Тимофій")
can.drawString(460, 195, "Довгич Олександр")
can.save()
packet.seek(0)
new_pdf = PdfFileReader(packet)
page = existing_pdf.getPage(0)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)


# 2
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
can.setFont(st_font, 12)
can.drawString(100, 800, "Жигалов Юлій Анатолійович")
can.save()
packet.seek(0)
new_pdf = PdfFileReader(packet)
page = existing_pdf.getPage(1)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)


# 3
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
#ruler(can)
can.setFont(st_font, 12)
can.drawString(100, 800, "Жигалов Юлій Анатолійович")
zakl = '''В цілому результати аналізу крові знаходяться в межах норми.Детальний аналіз показує, що
рівень моноцитів як абсолютне значення так і відносне
підвищено, що вказує на присутність в організмі інфекції, тобто в даному випадку клієнт ще
не повністю одужав після недавнього захворювання. Про це свідчить і знижений рівень
тромбоцитів. При  інфекціях  показник знижується. Дещо  підвищений рівень Альбуміну (%)
і знижений рівень глобуліну. Це незначні порушення. Але слід звернути увагу, що це може
бути пов’язано з інфекцією присутньою в організмі після нещодавнього захворювання ,а
також можливим зневодненням. пити більше рідини-головна рекомендація при
підвищеному рівні альбуміну, так як зневоднення найбільш часта причина завищення
показника.
Рекомендації: На рівень холестерину в крові впливають жири, які ми їмо або, навпаки,
не їмо. Насичені жири підвищують холестерин. Ними багаті жирне м`ясо, вершкове масло,
сири. Поліненасичені жири знижують холестерин. Вони входять до складу соєвої,
соняшникової, кукурудзяної олії, морепродуктів, нежирних молочних продуктів.'''
text = can.beginText()
text.setTextOrigin(170, 320)
text.setFont(st_font, 10)
for line in zakl.split('\n'):
    text.textLine(line)
can.drawText(text)
can.save()
packet.seek(0)
new_pdf = PdfFileReader(packet)
page = existing_pdf.getPage(2)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)


# 4
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
#ruler(can)
can.setFont(st_font, 12)
can.drawString(100, 800, "Жигалов Юлій Анатолійович")
can.setFont(st_font, 10)
can.drawString(270, 670, "168 см")
can.drawString(270, 655, "83,70 кг")
can.drawString(270, 641, "40 см")
can.drawString(270, 612, "113 см")
can.drawString(270, 597, "108 см")
can.drawString(270, 566, "38 см")
can.drawString(270, 553, "38 см")
can.drawString(270, 538, "29 см")
can.drawString(270, 521, "29 см")
can.drawString(270, 493, "91 см")
can.drawString(270, 478, "97 см")
can.drawString(270, 447, "99 см")
can.drawString(270, 432, "57 см")
can.drawString(270, 417, "60 см")
can.drawString(270, 395, "0,92")
can.save()
packet.seek(0)
new_pdf = PdfFileReader(packet)
page = existing_pdf.getPage(3)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)


# 5
#new_pdf = PdfFileReader(open("REP_new.pdf", "rb"))
#output.addPage(new_pdf.getPage(4))

# 6
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
#ruler(can)
can.setFont(st_font, 12)
can.drawString(100, 800, "Жигалов Юлій Анатолійович")
can.setFont(st_font, 8)
can.drawString(400, 673, "64.30 %")
can.drawString(400, 662, "14.20 %")
can.drawString(400, 650, "1.00 %")
can.drawString(400, 640, "1.00 %")
can.drawString(400, 628, "9.70 %")
can.drawString(400, 618, "9.20 %")
can.drawString(400, 608, "19.70 %")
can.drawString(400, 597, "68.10 кг")
can.drawString(400, 585, "4.60 кг")
can.drawString(400, 573, "4.50 кг")
can.drawString(400, 563, "11.35 кг")
can.drawString(400, 553, "11.85 кг")
can.drawString(400, 542, "35.80 кг")
can.drawString(400, 530, "7.00 Lv")
can.drawString(400, 520, "3.50 кг")
can.drawString(400, 511, "35 лет")
can.drawString(400, 500, "29.51 кг/м2")
zakl = '''Індекс маси тіла вище норми (надмірна вага) Примітка: клієнт відноситься до людей з
гіпертрофованою м'язовою масою і застосування імпедансметра має похибку
Відсоток жиру низький
Відсоток м'язової тканини - високий (тип фігури атлетичний)
Спостерігається диспропорція розвитку м'язів верхніх і нижніх кінцівок. М'язи тулуба і рук
домінують
'''
rek = '''Рекомендується збільшити кількість силових навантажень на м'язи нижніх кінцівок для корекції
диспропорції'''
text = can.beginText()
text.setTextOrigin(95, 170)
text.setFont(st_font, 10)
text.textLines(zakl)
can.drawText(text)

text = can.beginText()
text.setTextOrigin(95, 90)
text.setFont(st_font, 10)
text.textLines(rek)
can.drawText(text)

can.save()
packet.seek(0)
new_pdf = PdfFileReader(packet)
page = existing_pdf.getPage(5)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)


#new_pdf = PdfFileReader(open("REP_new.pdf", "rb"))
#for i in range(6, 21):
#    output.addPage(new_pdf.getPage(i))


outputStream = open("destination2.pdf", "wb")
output.write(outputStream)
outputStream.close()