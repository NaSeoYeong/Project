import pandas as pd
import matplotlib.pyplot as plt
import time
import threading

from shiny import ui, render, App, reactive


# ui 구현 -----------------------------------------------------------
app_ui = ui.page_fluid(
    ui.include_css('style.css'),

    ui.div(
        {"style": "padding:30px;"},
        ui.p("현재 날씨 현황", {"style": "font-size: 35px; color: white; font-weight:bolder"}),
        ui.p(ui.output_ui('get_time'))
    ),
    ui.div(
        ui.layout_column_wrap(
            ui.value_box('기온', ui.output_text('get_temp'), class_='card border-secondary mb-3'),
            ui.value_box('습도', ui.output_text('get_humi'), class_='card border-success mb-3'),
            ui.value_box('풍속', ui.output_text('get_wind'), class_='card border-light mb-3')
        )
    ),
    ui.div(
        {"style": "background-color: rgba(0,0,0,0);"},
        # {"style": "border-radius: 10px; background-color: #f0f0f0"},     
        ui.output_plot('make_plot')
    )
)


# 스레드 구현 ----------------------------------------------------------
_df = pd.read_csv('./data.csv')
_df['시간'] = pd.to_datetime(_df['시간'])
_now_row = 0

_temp = [0] * 24
_humi = [0] * 24
_wind = [0] * 24

_time = ''


# 서버 구현 ------------------------------------------------------------------
def server(input, output, session):

    @reactive.poll
    def thread_function():
        global _df, _now_row, _temp, _humi, _wind, _time

        data = _df.iloc[_now_row,:]

        _time = str(data['시간'])

        if len(_temp) == 24:
            _temp.pop(0)
            _humi.pop(0)
            _wind.pop(0)
        
        _temp.append(data['기온'])
        _humi.append(data['습도'])
        _wind.append(data['풍속'])

        _now_row += 1

        time.sleep(3)

        
    @output
    @render.text
    def get_temp():
        global _temp
        reactive.invalidate_later(3)
        return _temp[-1]
    
    @output
    @render.text
    def get_humi():
        global _humi
        reactive.invalidate_later(3)
        return _humi[-1]
    
    @output
    @render.text
    def get_wind():
        global _wind
        reactive.invalidate_later(3)
        return _wind[-1]
    
    @output
    @render.ui
    def get_time():
        global _time
        reactive.invalidate_later(3)
        return ui.tags.p(f'측정시간: {_time}', {'class':"text-warning"})

    @output
    @render.plot
    def make_plot():

        global _temp, _humi, _wind
        reactive.invalidate_later(3)

        fig, ax = plt.subplots()
        fig.patch.set_alpha(0.0)

        ax.plot(_temp, label='temp', color='fuchsia')
        ax.plot(_humi, label='humi', color='lime')
        ax.plot(_wind, label='wind', color='cyan')

        ax.set_facecolor((0, 0, 0, 0))

        ax.legend()
        
        return fig
        
        
app = App(app_ui, server)
