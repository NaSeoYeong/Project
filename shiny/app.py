import pandas as pd
import matplotlib.pyplot as plt
import time
import threading

from shiny import ui, render, App, reactive


# ui 구현 -----------------------------------------------------------
app_ui = ui.page_fluid(
    ui.include_css('./shiny/style.css'),

    ui.div(
        {"style": "padding:30px;"},
        ui.p("현재 우리 아기는", {"style": "font-size: 35px; color: white; font-weight:bolder"}),
        ui.p(ui.output_ui('get_time'))
    ),
    ui.div(
        ui.layout_column_wrap(
            ui.value_box('온도', ui.output_text('get_temp'), class_='card border-secondary mb-3'),
            ui.value_box('습도', ui.output_text('get_humi'), class_='card border-success mb-3'),
            ui.value_box('가스', ui.output_text('get_voc'), class_='card border-light mb-3')
        )
    ),
    ui.div(
        {"style": "background-color: rgba(0,0,0,0);"},
        # {"style": "border-radius: 10px; background-color: #f0f0f0"},     
        ui.output_plot('make_plot')
    )
)


# 스레드 구현 ----------------------------------------------------------
_df = pd.read_csv('./shiny/data.csv')
_df['index'] = pd.to_datetime(_df['index'])
_now_row = 0

_temp = [0] * 1800
_humi = [0] * 1800
_voc = [0] * 1800

_time = ''


# 서버 구현 ------------------------------------------------------------------
def server(input, output, session):

    
    def thread_function():
        global _df, _now_row, _temp, _humi, _voc, _time

        data = _df.iloc[_now_row:_now_row+60,:]

        _time = str(data['index'].iloc[-1])

        if len(_temp) == 1800:
            _temp.pop(0)
            _humi.pop(0)
            _voc.pop(0)
        
        _temp.extend(data['temperature'])
        _humi.extend(data['humidity'])
        _voc.extend(data['voc'])

        _now_row += 60

        # time.sleep(0.01)
        
    reactive.poll(thread_function, 0.01)

        
    @output
    @render.text
    def get_temp():
        global _temp
        reactive.invalidate_later(0.01)
        return _temp[-1]
    
    @output
    @render.text
    def get_humi():
        global _humi
        reactive.invalidate_later(0.01)
        return _humi[-1]
    
    @output
    @render.text
    def get_voc():
        global _voc
        reactive.invalidate_later(0.01)
        return _voc[-1]
    
    @output
    @render.ui
    def get_time():
        global _time
        reactive.invalidate_later(0.01)
        return ui.tags.p(f'갱신 시간: {_time}', {'class':"text-warning"})

    @output
    @render.plot
    def make_plot():

        global _temp, _humi, _voc
        reactive.invalidate_later(0.01)

        fig, ax = plt.subplots()
        fig.patch.set_alpha(0.0)

        ax.plot(_temp, label='temp', color='fuchsia')
        ax.plot(_humi, label='humi', color='lime')
        ax.plot(_voc, label='voc', color='cyan')

        ax.set_facecolor((0, 0, 0, 0))

        ax.legend()
        
        return fig
        
        
app = App(app_ui, server)
