change_log = """
###############################################################################
rtCount.py
2021-04-16, version 0.9, first

###############################################################################
"""
import time, os, sys
import json
from tkinter import *
from tkinter import ttk


from rt_main import var, menus, lang, cwd, ARR_SCREEN, ARR_CONFIG, getSCREEN, getCRPT, dbconMaster, loadConfig, getScreenData, putSections, procScreen, getDataThread, updateVariables

oWin = None
eWin = None
ths = None
thd = None
thv = None

def exitProgram(event=None):
    global ths, thd, thv, oWin, eWin, root
    print ("Exit Program")
   
    for i in range(100):
        r = True
        s = ""
        if oWin:
            closeOption()
        if eWin:
            closeEdit()

        if ths:
            ths.stop()
            ths.Running = 0
            s += "ths: alive %s, ex %s " %(str(ths.is_alive()), str(ths.exFlag))
            r &= not (ths.is_alive())
            r &= ths.exFlag
        if thd:
            thd.stop()
            thd.Running = 0
            s += "  thd: alive %s, ex %s " %(str(thd.is_alive()), str(thd.exFlag))
            r &= not (thd.is_alive())
            r &= thd.exFlag
        # if thv:
        #     thv.stop()
        #     thv.Running = 0
        #     r &= thv.exFlag
        
        print (i, r, s)

        if r:
            break
        time.sleep(0.5)

    # root.overrideredirect(False)
    # root.attributes("-fullscreen", False)
    time.sleep(1)
    root.destroy()
    root.quit()
    print ("destroyed root")
    # raise SystemExit()
    # sys.exit()
    # print ("sys.exit()")


#########################################################################################################
############################################## Option Config ############################################
#########################################################################################################
def frame_option(e=None):
    global oWin, var, ARR_CONFIG
    # print(e)
    
    var['refresh_interval'] = StringVar()
    var['full_screen'] = IntVar()
    var['template'] = StringVar()
    var['message_str'] = StringVar()

    for key in ARR_CONFIG['mysql']:
        var[key] = StringVar()
        var[key].set(ARR_CONFIG['mysql'][key])

    if oWin: 
        oWin.lift()
    else :
        oWin = Toplevel(root)		
        oWin.title("Configuration")
        oWin.geometry("300x400+%d+%d" %(int(screen_width/2-150), int(screen_height/2-200)))
        oWin.protocol("WM_DELETE_WINDOW", closeOption)
        oWin.resizable(False, False)
        # oWin.overrideredirect(True)
        optionMenu(oWin)
    ths.delay =  ARR_CONFIG['refresh_interval']

def closeOption():
    global oWin
    oWin.destroy()
    oWin = None




