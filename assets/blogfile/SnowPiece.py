"""
SnowPiece.py

examples of proper usage of logging module

__author__ = "Vega Bai"
__copyright__ = "Copyright 2015, Vega Bai"
__version__ = "1.0.1"
__maintainer__ = "Vega Bai"
__email__ = "vegabaixuan@gmail.com"
__status__ = "Practise"

"""

import pymel.core as pm

def select_obj(selType):
    ### global varibles
    global snow_obj
    global from_point
    global from_point_index
    global to_point
    global to_point_index
    sel_obj = pm.selected()
    
    ### judge if there is object selected
    if not sel_obj:
        pm.PopupError("No object selected!")
        return
    
    ### select object
    if selType == 0:
        snow_obj = sel_obj
        print 'obj OK'
        print snow_obj
        return snow_obj

    ### select destination point
    elif selType == 2:
        to_point = sel_obj[0]
        to_point_index = to_point.index()
        print to_point_index
        return to_point_index

    
def on_click_run(slider_scale, slider_angle, slider_level, snow_win):
    ### get values from sliders
    snow_scale = slider_scale.getValue()
    snow_angle = slider_angle.getValue()
    snow_level = slider_level.getValue()       

    ### list for 1/6 snow piece
    snow_list = []
    snow_list.append(snow_obj)
    
    ### list for 6 parts of the snow piece
    snow_joint_list = []
    
    ### rename the origin object
    pm.rename(snow_obj, 's0')

    ### draw 1/6 snow piece
    for i in range(1, snow_level):
        tmp = pm.duplicate(snow_list[i-1])
        snow_list.append(tmp[0])
        pm.rotate(snow_list[i], 0, snow_angle, 0, r = True)
        pm.scale(snow_list[i], snow_scale, 1, snow_scale, r = True)
        pos = pm.xform('%s.vtx[%d]'%(snow_list[i], to_point_index), q = 1, t = 1, ws = 1)
        pm.xform(snow_list[i], t = (pos[0], 0, pos[2]), ws = 1)

    ### unite the 1/6 snow piece
    tmpunit = snow_list[0]
    for i in range(1, snow_level):
        print tmpunit, i
        tmpunit = pm.polyUnite(tmpunit, snow_list[i])
        
    ### draw all 6 parts
    snow_joint_list.append(tmpunit[0])
    for i in range(1, 6):
        tmp = pm.duplicate(tmpunit[0])
        snow_joint_list.append(tmp)
        pm.rotate(tmp, 0, 60*i, 0, r = True)     
        
    ### unite the whole snow piece
    snow_final = snow_joint_list[0]
    for i in range(1,6):
        snow_final = pm.polyUnite(snow_final, snow_joint_list[i])
    
    ### delete the menu window
    snow_win.delete()
    
    return

def ui():
    win_title = 'Draw A Snowpiece'
    win_name = 'snow_window'
    win_width = 300
    win_height = 160

    if pm.window(win_name, exists = True):
        pm.deleteUI(win_name)

    ### create the menu window
    snow_win = pm.window(win_name,
                         title = win_title,
                         widthHeight = (win_width, win_height),
                         sizeable = False
                         )
    col_layout1 = pm.columnLayout(adj = True)  
    row_layout1 = pm.rowLayout(nc = 2,
                               cw2 = ((win_width/2-10), (win_width/2+10)),
                               parent = col_layout1
                               ) 
    
    ### select object button
    button_sel_obj = pm.button(label = 'Select Object',
                               width = 100,
                               command = pm.Callback(select_obj, 0)
                               ) 
    ### select destination point button
    button_sel_end_point = pm.button(label = 'Select Destination Point',
                                     width = 130,
                                     command = pm.Callback(select_obj, 2)
                                     )
    
    ### slider for scale
    slider_scale = pm.floatSliderGrp(label = 'Scale',
                                     field = True,
                                     minValue = -2.0,
                                     maxValue = 2.0,
                                     fieldMinValue = -2.0,
                                     fieldMaxValue = 2.0,
                                     value = 0.5,
                                     cw3 = (40, 50, 200),
                                     adj = 3,
                                     parent = col_layout1
                                     )
    ### slider for angle
    slider_angle = pm.floatSliderGrp(label = 'Angle',
                                     field = True,
                                     minValue = -30,
                                     maxValue = 30,
                                     fieldMinValue = -30,
                                     fieldMaxValue = 30,
                                     value = 0,
                                     cw3 = (40, 50, 200),
                                     adj = 3,
                                     parent = col_layout1
                                     )
    ### slider for level
    slider_level = pm.intSliderGrp(label = 'Level',
                                     field = True,
                                     minValue = 0,
                                     maxValue = 10,
                                     fieldMinValue = 0,
                                     fieldMaxValue = 10,
                                     value = 4,
                                     cw3 = (40, 50, 200),
                                     adj = 3,
                                     parent = col_layout1
                                     ) 
    ### layout for run button and cancel button
    row_layout2 = pm.rowLayout(nc = 2,
                               cw2 = ((win_width/2), (win_width/2)),
                               co2 = (20, 20),
                               parent = col_layout1
                               )
    button_run = pm.button(label = 'Run',
                           width = 100
                           )
    button_run.setCommand(pm.Callback(on_click_run,
                                      slider_scale = slider_scale,
                                      slider_angle = slider_angle,
                                      slider_level = slider_level,
                                      snow_win = snow_win
                                      )
                          )
    
    button_cancel = pm.button(label = 'Cancel',
                              width = 100,
                              command = pm.Callback(snow_win.delete)
                              )
    snow_win.show()
    snow_win.setWidthHeight((win_width, win_height))
    
