from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import os
import sys
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import black, blue, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor
from django.conf import settings
from bisect import bisect_left
from django.http import HttpResponseRedirect, HttpResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hrm.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from diagnostics.models import *
import datetime


class DiagnosticReports():
    def __init__(self):
        self.out_report = ''
        self.user_diagnostic = 30
        self.user_id = 50
        self.report_id = 1
        self.default_font_size = 12
        self.output_pdf = PdfFileWriter()
        self.styles = getSampleStyleSheet()
        self.styleN = self.styles['Normal']
        pdfmetrics.registerFont(TTFont('AdonisC', settings.BASE_DIR + r'/report/Ahellya.ttf')) # Для укр яз
        pdfmetrics.registerFont(TTFont('HelveticaNeueC', settings.BASE_DIR + r'/report/HelveticaNeue.ttf'))
        self.st_font = 'HelveticaNeueC'

    def GetPosScale(self, st_scale, val, x1, x2):
        cnt_items = len(st_scale.split(';'))
        st_scale_items = self.splitEx(st_scale, [';', '-'])
        scale_items = [float(i) for i in st_scale_items]
        index = bisect_left(scale_items, val)
        call_index = pos_index = 0
        for st_item in st_scale.split(';'):
            if (pos_index == index):
                callofset = (x2 - x1)/cnt_items/2
                return x1 + (((x2 - x1)/cnt_items)*(call_index)) + callofset
            call_index += 1
            if '-' in st_item:
                pos_index += 1
            pos_index += 1
        return call_index

    def splitEx(self, s, seps):
        res = [s]
        for sep in seps:
            s, res = res, []
            for seq in s:
                res += seq.split(sep)
        return res

    def drange(self, start, stop, step):
       while start < stop:
          yield start
          start += step

    # Линейка ОТЛАДКА
    def showscale(self, canvas):
       canvas.setFont(self.st_font, 5)
       canvas.setLineWidth(.1)
       for x in self.drange(0, 600, 10):
          canvas.line(x, 0, x, 10)
          canvas.drawString(x, 12, str(x))
       for y in self.drange(0, 840, 10):
          canvas.line(0, y, 10, y)
          canvas.drawString(12, y, str(y))


    def drawRamka(self, can, y, text, type):
        #global styleN
        self.styleN.alignment = TA_JUSTIFY
        self.styleN.fontName = 'AdonisC'
        leading = self.styleN.leading

        can.setLineWidth(.8)
        text = Paragraph(text, self.styleN)
        lines = text.breakLines(530)
        textHeight = leading * len(lines.lines)

        can.setStrokeColor(HexColor("0x00b0f0"))
        can.rect(30, y - textHeight - 10 - 5, 540, textHeight + 10 + 5) # Рамка
        head = type
        headWidth = stringWidth(head, 'HelveticaNeueC', 10)
        can.setFillColor(HexColor("0x00b0f0"))
        can.rect(30 + 15, y - 10, 30 + headWidth + 5, 20, fill=1) # прямоугольник в шапке (сверху)
        can.setFillColor(white)
        can.setFont("HelveticaNeueC", 10)
        can.drawString(30 + 15 + 30, y - 5, head) # надпись в шапке
        can.setFillColor(black)

        text.wrapOn(can, 530, textHeight)
        text.drawOn(can, 30 + 5, y - textHeight - 10)


    # Шаблон страницы
    def templ_page(self, packet, object):
       tmpl_file = str(object.template_file.file)
       print(tmpl_file)
       tmpl_pdf = PdfFileReader(open(tmpl_file, "rb"))
       page = tmpl_pdf.getPage(0)
       self.output_pdf.addPage(page)

    # Отображение объектов в отчете
    def write_page_objects(self, page_objects, pagenumber, ruller):
        packet = io.BytesIO()
        getTemplate = False
        # поиск шаблона
        for page_object in page_objects:
            if (page_object.page_object_type.code == 101):
                self.templ_page(packet, page_object)
                getTemplate = True
                break

        # размещаем остальные елементы в pdf
        if(getTemplate):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            if ruller:
                self.showscale(can)
            user_info = User.objects.filter(pk=self.user_id)[0]
            for page_object in page_objects:

                # Установка размера шрифта
                if (page_object.font_size is not None):
                    can.setFont(self.st_font, int(page_object.font_size))
                else:
                    can.setFont(self.st_font, self.default_font_size)

                code = page_object.page_object_type.code
                if (code == 101):  # Шаблон страницы
                    continue
                elif (code == 102):  # Надпись
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), str(page_object.title))
                elif (code == 103):  # ФИО клиента
                    user_fullname = user_info.get_full_name()
                    if (user_info.userprofile.user_full_name is not None) and (len(user_info.userprofile.user_full_name) > 0):
                        user_fullname += ' ' + str(user_info.userprofile.user_full_name)
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), str(user_fullname))
                elif (code == 104):  # Информ. о тестировании
                    pass
                elif (code == 105):  # Штрих код
                    pass
                elif (code == 106):  # Дата рождения
                    if(user_info.userprofile.birthday is not None):
                        can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate),
                                    user_info.userprofile.birthday.strftime("%d/%m/%Y"))
                elif (code == 107):  # Дата тестирования
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), str(datetime.datetime.now().strftime("%d/%m/%Y")))
                elif (code == 108):  # Велнес консультант
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), page_object.st_text)
                elif (code == 109):  # Менеджер
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), page_object.st_text)
                elif (code == 110):  # Тренер
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), page_object.st_text)
                elif (code == 111):  # Номер страници
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), str(page_object.page.page_number))
                elif code == 112:    # Значение диагностики
                    value = DiagnosticsResult.objects.get(
                        diagnostics=Diagnostics.objects.get(id=self.user_diagnostic), # Времено
                        parameter_diagnostics=page_object.for_parameter
                    ).value
                    if re.match("^\d+?\.\d+?$", value) is not None:
                        value = str(round(float(value), 1))
                    can.drawString(int(page_object.x_coordinate), int(page_object.y_coordinate), value)
                elif code == 113:    # Текст в рамке (Заключение, Рекомендации)
                    value = DiagnosticsResult.objects.get(
                        diagnostics=Diagnostics.objects.get(id=self.user_diagnostic),  # Времено
                        parameter_diagnostics=page_object.for_parameter
                    ).value
                    self.drawRamka(can, int(page_object.y_coordinate), value, page_object.title)
                elif code == 114:
                    heightitem = widthitem = None
                    if page_object.x2_coordinate is not None and int(page_object.x2_coordinate) > 0:
                        widthitem=int(page_object.x2_coordinate)
                    if page_object.x2_coordinate is not None and int(page_object.y2_coordinate) > 0:
                        heightitem=int(page_object.y2_coordinate)
                    can.drawImage(str(page_object.template_file.file), int(page_object.x_coordinate), int(page_object.y_coordinate),
                             width=widthitem, height=heightitem, preserveAspectRatio=True)
                elif code == 115:
                    value = DiagnosticsResult.objects.get(
                        diagnostics=Diagnostics.objects.get(id=self.user_diagnostic),  # Времено
                        parameter_diagnostics=page_object.for_parameter
                    ).value
                    if re.match("^\d+?\.\d+?$", value) is not None:
                        value = round(float(value), 1)
                    else:
                        value = int(value)
                    indexX = self.GetPosScale(page_object.st_text, value, int(page_object.x_coordinate), int(page_object.x2_coordinate))
                    can.drawString(int(indexX), int(page_object.y_coordinate), str(value))

                    pass

            can.save()
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            print(pagenumber)
            page = self.output_pdf.getPage(pagenumber)
            page.mergePage(new_pdf.getPage(0))


    def generate_diagnostic_reports_view(self, user_id, diagnostic_id, ruller, page_number):
        self.user_diagnostic = diagnostic_id
        self.user_id = user_id
        pagenumber = 0

        if page_number is None:
            report_pages = Page.objects.filter(report=self.report_id).order_by('page_number')
            for report_page in report_pages:
                page_objects = PageObject.objects.filter(page=report_page.id)
                self.write_page_objects(page_objects, pagenumber, ruller)
                pagenumber += 1
        else:
            report_page = Page.objects.get(report=self.report_id, page_number=page_number)
            page_objects = PageObject.objects.filter(page=report_page.id)
            self.write_page_objects(page_objects, pagenumber, ruller)



        response = HttpResponse(content_type='application/pdf')
        outputStream = response
        self.output_pdf.write(response)
        outputStream.close()

        return response

    def generate_diagnostic_reports_attach(self, user_id, diagnostic_id):
        self.user_diagnostic = diagnostic_id
        self.user_id = user_id

        pagenumber = 0
        report_pages = Page.objects.filter(report=self.report_id).order_by('page_number')
        for report_page in report_pages:
            page_objects = PageObject.objects.filter(page=report_page.id)
            self.write_page_objects(page_objects, pagenumber)
            pagenumber += 1

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=ReportIII.pdf'

        outputStream = response
        self.output_pdf.write(response)
        outputStream.close()

        return response

# --------------------------------------------------develop-------------------------------------------------------------
    def generate_diagnostic_reports_develop(self, user_id, diagnostic_id):
        self.user_diagnostic = diagnostic_id
        self.user_id = user_id

        pagenumber = 0
        report_pages = Page.objects.filter(report=self.report_id).order_by('page_number')
        report_pages = [Page.objects.get(page_number=3)]
        for report_page in report_pages:
            page_objects = PageObject.objects.filter(page=report_page.id)
            self.write_page_objects(page_objects, pagenumber)
            pagenumber += 1

        outputStream = open(settings.MEDIA_ROOT + r"\report3.pdf", "wb")
        self.output_pdf.write(outputStream)
        outputStream.close()
        return

#------------------------------------------------------main-------------------------------------------------------------
#if not settings.ISSERVER:
   # DiagnosticReports().generate_diagnostic_reports_develop(50, 30)