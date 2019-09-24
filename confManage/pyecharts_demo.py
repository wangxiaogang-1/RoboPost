# -*- coding: utf-8 -*-
from pyecharts.charts import Radar
from pyecharts import options as opts


def radar_demo():
    # radar_data = [[2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]]#降水量
    radar_data = [[20, 49, 70, 232, 256, 767, 1356, 1622, 326, 200, 64, 33]]#降水量
    schema = [
        opts.RadarIndicatorItem(name="Jan", max_=50),
        opts.RadarIndicatorItem(name="Feb", max_=50),
        opts.RadarIndicatorItem(name="Mar", max_=100),
        opts.RadarIndicatorItem(name="Apr", max_=250),
        opts.RadarIndicatorItem(name="May", max_=300),
        opts.RadarIndicatorItem(name="Jun", max_=800),
        opts.RadarIndicatorItem(name="Jul", max_=1400),
        opts.RadarIndicatorItem(name="Aug", max_=1700),
        opts.RadarIndicatorItem(name="Sep", max_=350),
        opts.RadarIndicatorItem(name="Oct", max_=200),
        opts.RadarIndicatorItem(name="Nov", max_=100),
        opts.RadarIndicatorItem(name="Dec", max_=50)
    ]
    Radar().add_schema(schema).add("data1", radar_data).set_global_opts(
        title_opts=opts.TitleOpts(title="一年降水量统计")
    ).render("/aa.html")


if __name__ == '__main__':
    radar_demo()