from django.conf import settings

from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, String, Rect, Group, Circle
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('HelveticaNeueC', settings.BASE_DIR + r'/report/HelveticaNeue.ttf'))
st_font = 'HelveticaNeueC'


class DiagnosticChartDrawing(Drawing):

    def __init__(self, width=1000, height=400, *args, **kwargs):
        Drawing.__init__(self, width, height, *args, **kwargs)
        # background color
        self.background = Rect(0, 0, self.width, self.height, strokeWidth=0, fillColor=colors.lightgrey)
        # end here
        self.add(Circle(500, 200, 180), name='circle_perfect')
        self.add(Circle(500, 200, 145), name='circle_good')
        self.add(Circle(500, 200, 115), name='circle_medium')
        self.add(Circle(500, 200, 85), name='circle_bad')
        self.add(Circle(500, 200, 50), name='circle_awful')
        self.add(Circle(500, 200, 20), name='circle_center')
        self.add(SpiderChart(), name='background_chart')
        self.add(SpiderChart(), name='chart')


        # QR code
        qrw = QrCodeWidget('Well met')

        # QR size
        qrw.barHeight = 150
        qrw.barWidth = 150

        # QR position
        qrw.y = 100
        qrw.x = 10

        self.add(qrw)
        # end here

        # barcode
        barcode_group = Group()
        barcode = createBarcodeDrawing('EAN13', value='1234567890', width=200, height=100)

        barcode_group.add(barcode)
        barcode_group.shift(10, 10)  # barcode position
        self.add(barcode_group)
        # end here

        self.add(String(470, 386, 'Аналіз крові'), name='text0')
        self.add(String(605, 352, 'Антропометрія'), name='text1')
        self.add(String(670, 275, 'Постава'), name='text2')
        self.add(String(685, 170, 'Композиція тіла'), name='text3')
        self.add(String(645, 75, 'Електрокардіограмма'), name='text4')
        self.add(String(550, 10, 'Варіаційна пульсометрія'), name='text5')
        self.add(String(350, 10, 'Система дихання'), name='text6')
        self.add(String(220, 75, 'Кистьова динамометрія'), name='text7')
        self.add(String(225, 170, 'Основний обмін'), name='text8')
        self.add(String(160, 275, 'Карідореспіраторний профіль'), name='text9')
        self.add(String(330, 350, 'Психотест'), name='text10')

        # info
        self.add(String(840, 366, 'Чудово'), name='info_perfect')
        self.circle_perfect.fillColor = colors.Color(0, 0, 255, alpha=0.3)
        self.circle_perfect.strokeColor = colors.transparent
        self.info_perfect.fontName = 'HelveticaNeueC'
        self.info_perfect.fontSize = 12
        self.add(Rect(800, 356, 30, 30), name='rect_perfect')
        self.rect_perfect.fillColor = colors.Color(0, 0, 255, alpha=0.3)
        self.rect_perfect.strokeColor = colors.transparent

        self.add(String(840, 326, 'Добре'), name='info_good')
        self.circle_good.fillColor = colors.Color(0, 255, 0, alpha=0.5)
        self.circle_good.strokeColor = colors.transparent
        self.info_good.fontName = 'HelveticaNeueC'
        self.info_good.fontSize = 12
        self.add(Rect(800, 316, 30, 30), name='rect_good')
        self.rect_good.fillColor = colors.Color(0, 255, 0, alpha=0.5)
        self.rect_good.strokeColor = colors.transparent

        self.add(String(840, 286, 'Задовільно'), name='info_medium')
        self.circle_medium.fillColor = colors.yellow
        self.circle_medium.strokeColor = colors.transparent
        self.info_medium.fontName = 'HelveticaNeueC'
        self.info_medium.fontSize = 12
        self.add(Rect(800, 276, 30, 30), name='rect_medium')
        self.rect_medium.fillColor = colors.yellow
        self.rect_medium.strokeColor = colors.transparent

        self.add(String(840, 246, 'Погано'), name='info_bad')
        self.circle_bad.fillColor = colors.orange
        self.circle_bad.strokeColor = colors.transparent
        self.info_bad.fontName = 'HelveticaNeueC'
        self.info_bad.fontSize = 12
        self.add(Rect(800, 236, 30, 30), name='rect_bad')
        self.rect_bad.fillColor = colors.orange
        self.rect_bad.strokeColor = colors.transparent

        self.add(String(840, 206, 'Дуже погано'), name='info_awful')
        self.circle_awful.fillColor = colors.red
        self.circle_awful.strokeColor = colors.transparent
        self.info_awful.fontName = 'HelveticaNeueC'
        self.info_awful.fontSize = 12
        self.add(Rect(800, 196, 30, 30), name='rect_awful')
        self.rect_awful.fillColor = colors.red
        self.rect_awful.strokeColor = colors.transparent

        # end here

        self.chart.x = 20
        self.chart.y = 40
        self.chart.width = self.width - 40
        self.chart.height = self.height - 80

        self.background_chart.x = 10
        self.background_chart.y = 20
        self.background_chart.width = self.width - 20
        self.background_chart.height = self.height - 40

        # ruin has com to my code TODO rework this garbage
        self.text0.fontName = 'HelveticaNeueC'
        self.text0.fontSize = 12
        self.text1.fontName = 'HelveticaNeueC'
        self.text1.fontSize = 12
        self.text2.fontName = 'HelveticaNeueC'
        self.text2.fontSize = 12
        self.text3.fontName = 'HelveticaNeueC'
        self.text3.fontSize = 12
        self.text4.fontName = 'HelveticaNeueC'
        self.text4.fontSize = 12
        self.text5.fontName = 'HelveticaNeueC'
        self.text5.fontSize = 12
        self.text6.fontName = 'HelveticaNeueC'
        self.text6.fontSize = 12
        self.text7.fontName = 'HelveticaNeueC'
        self.text7.fontSize = 12
        self.text8.fontName = 'HelveticaNeueC'
        self.text8.fontSize = 12
        self.text9.fontName = 'HelveticaNeueC'
        self.text9.fontSize = 12
        self.text10.fontName = 'HelveticaNeueC'
        self.text10.fontSize = 12
        # end here aaaaaaaaaaaaaaaaaa

        self.chart.labels = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        self.background_chart.labels = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

        self.chart.data = [[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],  # style
                           [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # style
                           [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # style
                           [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # style
                           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # style

                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # values
                           ]

        self.background_chart.data = [[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],  # style
                           [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # style
                           [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # style
                           [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # style
                           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # style

                           ]

        # style
        self.chart.strands.strokeColor = colors.transparent
        self.background_chart.strands.strokeColor = colors.transparent
        self.background_chart.spokes.strokeColor = colors.lightgrey
        # self.chart.strands[1].strokeWidth = 15
        # self.chart.strands[1].strokeColor = colors.lightgreen
        # self.chart.strands[2].strokeWidth = 15
        # self.chart.strands[2].strokeColor = colors.yellow
        # self.chart.strands[3].strokeWidth = 15
        # self.chart.strands[3].strokeColor = colors.orange
        # self.chart.strands[4].strokeWidth = 15
        # self.chart.strands[4].strokeColor = colors.red

        # self.background_chart.strands[0].fillColor = colors.Color(0, 0, 255, alpha=0.3)
        # self.background_chart.strands[1].fillColor = colors.Color(0, 255, 0, alpha=0.5)
        # self.background_chart.strands[2].fillColor = colors.yellow
        # self.background_chart.strands[3].fillColor = colors.orange
        # self.background_chart.strands[4].fillColor = colors.red

        # self.chart.strands[0].strokeColor = colors.blue
        # self.chart.strands[0].strokeDashArray = (4, 4)
        # self.chart.strands[0].symbol = makeMarker("Circle")
        # self.chart.strands[0].strokeWidth = 0.5
        # self.chart.strands[0].symbol.fillColor = colors.black

        #end here

        self.chart.strandLabels.format = 'values'

        # main graph style
        self.chart.strands[5].strokeColor = colors.darkblue
        self.chart.spokes.strokeColor = colors.transparent

        self.chart.strands[5].symbol = makeMarker('FilledCircle', size=11)
        # self.chart.strandLabels.dR = -20
        self.chart.strands[5].symbol.fillColor = colors.white
        self.chart.strands[5].strokeWidth = 2

        # end here

    def set_graph_data(self, chart_data):
        self.chart.data[5] = chart_data

        for i in range(len(chart_data)):
            self.chart.strandLabels[5, i]._text = str(chart_data[i])

        self.chart.strands.symbolSize = 20