def optionMenu(win):
    global ARR_CONFIG, var

    def saveConfig():
        global ARR_CONFIG, ARR_SCREEN, var, thd, ths, menus
        message ("")
        chMysql = False
        for key in ARR_CONFIG['mysql']:
            if str(ARR_CONFIG['mysql'][key]).strip() != str(var[key].get()).strip():
                print ("%s : %s" %(ARR_CONFIG['mysql'][key], var[key].get()))
                chMysql = True
                break
        if chMysql:
            try:
                dbconMaster(
                    host = str(var['host'].get().strip()),
                    user = str(var['user'].get().strip()), 
                    password = str(var['password'].get().strip()),
                    charset = str(var['charset'].get().strip()),
                    port = int(var['port'].get().strip())
                )
            except Exception as e:
                print ("MYSQL Error")
                print (e)
                message (lang.get("check_mysql_conf"))
                return False

            for key in ARR_CONFIG['mysql']:
                ARR_CONFIG['mysql'][key] = str(var[key].get()).strip()

        try:
            ARR_CONFIG['refresh_interval'] = int(var['refresh_interval'].get())
        except:
            message (lang.get("refresh_time_error"))
            return False

        if ARR_CONFIG['template'] != var['template'].get().strip():
            ARR_CONFIG['template'] = var['template'].get().strip()
            print ("template changed")
            for m in menus:
                print (m)
                menus[m].place_forget()

            getScreenData(True)
            putSections()
            print()
            # if ths:
            #     ths.stop()
            #     for i in range(50):
            #         print (ths.exFlag)
            #         if ths.exFlag:
            #             break
            #         time.sleep(0.2)
            #     ths = procScreen()
            #     ths.start()                

        fx = "yes" if var['full_screen'].get() else "no"
        if ARR_CONFIG['full_screen'] != fx:
            ARR_CONFIG['full_screen'] = fx
            if ARR_CONFIG['full_screen'] == "yes":
                # root.overrideredirect(True)
                root.attributes("-fullscreen", True)
                root.resizable (False, False)
            else :
                root.overrideredirect(False)
                root.attributes("-fullscreen", False)
                root.resizable (True, True)

        if thd and chMysql:
            thd.stop()
            for i in range(50):
                print (thd.exFlag)
                if thd.exFlag:
                    break
                time.sleep(0.2)

            # for sect in ARR_SCREEN:
            #     menus[sect['name']].place_forget()

            thd = getDataThread()
            thd.start()

        # print (ARR_CONFIG)
        json_str = json.dumps(ARR_CONFIG, ensure_ascii=False, indent=4, sort_keys=True)
        with open("%s\\rtScreen.json" %cwd, "w", encoding="utf-8") as f:
            f.write(json_str)
        message("saved")

    btnFrame = Frame(win)
    btnFrame.pack(side="bottom", pady=10)
    Button(btnFrame, text=lang['close_option'], command=closeOption, width=16).pack(side="left", padx=5)
    Button(btnFrame, text=lang['exit_program'], command=exitProgram, width=16).pack(side="right", padx=5)

    dbFrame = Frame(win)
    dbFrame.pack(side="top", pady=10)

    Label(dbFrame, text=lang['db_server']).grid(row=0, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['user']).grid(row=1, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['password']).grid(row=2, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['charset']).grid(row=3, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['port']).grid(row=4, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['db_name']).grid(row=5, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['refresh_interval']).grid(row=6, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['full_screen']).grid(row=7, column=0, sticky="w", pady=2, padx=4)
    Label(dbFrame, text=lang['template']).grid(row=8, column=0, sticky="w", pady=2, padx=4)

    Entry(dbFrame, textvariable=var['host']).grid(row=0, column=1, ipadx=3)
    Entry(dbFrame, textvariable=var['user']).grid(row=1, column=1, ipadx=3)
    Entry(dbFrame, textvariable=var['password']).grid(row=2, column=1, ipadx=3)
    Entry(dbFrame, textvariable=var['charset']).grid(row=3, column=1, ipadx=3)
    Entry(dbFrame, textvariable=var['port']).grid(row=4, column=1, ipadx=3)
    Entry(dbFrame, textvariable=var['db']).grid(row=5, column=1, ipadx=3)
    Entry(dbFrame, textvariable=var['refresh_interval']).grid(row=6, column=1, ipadx=3)
    cfs = Checkbutton(dbFrame, variable=var['full_screen'])
    cfs.grid(row=7, column=0, columnspan=2)
    Entry(dbFrame, textvariable=var['template']).grid(row=8, column=1, ipadx=3)
    Button(dbFrame, text=lang['save_changes'], command=saveConfig, width=16).grid(row=9, column=0, columnspan=2)

    var['refresh_interval'].set(ARR_CONFIG['refresh_interval'])
    var['template'].set(ARR_CONFIG['template'])
    if ARR_CONFIG['full_screen'] == 'yes':
        cfs.select()
    Message(win, textvariable = var['message_str'], width= 300,  bd=0, relief=SOLID, foreground='red').pack(side="top")

def message(strn):
    var['message_str'].set(strn)



#########################################################################################################
############################################## Screen Edit ##############################################
#########################################################################################################
def edit_screen(e):
    global eWin
    ths.delay =  1
    updateVariables(_editmode=True)
    print(e)
    # print(e.x, e.y)
    
    if eWin: 
        eWin.lift()
    else :
        eWin = Toplevel(root)		
        eWin.title("Edit Screen")
        eWin.geometry("260x600+%d+%d" %(int(screen_width/2-150), int(screen_height/2-200)))
        eWin.protocol("WM_DELETE_WINDOW", closeEdit)
        eWin.resizable(True, True)
        editScreen(eWin)
    

def closeEdit():
    global eWin
    eWin.destroy()
    eWin = None
    updateVariables(_editmode=False)
    updateVariables(_selLabel=False )
    ths.delay = ARR_CONFIG['refresh_interval']

