#!/usr/bin/python2.4
# -*- encoding: utf-8 -*-
#    GLADE_VCP
#    Copyright 2010 Chris Morley
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import sys
import gtk
import hal
import gtk.glade
import gobject
import getopt
import xml.etree.ElementTree
import xml.etree.ElementPath

sys.path.append('/usr/lib/glade3/modules')

from hal_pythonplugin import *

class GladePanel():
    global GTKBUILDER,LIBGLADE
    GTKBUILDER = 1
    LIBGLADE = 0
    def on_window_destroy(self, widget, data=None):
        self.hal.exit()
        gobject.source_remove(self.timer)
        gtk.main_quit()

    def __init__(self,halcomp,xmlname,builder,buildertype):
        
        self.buildertype = buildertype
        self.builder = builder
        self.hal = halcomp
        doc = xml.etree.ElementTree.parse(xmlname)
        self.updatelist= {}
        if self.buildertype == LIBGLADE:
            temp = "widget"
        else:
            temp = "object"
        for parent in doc.getiterator(temp):
            #print parent.attrib
            j = parent.attrib
            k = j.get("class")
            idname = j.get("id")
            if k =="HAL_CheckButton" or k=="HAL_ToggleButton" or k =="HAL_RadioButton":
                    print" found a HAL chekcbutton! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self[idname].set_active(False)
                    self.hal.newpin(idname, hal.HAL_BIT, hal.HAL_OUT)
                    self[idname].connect("toggled", self.chkbtn_callback, idname)
                    self[idname].emit("toggled")
            if k =="HAL_Button" :
                    print" found a HAL button! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self.hal.newpin(idname, hal.HAL_BIT, hal.HAL_OUT)
                    self[idname].connect("pressed", self.button_callback, idname,True)
                    self[idname].connect("released", self.button_callback, idname,False)
                    self[idname].emit("released")
            if k =="HAL_HScale" or k == "HAL_VScale"or k == "HAL_SpinButton":
                    print" found a HAL scale bar! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self.hal.newpin(idname, hal.HAL_FLOAT, hal.HAL_OUT)
                    self[idname].connect("value-changed", self.scale_callback, idname)
                    self[idname].emit("value-changed")        
            if k =="HAL_ProgressBar" :
                    print" found a HAL progess bar ! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self.hal.newpin(idname, hal.HAL_FLOAT, hal.HAL_IN)
                    self.hal.newpin(idname+".scale", hal.HAL_FLOAT, hal.HAL_IN)
                    self.updatelist[idname] = k
            if k =="HAL_LED" :
                    print" found a HAL LED ! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self.hal.newpin(idname, hal.HAL_BIT, hal.HAL_IN)
                    for child in parent:
                        temp = child.attrib.get("name")
                        data = child.text
                        #print  temp,data
                        if temp =="off_color":
                            self[idname].set_color("off",None,data)
                        if temp =="on_color":
                            self[idname].set_color("on",None,data)
                        if temp =="pick_color_on" or temp == "pick_color_off":
                            r = int("0x"+data[1:5],16)/65536.0
                            g = int("0x"+data[5:9],16)/65536.0
                            b = int("0x"+data[9:13],16)/65536.0 
                            self[idname].set_color(temp[11:],(r,g,b),None)
                        if temp =="led_size":
                            self[idname].set_dia(int(data))
                        if temp =="led_shape":
                            self[idname].set_shape(int(data))  
                        if temp =="led_blink":
                            self[idname].set_blink_active(bool(data))
                        if temp =="led_blink_rate":
                            self[idname].set_blink_rate(int(data))
                    self[idname].set_active(False)
                    self.updatelist[idname] = k
            if k =="HAL_HBox" :
                    print" found a HAL hbox ! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self.hal.newpin(idname, hal.HAL_BIT, hal.HAL_IN)
                    self.updatelist[idname] = k
            if k =="HAL_Table" :
                    print" found a HAL table ! ",idname
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self[idname].connect("property-notify-event", self.table_callback, idname)
                    self.hal.newpin(idname, hal.HAL_BIT, hal.HAL_IN)
                    self.updatelist[idname] = k
            if k =="HAL_Label" :
                    print" found a HAL label ! ",idname
                    pin_type = hal.HAL_S32
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    for child in parent:
                        temp = child.attrib.get("name")
                        data = child.text
                        #print  temp,data
                        if temp =="label_pin_type":
                            if data == "1":
                                pin_type = hal.HAL_FLOAT
                            elif data == "2":
                                pin_type = hal.HAL_U32
                    self.hal.newpin(idname, pin_type, hal.HAL_IN)
                    self.updatelist[idname] = k
            if k =="HAL_ComboBox" :
                    print" found a HAL combo boxr ! ",idname
                    for child in parent:
                        temp = child.attrib.get("name")
                        data = child.text
                        #print  temp,data
                    self[idname] = self.read_widget(idname,builder,self.buildertype)
                    self.hal.newpin(idname, hal.HAL_FLOAT, hal.HAL_OUT)
                    self[idname].connect("changed", self.combo_callback, idname)

        self.timer = gobject.timeout_add(100, self.update)                  
        

    def update(self):
        for obj in self.updatelist:
            hal_type = self.updatelist[obj]
            if hal_type == "HAL_LED":
                self[obj].set_active(self.hal[obj])
            if hal_type == "HAL_HBox":
                self[obj].set_sensitive(self.hal[obj])
            if hal_type == "HAL_Table":
                self[obj].set_sensitive(self.hal[obj])
            if hal_type == "HAL_Label":
                self[obj].set_text("%s"% str ( self.hal[obj] ) )
            if hal_type == "HAL_ProgressBar":
                scale = self.hal[obj+".scale"]
                setting = self.hal[obj]
                if scale <= 0 : scale = 1
                if setting < 0 : setting = 0
                if (setting/scale) >1:
                    setting = 1
                    scale = 1
                self[obj].set_fraction(setting/scale)
        #add suport for pulsing 
        #self["hal_progressbar2"].pulse()
        return True # keep running this event

    def chkbtn_callback(self,widget,component):
        #print widget,component
        if self[component].get_active():
            self.hal[component] = True
        else:
            self.hal[component] = False
    def button_callback(self,widget,component,data):
        #print widget,component
            self.hal[component] = data
    def table_callback(self,widget,component,data):
        print widget,component
        print data
    def scale_callback(self,widget,component):
        #print widget,component
            data=self[component].get_value()
            self.hal[component] = data
    def combo_callback(self,widget,component):
        #print widget,component
        self.hal[component] = self[component].get_active()

    def read_widget(self,widgetname,builder,builder_type=LIBGLADE):
        if builder_type == LIBGLADE:
            return builder.get_widget(widgetname)
        else:
            return builder.get_object(widgetname)

    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, item, value):
        return setattr(self, item, value)
    
if __name__ == "__main__":
    print "Gladevcp_make_pins cannot be run on its own"
    print "It must be called by gladevcp or a python program"
    print "that loads and displays the glade panel and creates a HAL component"