import csv
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
import openpyxl
from .forms import UploadFileForm
import io
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

def handle_uploaded_file(file):
    data = []
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.reader(decoded_file)
    headers = next(reader)  # Extract headers
    for row in reader:
        data.append(row)
    return headers, data

def segment_data_by_trade_type(headers, data):
    trade_type_index = headers.index('trade_type')  # Find the index of the trade_type column
    price_index = headers.index('price') if 'price' in headers else None
    buy_segments = []
    sell_segments = []
    for row in data:
        if row[trade_type_index].strip().lower() == 'buy':
            buy_segments.append(row)
        elif row[trade_type_index].strip().lower() == 'sell':
            sell_segments.append(row)
    return buy_segments, sell_segments, price_index

def calculate_total_price(segments, price_index):
    if price_index is None:
        return None
    total = 0
    for row in segments:
        total += float(row[price_index])
    return total

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                headers, data = handle_uploaded_file(request.FILES['file'])
                buy_segments, sell_segments, price_index = segment_data_by_trade_type(headers, data)
                
                

                request.session['headers'] = headers
                request.session['buy_segments'] = buy_segments
                request.session['sell_segments'] = sell_segments
                request.session['price_index'] = price_index
                request.session['trade_type_index'] = headers.index('trade_type')
                request.session['symbol_index'] = headers.index('symbol')
                request.session['trade_date_index'] = headers.index('trade_date')  
                request.session['quantity_index'] = headers.index('quantity') 

                buy_total = calculate_total_price(buy_segments, price_index)
                sell_total = calculate_total_price(sell_segments, price_index)

                return render(request, 'result.html', {
                    'headers': headers,
                    'buy_segments': buy_segments,
                    'sell_segments': sell_segments,
                    'buy_total': buy_total,
                    'sell_total': sell_total,
                    'price_index': price_index
                })
            except ValueError as e:
                error_message = str(e)
                return render(request, 'upload.html', {'form': form, 'error_message': error_message})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def download_buy_pdf(request):
    if 'buy_segments' not in request.session:
        return HttpResponse("No buy segments data available.", status=400)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=portrait(A4))
    elements = []

    headers = ['Trade Type', 'Symbol', 'Price', 'Trade Date', 'Quantity']
    data = [headers]

    buy_segments = request.session['buy_segments']
    price_index = request.session['price_index']
    total_price = 0

    for row in buy_segments:
        filtered_row = [row[request.session['trade_type_index']], row[request.session['symbol_index']], row[price_index],
                        row[request.session['trade_date_index']], row[request.session['quantity_index']]]
        data.append(filtered_row)
        total_price += float(row[price_index])

    # Append total price
    data.append(['Total', '', total_price, '', ''])

    # Create table with style
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='buy_trades.pdf')

def download_buy_excel(request):
    if 'buy_segments' not in request.session:
        return HttpResponse("No buy segments data available.", status=400)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Buy Trades'

    for row in request.session['buy_segments']:
        sheet.append(row)

    response = HttpResponse(content=io.BytesIO(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=buy_trades.xlsx'
    workbook.save(response)

    return response

def download_sell_pdf(request):
    if 'sell_segments' not in request.session:
        return HttpResponse("No sell segments data available.", status=400)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=portrait(A4))
    elements = []

    headers = ['Trade Type', 'Symbol', 'Price', 'Trade Date', 'Quantity']
    data = [headers]

    sell_segments = request.session['sell_segments']
    price_index = request.session['price_index']
    total_price = 0

    for row in sell_segments:
        filtered_row = [row[request.session['trade_type_index']], row[request.session['symbol_index']], row[price_index],
                        row[request.session['trade_date_index']], row[request.session['quantity_index']]]
        data.append(filtered_row)
        total_price += float(row[price_index])

    # Append total price
    data.append(['Total', '', total_price, '', ''])

    # Create table with style
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='sell_trades.pdf')


def download_sell_excel(request):
    if 'sell_segments' not in request.session:
        return HttpResponse("No sell segments data available.", status=400)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Sell Trades'

    for row in request.session['sell_segments']:
        sheet.append(row)

    response = HttpResponse(content=io.BytesIO(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sell_trades.xlsx'
    workbook.save(response)

    return response