def editScreen(win):
    global ARR_SCREEN
    btnFrame = Frame(win)
    btnFrame.pack(side="bottom", pady=10)
    Button(btnFrame, text=lang['close_option'], command=closeEdit, width=16).pack(side="left", padx=5)

    dbFrame = Frame(win)
    dbFrame.pack(side="top", pady=10)

    listLabels = list()
    listDevice = set()
    listFontFamily = ['simhei', 'arial', 'fangsong', 'simsun', 'gulim', 'batang', 'ds-digital','bauhaus 93', 'HP Simplified' ]
    listFontShape  = ['normal', 'bold', 'italic']
    listFontColor  = ['white', 'black', 'orange', 'blue', 'red', 'green', 'purple', 'grey', 'yellow', 'pink']

    ARR_SCREEN = getSCREEN()
    for x in ARR_SCREEN:
        listLabels.append(x['name'])

    arr = getCRPT()
    for dt in arr:
        for x in arr[dt]:
            listDevice.add(x)
    listDevice = list(listDevice)


    arr_lvar = ['display', 'font', 'fontsize', 'fontshape', 'color', 'bgcolor', 'width', 'height', 'posX', 'posY', 'padX', 'padY', 'device_info', 'rule','use', 'url']
    lvar = dict()
    elb = dict()
    ent = dict()

    for x in arr_lvar:
        lvar[x] = StringVar()
    
    def updateEntry(e):
        sel = selLabel.get()
        updateVariables(_selLabel = sel)

        for l in arr_lvar:
            if elb.get(l):
                elb[l].grid_forget()
            if ent.get(l):
                ent[l].grid_forget()
        
        btn_f_p.grid_forget()
        btn_f_m.grid_forget()

        for x in ARR_SCREEN:
            if x['name'] == sel:
                
                ent['posX'].grid(row=4, column=0)
                ent['posY'].grid(row=4, column=1, columnspan=2)
                elb['width'].grid(row=6, column=0, sticky="w", pady=2, padx=4)
                ent['width'].grid(row=6, column=1, sticky="w", ipadx=3)
                ent['height'].grid(row=6, column=2, sticky="w", ipadx=3)
                elb['padding'].grid(row=7, column=0, sticky="w", pady=2, padx=4)
                ent['padX'].grid(row=7, column=1, sticky="w", ipadx=3)
                ent['padY'].grid(row=7, column=2, sticky="w", ipadx=3)
                elb['use'].grid(row=10, column=0, sticky="w", pady=2, padx=4)
                ent['use'].grid(row=10, column=1, sticky="w")

                lvar['width'].set(x.get('size')[0])
                lvar['height'].set(x.get('size')[1])
                lvar['posX'].set(x.get('position')[0])
                lvar['posY'].set(x.get('position')[1])
                lvar['padX'].set(x.get('padding')[0])
                lvar['padY'].set(x.get('padding')[1])


                if x.get('flag') == 'y':
                    ent['use'].select()
                else :
                    ent['use'].deselect()

                if sel.startswith('picture') or sel.startswith('video'):
                    elb['url'].grid(row=1, column=0, sticky="w", pady=2, padx=4)
                    ent['url'].grid(row=1, column=1, columnspan=2, sticky="w")
                    lvar['url'].set(x.get('url'))

                else :
                    btn_f_p.grid(row=1, column=1)
                    btn_f_m.grid(row=1, column=2)
                    ent['fontsize'].grid(row=4, column=3)

                    elb['font'].grid(row=2, column=0, sticky="w", pady=2, padx=4)
                    ent['font'].grid(row=2, column=1, columnspan=2, sticky="w")
                    elb['fontshape'].grid(row=3, column=0, sticky="w", pady=2, padx=4)
                    ent['fontshape'].grid(row=3, column=1, columnspan=2, sticky="w")
                    elb['color'].grid(row=4, column=0, sticky="w", pady=2, padx=4)
                    ent['color'].grid(row=4, column=1, columnspan=2, sticky="w")
                    elb['bgcolor'].grid(row=5, column=0, sticky="w", pady=2, padx=4)
                    ent['bgcolor'].grid(row=5, column=1, columnspan=2, sticky="w")

                    for i, ft in enumerate(listFontFamily):
                        if x.get('font')[0] == ft:
                            ent['font'].current(i)
                    lvar['fontsize'].set(x.get('font')[1])

                    for i, ft in enumerate(listFontShape):
                        if x.get('font')[2] == ft:
                            ent['fontshape'].current(i)

                    for i, ft in enumerate(listFontColor):
                        if x.get('color')[0] == ft:
                            ent['color'].current(i)

                    for i, ft in enumerate(listFontColor):
                        if x.get('color')[1] == ft:
                            ent['bgcolor'].current(i)

                    if sel.startswith('number'):
                        elb['device_info'].grid(row=8, column=0, sticky="w", pady=2, padx=4)
                        ent['device_info'].grid(row=8, column=1, columnspan=2, sticky="w")
                        elb['rule'].grid(row=9, column=0, sticky="w", pady=2, padx=4)
                        ent['rule'].grid(row=9, column=1, columnspan=2, sticky="w", ipadx=3)
                        for i, ft in enumerate(listDevice):
                            if x.get('device_info') == ft:
                                ent['device_info'].current(i)

                        lvar['rule'].set(x.get('rule'))
                    else :
                        elb['display'].grid(row=1, column=0, sticky="w", pady=2, padx=4)
                        ent['display'].grid(row=1, column=1, columnspan=2, sticky="w", ipadx=3)
                        lvar['display'].set(x.get('text'))

    def saveScreen():
        global ARR_CONFIG
        arr = ARR_SCREEN
        sel = selLabel.get()
        for i, r in enumerate(arr):
            if r['name'] == sel:
                arr[i]['padding'] = [int(lvar['padX'].get()), int(lvar['padY'].get())]
                arr[i]['position'] = [int(lvar['posX'].get()), int(lvar['posY'].get())]
                arr[i]['size'] = [int(lvar['width'].get()), int(lvar['height'].get())]
                arr[i]['flag'] = 'y' if int(lvar['use'].get()) else 'n'

                if sel.startswith('picture') or sel.startswith('video'):
                    arr[i]['url'] = lvar['url'].get()

                else:
                    arr[i]['font'] = [ent['font'].get(), int(lvar['fontsize'].get()), ent['fontshape'].get()]
                    arr[i]['color'] = [ent['color'].get(), ent['bgcolor'].get()]
                    arr[i]['size'] = [int(lvar['width'].get()), int(lvar['height'].get())]
                    arr[i]['padding'] = [int(lvar['padX'].get()), int(lvar['padY'].get())]
                    arr[i]['position'] = [int(lvar['posX'].get()), int(lvar['posY'].get())]

                    if sel.startswith('number'):
                        arr[i]['text'] = ""
                        arr[i]['device_info'] = ent['device_info'].get()
                        arr[i]['rule'] = lvar['rule'].get()
                    else :
                        arr[i]['text'] = lvar['display'].get()
                    

        # print (arr)
        print (".")
        json_str = json.dumps(arr, ensure_ascii=False, indent=4, sort_keys=True)
        with open("%s\\%s" %(cwd, ARR_CONFIG['template']), "w", encoding="utf-8") as f:
            f.write(json_str)

    def posLeft():
        lvar['posX'].set(str(int(lvar['posX'].get())-1))
        saveScreen()
    def posRight():
        lvar['posX'].set(str(int(lvar['posX'].get())+1))
        saveScreen()
    def posUp():
        lvar['posY'].set(str(int(lvar['posY'].get())-1))
        saveScreen()
    def posDown():
        lvar['posY'].set(str(int(lvar['posY'].get())+1))
        saveScreen()
    def fontSizeU():
        lvar['fontsize'].set(str(int(lvar['fontsize'].get())+1))
        saveScreen()
    def fontSizeD():
        lvar['fontsize'].set(str(int(lvar['fontsize'].get())-1))
        saveScreen()

    Label(dbFrame, text=lang['name']).grid(row=0, column=0, sticky="w", pady=2, padx=4)
    selLabel = ttk.Combobox(dbFrame, width=20, values=listLabels)
    selLabel.bind("<<ComboboxSelected>>", updateEntry)
    selLabel.grid(row=0, column=1, columnspan=2, sticky="w")

    # Text
    elb['display'] = Label(dbFrame, text=lang['display'])
    ent['display'] = Entry(dbFrame, textvariable=lvar['display'], width=22)
    # Font
    elb['font'] = Label(dbFrame, text=lang['fontfamily'])
    ent['font'] =  ttk.Combobox(dbFrame, width=20, values=listFontFamily)
    #Font shape
    elb['fontshape'] = Label(dbFrame, text=lang['fontshape'])
    ent['fontshape'] = ttk.Combobox(dbFrame, width=20, values=listFontShape)
    # Color
    elb['color'] = Label(dbFrame, text=lang['color'])
    ent['color'] = ttk.Combobox(dbFrame, width=20, values=listFontColor)
    # Bg color
    elb['bgcolor'] = Label(dbFrame, text=lang['bgcolor'])
    ent['bgcolor'] = ttk.Combobox(dbFrame, width=20, values=listFontColor)
    # Width
    elb['width'] = Label(dbFrame, text=(lang['width'] + "/" + lang['height']))
    ent['width'] = Entry(dbFrame, textvariable=lvar['width'], width=10)
    ent['height']= Entry(dbFrame, textvariable=lvar['height'], width=10)
    # Padding
    elb['padding'] = Label(dbFrame, text=lang['padding'])
    ent['padX'] = Entry(dbFrame, textvariable=lvar['padX'], width=10)
    ent['padY'] = Entry(dbFrame, textvariable=lvar['padY'], width=10)
    # Device Info
    elb['device_info'] = Label(dbFrame, text=lang['deviceinfo'])
    ent['device_info'] = ttk.Combobox(dbFrame, width=20, values=listDevice)
    # Rule
    elb['rule'] = Label(dbFrame, text=lang['rule'])
    ent['rule'] = Entry(dbFrame, textvariable=lvar['rule'], width=22)
    # Use flag
    elb['use'] = Label(dbFrame, text=lang['use'])
    ent['use'] = Checkbutton(dbFrame, variable=lvar['use'])
    # Pic, Video url
    elb['url'] = Label(dbFrame, text=lang['url'])
    ent['url'] =  Entry(dbFrame, textvariable=lvar['url'], width=22)

    Button(dbFrame, text=lang['save_changes'], command=saveScreen, width=16).grid(row=11, column=0, columnspan=3)

    btFrame = Frame(win)
    btFrame.pack(side="top", pady=10)

    Button(btFrame, text="^", command=posUp,     width=4).grid(row=0, column=1, columnspan=2)
    Button(btFrame, text="<", command=posLeft,   width=4).grid(row=1, column=0)
    btn_f_p = Button(btFrame, text="+", command=fontSizeU, width=2)
    # btn_f_p.grid(row=1, column=1)
    btn_f_m = Button(btFrame, text="-", command=fontSizeD, width=2)
    # btn_f_m.grid(row=1, column=2)
    Button(btFrame, text=">", command=posRight,  width=4).grid(row=1, column=3)
    Button(btFrame, text="v", command=posDown,   width=4).grid(row=2, column=1, columnspan=2)

    Label(btFrame, text='X').grid(row=3, column=0)
    Label(btFrame, text='Y').grid(row=3, column=1, columnspan=2)
    Label(btFrame, text='S').grid(row=3, column=3)
    ent['posX'] = Entry(btFrame, textvariable=lvar['posX'], width=4)
    # ent['posX'].grid(row=4, column=0)
    ent['posY'] = Entry(btFrame, textvariable=lvar['posY'], width=4)
    # ent['posY'].grid(row=4, column=1, columnspan=2)
    ent['fontsize'] = Entry(btFrame, textvariable=lvar['fontsize'], width=4)
    # ent['fontsize'].grid(row=4, column=3)




if __name__ == '__main__':
    root =Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.geometry("%dx%d+0+0" %((screen_width), (screen_height)))

    root.bind('<Double-Button-1>', edit_screen)
    root.bind('<Button-3>', frame_option)
    root.configure(background="black")


    
    ths = procScreen()
    ths.start()

    thd = getDataThread()
    thd.start()
    
    # thv = showPicture()
    # thv.start()

    if ARR_CONFIG['full_screen'] == "yes":
        # root.overrideredirect(True)
        root.attributes("-fullscreen", True)
        root.resizable (False, False)
    else :
        root.resizable (True, True)


    root.mainloop()
raise SystemExit()
sys.exit()

