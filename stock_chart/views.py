import pandas as pd
import plotly.graph_objs as go
from django.shortcuts import render
from django.conf import settings
import os


def stock_chart(request):
    user_input = request.POST.get('stock_symbol', '').strip()

    if user_input:
        excel_file = os.path.join(settings.BASE_DIR, 'C:\\ck_website\\stock_chart_project\\stock_chart_project\\data-Fintech2023.xlsx')
        user_input = user_input.split(":")[-1]  # Loại bỏ "VT:" nếu có

        # Đọc dữ liệu từ sheet "Price"
        price_data = pd.read_excel(excel_file, sheet_name='Price', header=0)
        price_data.columns = price_data.iloc[0]
        price_data = price_data[1:].reset_index(drop=True)
        price_data = price_data.set_index(price_data.columns[0])

        # Đảm bảo rằng tên cột không chứa dấu cách hoặc ký tự đặc biệt
        price_data.columns = price_data.columns.str.replace('[^\w\s]', '')

        # Tìm các cột trong sheet Price có mã cổ phiếu tương ứng
        matching_columns = [col for col in price_data.columns if user_input in col]

        if matching_columns:
            selected_data = price_data[matching_columns[0]].dropna()

            # Clean and convert data to numeric type
            selected_data = pd.to_numeric(selected_data, errors='coerce')
            sma_period = 100
            sma_values = selected_data.rolling(window=sma_period).mean()
            ema_period = 50
            ema_values = selected_data.ewm(span=ema_period).mean()
            rolling_std = selected_data.rolling(window=sma_period).std()
            upper_band = sma_values + (2 * rolling_std)
            lower_band = sma_values - (2 * rolling_std)
            short_period = 12
            long_period = 26
            signal_period = 9
            exp_short = selected_data.ewm(span=short_period, adjust=False).mean()
            exp_long = selected_data.ewm(span=long_period, adjust=False).mean()
            macd = exp_short - exp_long
            signal_line = macd.ewm(span=signal_period, adjust=False).mean()
            rsi_period = 14
            delta = selected_data.diff(1)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=rsi_period).mean()
            avg_loss = loss.rolling(window=rsi_period).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            # Calculate Stochastic Oscillator (Simplified example with a fixed period)
            stochastic_period = 14  # Adjust the period as needed
            stoch_k = 100 * (selected_data - selected_data.rolling(window=stochastic_period).min()) / (
                    selected_data.rolling(window=stochastic_period).max() - selected_data.rolling(
                window=stochastic_period).min())
            stoch_d = stoch_k.rolling(window=3).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=selected_data.index, y=selected_data, mode='lines',
                                     name=f"{user_input} Giá đóng cửa"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=sma_values, mode='lines',
                                     name=f"{user_input} SMA {sma_period} ngày"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=ema_values, mode='lines',
                                     name=f"{user_input} EMA {ema_period} ngày"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=upper_band, mode='lines', name="Bollinger Bands (Upper)"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=lower_band, mode='lines', name="Bollinger Bands (Lower)"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=macd, mode='lines', name="MACD"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=signal_line, mode='lines', name="Signal Line"))
            fig.add_trace(go.Scatter(x=selected_data.index, y=rsi, mode='lines', name="RSI"))
            fig.add_trace(go.Scatter(x=stoch_k.index, y=stoch_k, mode='lines', name='Stochastic K'))
            fig.add_trace(go.Scatter(x=stoch_d.index, y=stoch_d, mode='lines', name='Stochastic D'))

            # Thêm các chỉ số khác vào biểu đồ ở đây

            fig.update_xaxes(rangeslider_visible=True)
            fig.update_yaxes(rangemode="tozero")
            fig.update_layout(title=f"<span style='font-weight: bold; display: block; text-align: center;'>Biểu đồ kỹ thuật cho {user_input}</span>", xaxis_title='Thời gian',
                              yaxis_title='Giá và chỉ số')
            plot_div = fig.to_html(full_html=False)

            # Đọc thông tin mã cổ phiếu từ sheet "Symbol"
            symbol_data = pd.read_excel(excel_file, sheet_name='Symbol', header=0)

            # Lọc thông tin mã cổ phiếu dựa trên mã nhập từ người dùng
            symbol_match = symbol_data[symbol_data['Symbol'].str.replace('VT:', '', regex=True) == user_input]

            if not symbol_match.empty:
                company_info = symbol_match.iloc[0]  # Chọn dòng đầu tiên của kết quả
                company_name = company_info['Full Name']
                ric = company_info['RIC']
                start_date = company_info['Start Date']
                exchange = company_info['Exchange']
                sector = company_info['Sector']

                stock_info = {
                    'company_name': company_name,
                    'ric': ric,
                    'start_date': start_date,
                    'exchange': exchange,
                    'sector': sector
                }

                context = {
                    'symbol': user_input,
                    'plot_div': plot_div,
                    'stock_info': stock_info
                }
            else:
                context = {
                    'error_message': f"Không tìm thấy dữ liệu cho mã cổ phiếu: {user_input}"
                }
        else:
            context = {
                'error_message': f"Không tìm thấy dữ liệu cho mã cổ phiếu: {user_input}"
            }
    else:
        context = {
            'error_message': "Vui lòng nhập mã cổ phiếu"
        }

    return render(request, 'stock_chart.html', context)
