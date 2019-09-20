# from PyPDF2 import PdfFileWriter, PdfFileReader
#
# q = open(r'C:\Users\Евгений\Desktop\REPORT3(оновлений)v1.pdf', 'rb')
# reeder = PdfFileReader(q)
# q.close()
#
# page = 3
#
# writer = PdfFileWriter()
# writer.addPage(reeder.getPage(page))
# q = open(r'C:\Users\Евгений\Desktop\REPORT3(оновлений)v1p{}.pdf'.format(page), 'wb')
# writer.write(q)
# q.close()

a = 1

def c():
    print(a + 1)

c()